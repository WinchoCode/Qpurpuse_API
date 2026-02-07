from datetime import datetime
from src.database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """User model for authentication."""
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    user_password_hash = db.Column(db.String(256), nullable=False)
    user_created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship('Task', backref='author', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.user_password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the password is correct."""
        return check_password_hash(self.user_password_hash, password)
    
    def to_dictionary(self):
        """Convert user to a dictionary"""
        return {
            'user_id': self.user_id,
            'user_username': self.user_username,
            'user_created_at': self.user_created_at.isoformat() if self.user_created_at else None,
            'task_counter': len(self.tasks) if self.tasks else 0
        }
    
class Task(db.Model):
    """Definition of the task model."""
    __tablename__ = 'tasks'

    task_id = db.Column(db.Integer, primary_key=True)
    task_title = db.Column(db.String(200), nullable=False, index=True)
    task_description = db.Column(db.Text, nullable=True)
    task_due_date = db.Column(db.DateTime, nullable=True)
    task_is_completed = db.Column(db.Boolean, default=False, index=True)
    task_created_at = db.Column(db.DateTime, default=datetime.utcnow)
    task_updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    def __repr__(self):
        return f'<Task {self.task_title[:30]}>'
    
    def to_dictionary(self):
        """Convert the task to a dictionary."""
        return {
            'task_id': self.task_id,
            'task_title': self.task_title,
            'task_description': self.task_description,
            'task_due_date': self.task_due_date.isoformat() if self.task_due_date else None,
            'task_is_completed': self.task_is_completed,
            'task_created_at': self.task_created_at.isoformat() if self.task_created_at else None,
            'task_updated_at': self.task_updated_at.isoformat() if self.task_updated_at else None,
            'user_id': self.user_id
        }
    
    def update_from_dictionary(self, **kwargs):
        """Update the tasks from a dictionary."""
        for key, value, in kwargs.items():
            if hasattr(self, key) and key not in ['task_id', 'task_created_at', 'user_id']:
                setattr(self, key, value)
            self.task_updated_at = datetime.utcnow()