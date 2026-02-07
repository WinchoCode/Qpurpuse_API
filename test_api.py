import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def print_response(response, test_name):
    """Helpre to print formatted response"""
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print(f"\n{'='*60}")
    
def test_health_check():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "Health Check")
    return response.status_code == 200

def test_register():
    """Test user registration"""
    user_data = {
        "username": f"testuser_{sys.version_info.micro}",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/api/register", json=user_data)
    print_response(response, "User Registration")

    if response.status_code == 201:
        data = response.json()
        return data.get('access_token')
    return None

def test_login():
    """Test user login"""
    login_data = {
        "username": f"testuser_{sys.version_info.micro}",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/api/login", json=login_data)
    print_response(response, "User Login")

    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    return None

def test_create_task(token):
    """Test creating a task"""
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {
        "title": "Test Task from Script",
        "description": "This is a test task created by the test script",
        "due_date": "2024-12-31T23:59:59"
    }
    response = requests.post(f"{BASE_URL}/api/tasls", json=task_data, headers=headers)

    if response.status_code == 201:
        data = response.json()
        return data.get('task', {}).get('id')
    return None

def test_get_tasks(token):
    """Test getting all tasks"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
    print_response(response, "Get All Tasks")
    return response.status_code == 200

def test_protected_without_token():
    """Test the access to a protected endpoint without token"""
    response = requests.get(f"{BASE_URL}/api/tasks")
    print_response(response, "Getting tasks without Token should fail")
    return response.status_code == 401

def main():
    """Run all tests"""
    print("Starting API tests")
    print(f"Base URL: {BASE_URL}")

    if not test_health_check():
        print("Health check failed. Make suer the server is running.")
        return
    
    token = test_register()
    if not token:
        print("Authentication tests failed.")
        return
    
    print(f"\nAuthentication test PASSED")
    print(f"Token: {token[:50]}...")

    task_id = test_create_task(token)
    if task_id:
        print(f"\nTask created with ID: {task_id}")

    test_get_tasks(token)

    test_protected_without_token()

    print("\n" + "="*60)
    print("All tests PASSED")
    print("\n" + "="*60)

if __name__ == '__main__':
    main()