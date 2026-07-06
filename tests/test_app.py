import pytest
from fastapi.testclient import TestClient
from app import app, activities

client = TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self):
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activity_has_required_fields(self):
        response = client.get("/activities")
        data = response.json()
        chess = data["Chess Club"]
        assert "description" in chess
        assert "schedule" in chess
        assert "max_participants" in chess
        assert "participants" in chess


class TestSignupForActivity:
    def test_signup_new_participant(self):
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]

    def test_signup_duplicate_participant(self):
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self):
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_participant_added_to_list(self):
        client.post("/activities/Basketball Team/signup?email=basketball@mergington.edu")
        response = client.get("/activities")
        data = response.json()
        assert "basketball@mergington.edu" in data["Basketball Team"]["participants"]


class TestUnregisterFromActivity:
    def test_unregister_existing_participant(self):
        response = client.delete(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_nonexistent_participant(self):
        response = client.delete(
            "/activities/Chess Club/signup?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self):
        response = client.delete(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404


class TestRootEndpoint:
    def test_root_redirects_to_index(self):
        response = client.get("/")
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
