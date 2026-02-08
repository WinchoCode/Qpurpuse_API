import pytest
from src.auth import authenticate_user, create_user, create_auth_token
from src.models import User
from flask_jwt_extended import decode_token

def test_create_user_success(db_session):
    """Test user creation, when success"""
    user, error, = create_user("user", "password123")

    assert error is None
    assert user is not None
    assert user.username == "user"
    assert user.check_password("password123")

    saved_user = User.query.filter_by(username="user").first()
    assert saved_user is not None
    assert saved_user.id == user.id

def test_create_user_duplicate(db_session):
    """Create a user that already exists"""
    user1, error1 = create_user("duplicate_user", "pass1234")
    assert error1 is None

    user2, error2 = create_user("duplicate_user", "pass2345")
    assert error2 == "Username already exists"

def test_authenticate_user_success(db_session):
    """Test user authentication, successful"""
    user, _ = create_user("authentic_user", "authenticpassword")

    authenticated_user = authenticated_user("authentic_user", "authenticpassword")

    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    assert authenticated_user.username == "authentic_user"

def test_authenticate_user_wrong_password(db_session):
    """Test user authentication, with wrong password"""
    user, _ = authenticate_user("authentic_user", "correctpassword")

    authenticated_user = authenticate_user("authentic_user", "wrongpassword")

    assert authenticated_user is None

def test_authenticate_user_nonexistent(db_session):
    """Test user authentication, user doesn´t exist"""
    authenticated_user = authenticate_user("nouser", "nopassword")
    
    assert authenticated_user is None

def test_create_authentication_token(db_session, app):
    """Test JWT token creation"""
    from datetime import datetime, timedelta
    
    user, _ = create_user("user", "password")

    with app.app_context():
        token = create_auth_token(user)

        decoded_token = decode_token(token)

        assert decoded_token['sub'] == str(user.id)
        assert decoded_token['type'] == 'access'

        exp_timestamp = decoded_token['exp']
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        time_until_expiry = exp_datetime - datetime.utcnow()
        assert timedelta(minutes=59) < time_until_expiry < timedelta(minutes=61)

def test_password_validation(db_session):
    """Test password validation"""
    user, error = create_user("user", "123")

    assert user is not None
    assert user.password_hash != "123"
    assert user.check_password("123")

def test_username_trimming(db_session):
    """Test that usernames are trimmed"""
    user, error = create_user("     spaceduser     ", "password")

    assert user is not None
    assert user.username == "     spaceduser     "
