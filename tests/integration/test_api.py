import json
from datetime import datetime, timedelta

def test_health_check(client):
    """Test health check"""
    response = client.get('/health')

    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'service' in data

def test_home_endpoint(client):
    """Test root endpoint"""
    response = client.get('/')

    assert response.status_code ==200
    data = response.get_json()
    assert 'message' in data
    assert 'endpoints' in data
    assert 'auth' in data['endpoints']
    assert 'tasks' in data['endpoints']

def test_register_success(client, db_session):    
    """Test successful user registration"""
    from src.models import User

    response = client.post('/api/register', json={
        'username': 'integration_test',
        'password': 'integration_password123'
    })

    assert response.status_code == 201
    data = response.get_json()

    assert data['message'] == 'User registered successfully'
    assert 'user' in data
    assert data['user']['username'] == 'integration_test'
    assert 'access_token' in data
    assert len(data['access_token']) > 50

    user = User.query.filter_by(username='integration_test')
    assert user is not None

def test_register_missing_fields(client):
    """Test registration missing fields"""
    response = client.post('/api/register', json={
        'username': 'user'
    })

    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'required fields' in data['error'].lower()

    response = client.post('/api/register', json={
        'password': 'password'
    })

    assert response.status_code == 400

def test_register_duplicate_username(client, test_user):
    """Test duplication of username"""
    response = client.post('/api/register', json={
        'username': test_user.username,
        'password': 'newpassword'
    })

    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'already exists' in data['error'].lower()

def test_login_success(client, test_user_with_password):
    """Test login, successful"""
    response = client.post('/api/login', json={
        'username': test_user_with_password.username,
        'password': 'password123'
    })

    assert response.status_code == 200
    data = response.get_json()

    assert data['message'] == 'Login successful'
    assert 'user' in data
    assert data ['user']['username'] == test_user_with_password.username
    assert 'access_token' in data

def test_login_wrong_password(client, test_user_with_password):
    """Test login with wrong password"""
    response = client.post('/api/login', json={
        'username': test_user_with_password.username,
        'password': 'wrongpassword'
    })

    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data
    assert 'invalid' in data['error'].lower()

def test_login_nonexistent_user(client):
    """Test login, nonexistent user"""
    response = client.post('/api/login', json={
        'username': 'nonexistent',
        'password': 'password'
    })

    assert response.status_code == 401

def test_protected_endpoint_without_token(client):
    """Test access to endpoint without token"""
    response = client.get('/api/tasks')

    assert response.status_code == 401
    data = response.get_json()
    assert 'msg' in data

def test_create_task_success(client, auth_headers):
    """Test creation of a task with aouthentication"""
    task_data = {
        'task_title': 'Integration test task',
        'task_description': 'Task from the integration test',
        'task_due_date': (datetime.utcnow() + timedelta(days=7)).isoformat(),
        'task_is_completed': False
    }

    response = client.post('/api/tasks', json=task_data, headers=auth_headers)

    assert response.status_code == 201
    data = response.get_json()

    assert data['message'] == 'Task created successfully'
    assert 'task' in data
    assert data['task']['task_title'] == task_data['task_title']
    assert data['task']['task_description'] == task_data['task_description']
    assert data['task']['task_is_completed'] == task_data['task_is_completed']

def test_create_task_missing_title(client, auth_headers):
    """Test creating a task without title"""
    response = client.post('/api/tasks', json={'description': 'No title'}, headers=auth_headers)

    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'required' in data['error'].lower()

def test_create_task_invalid_date(client, auth_headers):
    """Test creating task with invalid date format"""
    response = client.post('/api/tasks', json={
        'task_title': 'Test task',
        'task_due_date': 'not-a-valid-date'
    }, headers=auth_headers)

    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'date' in data['error'].lower()

def test_get_tasks_empty(client, auth_headers):
    """Test getting tasks when user has no tasks"""
    response = client.get('/api/tasks', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()

    assert 'tasks' in data
    assert 'count' in data
    assert len(data['tasks']) == 0
    assert data['count'] == 0

def test_get_tasks_with_data(client, auth_headers, test_tasks):
    """Test getting tasks when user has tasks"""
    response = client.get('/api/tasks', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()

    assert 'tasks' in data
    assert 'count' in data
    assert len(data['tasks']) == 3
    assert data['count'] == 3

    task = data ['tasks'][0]
    assert 'task_id' in task
    assert 'task_title' in task
    assert 'task_description' in task
    assert 'task_is_completed' in task
    assert 'task_created_at' in task

def test_get_completed_tasks(client, auth_headers, test_tasks):
    """Test retrieve the completed tasks"""
    response = client.get('/api/tasks?completed=true', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()

    assert data['count'] == 2
    for task in data['tasks']:
        assert task['task_is_completed'] is True

    response = client.get('/api/tasks?completed=false', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()

    assert data['count'] == 1
    for task in data['tasks']:
        assert task['task_is_completed'] is False

def test_get_single_task_success(client, auth_headers, test_tasks):
    """Test getting a single task"""
    task_id = test_tasks[0].task_id

    response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()

    assert 'task' in data
    assert data['task']['task_id'] == task_id
    assert data['task']['task_title'] == test_tasks[0].task_title

def get_single_task_not_found(client, auth_headers):
    """Test getting non-existent task"""
    response = client.get('/api/tasks/99999', headers=auth_headers)

    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data

def test_get_other_users_task(client, auth_headers, db_session):
    """Test cannot access another user's task"""
    from src.models import User, Task
    other_user = User(username='otheruser')
    other_user.set_password("password")
    db_session.add(other_user)
    db_session.commit()

    other_task = Task(task_title="Another user's task", user_id=other_user.id)
    db_session.add(other_task)
    db_session.commit()

    response = client.get(f'/api/tasks/{other_task.task_id}', headers=auth_headers)

    assert response.status_code == 404

def test_update_task_success(client, auth_headers, test_tasks):
    """Test task update"""
    task_id = test_tasks[0].task_id

    update_data = {
        'task_title': 'Updated task title',
        'task_description': 'Updated task description',
        'task_is_completed': True
    }

    response = client.put(f'/api/tasks/{task_id}', 
                         json=update_data,
                         headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['message'] == 'Task updated successfully'
    assert data['task']['task_title'] == update_data['task_title']
    assert data['task']['task_description'] == update_data['task_description']
    assert data['task']['task_is_completed'] == update_data['task_is_completed']

def test_update_task_partial(client, auth_headers, test_tasks):
    """Test updating only some fields"""
    task_id = test_tasks[0].task_id
    original_title = test_tasks[0].task_title
    
    response = client.put(f'/api/tasks/{task_id}', 
                         json={'task_description': 'Only description updated'},
                         headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['task']['task_title'] == original_title
    assert data['task']['task_description'] == 'Only description updated'

def test_delete_task_success(client, auth_headers, test_tasks, db_session):
    """Test deleting a task"""
    from src.models import Task

    task_id = test_tasks[0].task_id
    
    task = Task.query.get(task_id)
    assert task is not None
    
    response = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Task deleted successfully'
    
    task = Task.query.get(task_id)
    assert task is None

def test_delete_task_not_found(client, auth_headers):
    """Test deleting non-existent task"""
    response = client.delete('/api/tasks/99999', headers=auth_headers)
    
    assert response.status_code == 404