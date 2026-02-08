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
    assert user.password_hash.startswith("$2b$")
    assert user.check_password("supersecretpassword") is True
    assert user.check_password("wrongpassword") is False

def test_user_to_dict(db_session):
    """Test user serialization to dictionary"""
    user = User(username="dictuser")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()

    user_dict = user.to_dictionary()

    assert 'id' in user_dict
    assert user_dict['username'] == "dictuser"
    assert 'created_at' in user_dict
    assert 'password_hash' not in user_dict
    assert 'task_count' in user_dict
    assert user_dict['task_count'] == 0

def test_task_creation(db_session, test_user):
    """Test adding a new task"""
    due_date = datetime.utcnow() + timedelta(days=7)
    task = Task(
        task_title="Test task",
        task_description="Description of the task",
        task_due_date=due_date,
        task_is_completed=False,
        task_user_id=test_user.id
    )

    db_session.add(task)
    db_session.commit()

    saved_task = Task.query.filter_by(title="Test task").first()
    assert saved_task is not None
    assert saved_task.task_id is not None
    assert saved_task.task_title == "Test task"
    assert saved_task.task_description == "Task description"
    assert saved_task.task_due_date == due_date
    assert saved_task.task_is_completed is False
    assert saved_task.user_id == test_user.id
    assert saved_task.task_created_at is not None
    assert saved_task.task_updated_at is not None

def test_task_to_dict(db_session, test_user):
    """Test task to dictionary"""
    due_date = datetime.utcnow() + timedelta(days=7)
    task = Task(
        task_title="Dictionary task",
        task_description="Description of the task",
        task_due_date=due_date,
        task_is_completed=False,
        task_user_id=test_user.id
    )

    db_session.add(task)
    db_session.commit()

    task_dict = task.to_dictionary()

    assert task_dict['task_id'] == task.task_id
    assert task_dict['task_title'] == "Dictionary task"
    assert task_dict['task_description'] == "Testing to_dict method"
    assert task_dict['task_is_completed'] is True
    assert task_dict['user_id'] == test_user.id
    assert 'task_created_at' in task_dict
    assert 'task_updated_at' in task_dict
    assert 'task_due_date' in task_dict
    assert isinstance(task_dict['task_created_at'], str)
    assert 'T' in task_dict['task_created_at']

def test_task_update_method(db_session, test_user):
    """Test the task update"""
    task = Task(
        task_title="Task title",
        task_description="Task description",
        user_id=test_user.id
    )
    db_session.add(task)
    db_session.commit()

    original_updated_at = task.task_updated_at

    task.update_task(
        task_title="Updated task title",
        task_description="Updated task description",
        task_is_completed=True
    )
    db_session.commit()

    assert task.task_title == "Updated task title"
    assert task.task_ == "Updated task description"
    assert task.task_is_completed is True
    assert task.task_updated_at > original_updated_at
    
    original_id = task.task_id
    original_user_id = task.user_id
    original_created_at = task.task_created_at

    task.update_task(
        task_id=999,
        user_id=999,
        task_created_at=datetime(1900, 1, 1)
    )

    assert task.task_id == original_id
    assert task.user_id == original_user_id
    assert task.task_created_at == original_created_at

def test_user_task_relationship(db_session):
    """Test the relationship between User and Task"""
    user = User(username="relationship_test")
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    task1 = Task(task_title="Task 1", user_id=user.id)
    task2 = Task(task_title="Task 2", user_id=user.id)

    db_session.add_all([task1, task2])
    db_session.commit()

    assert len(user.tasks) == 2
    assert user.tasks[0].task_title == "Task 1"
    assert user.tasks[1].task_title == "Task 2"
    assert task1.author == user    
    assert task2.author == user

def test_cascade_delete(db_session):
    """Test delete of all tasks when deleting user"""
    user = User(username="cascade_test")
    user.set_password("password123")

    task1 = Task(task_title="Task 1", user_id=user.id)
    task2 = Task(task_title="Task 2", user_id=user.id)

    db_session.add(user)
    db_session.add(task1)
    db_session.add(task2)
    db_session.commit()

    assert Task.query.filter_by(user_id=user.id).count() == 2

    db_session.delete(user)
    db_session.commit()

    assert Task.query.filter_by(user_id=user.id).count() == 0