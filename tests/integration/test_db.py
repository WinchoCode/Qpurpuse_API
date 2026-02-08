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
    
    task = Task(task_title="Database Test Task", user_id=saved_user.id)
    db_session.add(task)
    db_session.commit()
    
    saved_task = Task.query.filter_by(task_title="Database Test Task").first()
    assert saved_task is not None
    assert saved_task.user_id == saved_user.id
    
    assert len(saved_user.tasks) == 1
    assert saved_user.tasks[0].title == "Database Test Task"

def test_transaction_rollback(db_session):
    """Test that failed transactions are rolled back"""
    initial_count = User.query.count()
    
    try:
        user1 = User(username="rollback1")
        user1.set_password("pass1")
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(username="rollback1")
        user2.set_password("pass2")
        db_session.add(user2)
        db_session.commit()  
        
        assert False, "Should have raised an exception"
        
    except Exception:
        db_session.rollback()
        
        assert User.query.count() == initial_count + 1

def test_query_filters(db_session, test_user):
    """Test various query filters"""
    tasks = [
        Task(task_title="Task 1", task_is_completed=True, user_id=test_user.id),
        Task(task_title="Task 2", task_is_completed=False, user_id=test_user.id),
        Task(task_title="Task 3", task_is_completed=True, user_id=test_user.id),
        Task(task_title="Archived", task_is_completed=False, user_id=test_user.id),
    ]
    
    for task in tasks:
        db_session.add(task)
    db_session.commit()
    
    completed_tasks = Task.query.filter_by(user_id=test_user.id, task_is_completed=True).all()
    
    assert len(completed_tasks) == 2
    for task in completed_tasks:
        assert task.task_is_completed is True
    
    archived_task = Task.query.filter_by(user_id=test_user.id,task_title="Archived").first()
    
    assert archived_task is not None
    assert archived_task.title == "Archived"
    
    search_result = Task.query.filter(Task.user_id == test_user.id, Task.task_title.like('%Task%')).all()
    
    assert len(search_result) == 3

def test_ordering(db_session, test_user):
    """Test query ordering"""
    tasks = [
        Task(task_title="Zebra Task", user_id=test_user.id),
        Task(task_title="Alpha Task", user_id=test_user.id),
        Task(task_title="Middle Task", user_id=test_user.id),
    ]
    
    for task in tasks:
        db_session.add(task)
    db_session.commit()
    
    ascending = Task.query.filter_by(user_id=test_user.id)\
                         .order_by(Task.task_title.asc())\
                         .all()
    
    assert ascending[0].task_title == "Alpha Task"
    assert ascending[1].task_title == "Middle Task"
    assert ascending[2].task_title == "Zebra Task"
    
    descending = Task.query.filter_by(user_id=test_user.id)\
                          .order_by(Task.task_title.desc())\
                          .all()
    
    assert descending[0].task_title == "Zebra Task"
    assert descending[1].task_title == "Middle Task"
    assert descending[2].task_title == "Alpha Task"