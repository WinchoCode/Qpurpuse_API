import pytest
import os
import tempfile
from datetime import datetime, timedelta

from src.app import create_app
from src.database import db
from src.models import User, Task
from faker import Faker

fake = Faker()

@pytest.fixture(scope='session')
def app():
    """Create a Flask app configured for testing"""
    db_fd, db_path = tempfile.mkstemp()

    app = create_app('testing')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite://{db_path}'
    app.config['TESTING'] = True

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a CLI runner"""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def db_session(app):
    """Create a testing database"""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        session = db.create_scoped_session(options={'bind': connection})
        db.session = session

        yield session

        transaction.rollback()
        connection.close()
        session.remove()

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        username='testuser',
        password_hash='$2b$1234567890!"#¤%&/()=@£$€{[]}qwerQWERasdfASDFzxcvZXCV'
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_user_with_password(db_session):
    user = User(username='authuser')
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_tasks(db_session, test_user):
    """Create a test task"""
    tasks = []
    for i in range(3):
        task = Task(
            task_title=f"Test Task {i+1}",
            task_description=f"Description for task {i+1}",
            task_due_date=datetime.utcnow() + timedelta(days=i+1),
            task_is_completed=(i % 2 == 0),
            user_id=test_user.id
        )
        db_session.add(task)
        tasks.append(task)

    db_session.commit()
    return tasks

@pytest.fixture
def auth_headers(test_user_with_password, client):
    """Get authentication for a test"""
    response = client.post('/api/login', json={
        'username': test_user_with_password.username,
        'password': 'testpassword123'
    })

    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

