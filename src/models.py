from datetime import datetime
from src.database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """User model for authentication."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship('Task', backref='author', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, user_password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(user_password)

    def check_password(self, user_password):
        """Check if the password is correct."""
        return check_password_hash(self.password_hash, user_password)
    
    def to_dict(self):
        """Convert user to a dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'task_count': len(self.tasks) if self.tasks else 0
        }
    
class Task(db.Model):
    """Definition of the task model."""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True, default="Description of the task")
    due_date = db.Column(db.DateTime, nullable=True)
    is_completed = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    def __repr__(self):
        return f'<Task {self.title[:30]}>'
    
    def to_dict(self):
        """Convert the task to a dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id
        }
    
    def update_from_dictionary(self, **kwargs):
        """Update the tasks from a dictionary."""
        for key, value, in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at', 'user_id']:
                setattr(self, key, value)
            self.updated_at = datetime.utcnow()

    def update(self, **kwargs):
        """Update task attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'created_at', 'user_id']:
                setattr(self, key, value)

        self.updated_at = datetime.utcnow()