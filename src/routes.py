from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from src.database import db
from src.models import User, Task
from src.auth import authenticate_user, create_user, create_auth_token

def get_current_user():
    """Get the current authenticated user from JWT"""
    try:
        user_id = get_jwt_identity()
        if user_id:
            return User.query.get(int(user_id))
    except Exception:
        pass
    return None

def validate_required_fields(data, required_fields):
    """Validate that all required fields exist"""
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return False, f"Missing required fields: {','.join(missing_fields)}"
    return True, None
    
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        is_valid, error_msg = validate_required_fields(data, ['username', 'password'])
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        username = data['username'].strip()
        password = data['password']

        if len(username) < 3:
            return jsonify({"error": "Username must be at least 3 characters"}), 400
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        user, error = create_user(username, password)
        if error:
            return jsonify({"error": error}), 400
        
        token = create_auth_token(user)

        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dictionary(),
            "access_token": token
        }), 201
    
    except Exception as exept:
        return jsonify({"error": f"Registration failed: {str(exept)}"}), 500
    
def login():
    """Authenticate user and return JWT token"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        is_valid, error_msg = validate_required_fields(data, ['username', 'password'])
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        username = data['username']
        password = data['password']

        user = authenticate_user(username, password)
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401
        
        token = create_auth_token(user)

        return jsonify({
            "message": "Login successful",
            "user": user.to_dictionary(),
            "access_token": token
        }), 200
    
    except Exception as exept:
        return jsonify({"error": f"Login failed: {str(exept)}"}), 500
    
@jwt_required()
def get_tasks():
    """Get all tasks for the authenticated user"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 404
            
        completed = request.args.get('completed', type=str)
        search = request.args.get('search', type=str)

        query = Task.query.filter_by(user_id=current_user.id)

        if completed is not None:
            if completed.lower() == 'true':
                query = query.filter_by(is_completed=True)
            elif completed.lower() == 'false':
                query = query.filter_by(is_completed=False)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Task.task_title.ilike(search_term)) |
                (Task.task_description.ilike(search_term))
            )

        tasks = query.order_by(Task.task_created_at.desc()).all()

        return jsonify({
            "task": [task.to_dictionary() for task in tasks],
            "count": len(tasks)
        }), 200
        
    except Exception as exept:
        return jsonify({"error": f"Failed to get tasks: {str(exept)}"}), 500
        
@jwt_required()
def create_task():
    """Create a new task for the authenticated user"""

    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        is_valid, error_msg = validate_required_fields(data, ['title'])
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        due_date = None
        if 'due_date' in data and data['due_date']:
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({"error": "Invalid date format. Use ISO format (e.g., 2024-12-31T23:59:59)"}), 400
            
            task = Task(
                task_title=data['title'].strip(),
                task_description=data.get('description', '').strip(),
                task_due_date=due_date,
                task_is_completed=data.get('is_completed', False),
                user_id=current_user.id
            )

            db.session.add(task)
            db.session.commit()

            return jsonify({
                "message": "Task created successfully",
                "task": task.to_dictionary()
            }), 201
        
    except Exception as exept:
        db.session.rollback()
        return jsonify({"error": f"Failed to create task: {str(exept)}"}), 500
    
@jwt_required()
def get_task(task_id):
    """Get an specific task by ID"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        return jsonify({"task": task.to_dictionary()}), 200
    
    except Exception as exept:
        return jsonify({"error": f"Failed to get task: {str(exept)}"}), 500
    
@jwt_required()
def update_task(task_id):
    """Update a specific task"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if 'title' in data:
            task.task_title = data['title'].strip()

        if 'description' in data:
            task.task_description = data['description'].strip()

        if 'due_date' in data:
            if data['due_date'] is None:
                task.task_due_date = None
            else:
                try:
                    task.task_due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({"error": "Invalid date format. Use ISO format"}), 400
                
        if 'is_completed' in data:
            task.task_is_completed = bool(data['is_completed'])

        task.task_updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            "message": "Task updated successfully",
            "task": task.to_dictionary()
        }), 200
    
    except Exception as exept:
        db.session.rollback()
        return jsonify({"error": f"Failed to update task: {str(exept)}"}), 500
    
@jwt_required()
def delete_task(task_id):
    """Delete a specific task"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"error": "User not found"}), 404
        
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        db.session.delete(task)
        db.session.commit()

        return jsonify({"message": "Task deleted successfully"}), 200
    
    except Exception as exept:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete task: {str(exept)}"}), 500
