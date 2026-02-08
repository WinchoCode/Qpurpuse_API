import pytest
from datetime import datetime, timedelta
from src.models import User, Task

def test_user_creation(db_session):
    """Test creating a new user"""
    user = User(username="newuser")
    user.set_password("password123")

    db_session.add(user)
    db_session.commit()

    saved_user = User.query.filter_by(username="newuser").first()
    assert saved_user is not None
    assert saved_user.id is not None
    assert saved_user.created_at  is not None
    assert isinstance(saved_user.created_at, datetime)

def test_user_password_hashing(db_session):
    """Test password hashing"""
    user = User(username="password_test")
    user.set_password("supersecretpassword")

    assert user.password_hash!= "supersecretpassword"
    assert user.password_hash.startswith("$2b$") or user.password_hash.startswith("scrypt:")
    assert user.check_password("supersecretpassword") is True
    assert user.check_password("wrongpassword") is False

def test_user_to_dict(db_session):
    """Test user serialization to dictionary"""
    user = User(username="dictuser")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()

    user_dict = user.to_dict()

    assert 'id' in user_dict
    assert user_dict['username'] == "dictuser"
    assert 'created_at' in user_dict
    assert 'password_hash' not in user_dict
    assert 'task_count' in user_dict
    assert user_dict['task_count'] == 0

def test_task_creation(db_session, test_user_with_password):
    """Test adding a new task"""
    due_date = datetime.utcnow() + timedelta(days=7)
    task = Task(
        title="Test task",
        description="Task description",
        due_date=due_date,
        is_completed=False,
        user_id=test_user_with_password.id
    )

    db_session.add(task)
    db_session.commit()

    saved_task = Task.query.filter_by(title="Test task").first()
    assert saved_task is not None
    assert saved_task.id is not None
    assert saved_task.title == "Test task"
    assert saved_task.description == "Task description"
    assert saved_task.due_date == due_date
    assert saved_task.is_completed is False
    assert saved_task.user_id == test_user_with_password.id
    assert saved_task.created_at is not None
    assert saved_task.updated_at is not None

def test_task_to_dict(db_session, test_user_with_password):
    """Test task to dictionary"""
    due_date = datetime.utcnow() + timedelta(days=3)
    task = Task(
        title="Dictionary task",
        description="Description of the task",
        due_date=due_date,
        is_completed=True,
        user_id=test_user_with_password.id
    )

    db_session.add(task)
    db_session.commit()

    task_dict = task.to_dict()

    assert task_dict['id'] == task.id
    assert task_dict['title'] == "Dictionary task"
    assert task_dict['description'] == "Description of the task"
    assert task_dict['is_completed'] is True
    assert task_dict['user_id'] == test_user_with_password.id
    assert 'created_at' in task_dict
    assert 'updated_at' in task_dict
    assert 'due_date' in task_dict
    assert isinstance(task_dict['created_at'], str)
    assert 'T' in task_dict['created_at']

def test_task_update_method(db_session, test_user_with_password):
    """Test the task update"""
    task = Task(
        title="Task title",
        description="Task description",
        user_id=test_user_with_password.id
    )
    db_session.add(task)
    db_session.commit()

    original_updated_at = task.updated_at

    task.update(
        title="Updated task title",
        description="Updated task description",
        is_completed=True
    )
    db_session.commit()

    assert task.title == "Updated task title"
    assert task.description == "Updated task description"
    assert task.is_completed is True
    assert task.updated_at > original_updated_at
    
    original_id = task.id
    original_user_id = task.user_id
    original_created_at = task.created_at

    task.update(
        id=999,
        user_id=999,
        created_at=datetime(1900, 1, 1)
    )

    assert task.id == original_id
    assert task.user_id == original_user_id
    assert task.created_at == original_created_at

def test_user_task_relationship(db_session):
    """Test the relationship between User and Task"""
    user = User(username="relationship_test")
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    task1 = Task(title="Task 1", user_id=user.id)
    task2 = Task(title="Task 2", user_id=user.id)

    db_session.add_all([task1, task2])
    db_session.commit()

    assert len(user.tasks) == 2
    assert user.tasks[0].title == "Task 1"
    assert user.tasks[1].title == "Task 2"
    assert task1.author == user    
    assert task2.author == user

def test_cascade_delete(db_session):
    """Test delete of all tasks when deleting user"""
    user = User(username="cascade_test")
    user.set_password("password")

    db_session.add(user)
    db_session.commit()

    task1 = Task(title="Task 1", user_id=user.id)
    task2 = Task(title="Task 2", user_id=user.id)

    db_session.add(task1)
    db_session.add(task2)
    db_session.commit()

    assert Task.query.filter_by(user_id=user.id).count() == 2

    db_session.delete(user)
    db_session.commit()

    assert Task.query.filter_by(user_id=user.id).count() == 0