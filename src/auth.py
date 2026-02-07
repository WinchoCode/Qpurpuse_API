from flask import jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from src.database import db
from src.models import User

def authenticate_user(username, password):
    """Authenticate a user using the username and password"""

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None

def create_user(username, password):
    """Create a new user"""
    if User.query.filter_by(username=username).first():
        return None, "Username already exists"
    
    user = User(username=username)
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return user, None

def create_auth_token(user):
    """Create a JWT token for a user"""
    token = create_access_token(identity=str(user.id))
    return token