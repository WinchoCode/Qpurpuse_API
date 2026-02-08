import pytest
from src.models import User, Task

def test_database_connection(db_session):
    """Test basic database operations"""
    user = User(username="db_test")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()
    
    saved_user = User.query.filter_by(username="db_test").first()
    assert saved_user is not None
    assert saved_user.username == "db_test"
    
    task = Task(title="Database Test Task", user_id=saved_user.id)
    db_session.add(task)
    db_session.commit()
    
    saved_task = Task.query.filter_by(title="Database Test Task").first()
    assert saved_task is not None
    assert saved_task.user_id == saved_user.id
    
    assert len(saved_user.tasks) == 1
    assert saved_user.tasks[0].title == "Database Test Task"

def test_query_filters(db_session, test_user_with_password):
    """Test various query filters"""
    tasks = [
        Task(title="Task 1", is_completed=True, user_id=test_user_with_password.id),
        Task(title="Task 2", is_completed=False, user_id=test_user_with_password.id),
        Task(title="Task 3", is_completed=True, user_id=test_user_with_password.id),
        Task(title="Archived", is_completed=False, user_id=test_user_with_password.id),
    ]
    
    for task in tasks:
        db_session.add(task)
    db_session.commit()
    
    completed_tasks = Task.query.filter_by(user_id=test_user_with_password.id, is_completed=True).all()
    
    assert len(completed_tasks) == 2
    for task in completed_tasks:
        assert task.is_completed is True
    
    archived_task = Task.query.filter_by(user_id=test_user_with_password.id,title="Archived").first()
    
    assert archived_task is not None
    assert archived_task.title == "Archived"
    
    search_result = Task.query.filter(Task.user_id == test_user_with_password.id, Task.title.like('%Task%')).all()
    
    assert len(search_result) == 3

def test_ordering(db_session, test_user_with_password):
    """Test query ordering"""
    tasks = [
        Task(title="Zebra Task", user_id=test_user_with_password.id),
        Task(title="Alpha Task", user_id=test_user_with_password.id),
        Task(title="Middle Task", user_id=test_user_with_password.id),
    ]
    
    for task in tasks:
        db_session.add(task)
    db_session.commit()
    
    ascending = Task.query.filter_by(user_id=test_user_with_password.id)\
                         .order_by(Task.title.asc())\
                         .all()
    
    assert ascending[0].title == "Alpha Task"
    assert ascending[1].title == "Middle Task"
    assert ascending[2].title == "Zebra Task"
    
    descending = Task.query.filter_by(user_id=test_user_with_password.id)\
                          .order_by(Task.title.desc())\
                          .all()
    
    assert descending[0].title == "Zebra Task"
    assert descending[1].title == "Middle Task"
    assert descending[2].title == "Alpha Task"