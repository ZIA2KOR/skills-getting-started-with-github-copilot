"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities database before each test"""
    global activities
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Join the school basketball team and compete in league games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu", "james@mergington.edu"]
        },
        "Swimming Club": {
            "description": "Learn swimming techniques and train for competitions",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["sarah@mergington.edu", "luke@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore various art mediums including painting, drawing, and sculpture",
            "schedule": "Mondays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["lily@mergington.edu", "grace@mergington.edu"]
        },
        "Drama Club": {
            "description": "Participate in theater productions and develop acting skills",
            "schedule": "Thursdays, 3:30 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking through competitive debates",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu", "noah@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in various science and engineering challenges",
            "schedule": "Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "william@mergington.edu"]
        }
    }
    
    # Reset activities to original state
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_get_activities_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
        
    def test_get_activities_participants(self, client):
        """Test that activities contain participant information"""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
        
    def test_signup_duplicate_participant(self, client):
        """Test signing up a student who is already registered"""
        email = "michael@mergington.edu"
        
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()
        
    def test_signup_nonexistent_activity(self, client):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        
    def test_signup_multiple_students(self, client):
        """Test signing up multiple students for the same activity"""
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/Chess Club/signup?email={email}"
            )
            assert response.status_code == 200
            
        # Verify all students were added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data["Chess Club"]["participants"]
        
        for email in emails:
            assert email in participants
            
    def test_signup_url_encoding(self, client):
        """Test that special characters in activity names are handled correctly"""
        response = client.post(
            "/activities/Programming%20Class/signup?email=coder@mergington.edu"
        )
        
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "coder@mergington.edu" in activities_data["Programming Class"]["participants"]


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_unregister_success(self, client):
        """Test successfully unregistering a participant"""
        email = "michael@mergington.edu"
        
        response = client.delete(
            f"/activities/Chess Club/participants/{email}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data["Chess Club"]["participants"]
        
    def test_unregister_nonexistent_participant(self, client):
        """Test unregistering a student who is not registered"""
        response = client.delete(
            "/activities/Chess Club/participants/notregistered@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()
        
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from an activity that doesn't exist"""
        response = client.delete(
            "/activities/Nonexistent Club/participants/student@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
        
    def test_unregister_and_resignup(self, client):
        """Test unregistering and then signing up again"""
        email = "michael@mergington.edu"
        activity = "Chess Club"
        
        # Unregister
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
        
        # Sign up again
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify re-addition
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
    def test_unregister_url_encoding(self, client):
        """Test that special characters in paths are handled correctly"""
        # Use a simple email to test URL encoding of activity name
        email = "testuser@mergington.edu"
        
        # Sign up for an activity with spaces in the name
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signup worked
        activities_response = client.get("/activities")
        assert email in activities_response.json()["Chess Club"]["participants"]
        
        # Now remove using URL encoded activity name
        response = client.delete(
            f"/activities/Chess%20Club/participants/{email}"
        )
        
        assert response.status_code == 200
        
        # Verify removal worked
        activities_response = client.get("/activities")
        assert email not in activities_response.json()["Chess Club"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_index(self, client):
        """Test that root endpoint redirects to static index page"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestIntegrationScenarios:
    """Integration tests for complete user workflows"""
    
    def test_full_signup_workflow(self, client):
        """Test a complete signup and unregister workflow"""
        email = "newstudent@mergington.edu"
        activity = "Programming Class"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify count increased
        response = client.get("/activities")
        new_count = len(response.json()[activity]["participants"])
        assert new_count == initial_count + 1
        
        # Unregister
        response = client.delete(f"/activities/{activity}/participants/{email}")
        assert response.status_code == 200
        
        # Verify count returned to original
        response = client.get("/activities")
        final_count = len(response.json()[activity]["participants"])
        assert final_count == initial_count
        
    def test_multiple_activities_signup(self, client):
        """Test signing up for multiple different activities"""
        email = "multisport@mergington.edu"
        activities_list = ["Chess Club", "Programming Class", "Gym Class"]
        
        for activity in activities_list:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
            
        # Verify participant is in all activities
        response = client.get("/activities")
        data = response.json()
        
        for activity in activities_list:
            assert email in data[activity]["participants"]
