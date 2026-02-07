import os
from flask import Flask, jsonify
from flask_restful import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()

def create_app(config_name='development'):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    if config_name == 'testing':
        app.config.from_object('src.config.TestingConfig')
    elif config_name == 'production':
        app.config.from_object('src.config.ProductionConfig')
    else:
        app.config.from_object('src.config.DevelopmentConfig')

    CORS(app)

    api = Api(app)

    jwt = JWTManager(app)

    register_routes(app, api)

    @app.errorhandler(404)
    def notfound(error):
        """Handle 404 errors"""
        return jsonify({
            'error': 'Resource not found',
            'message': 'The requested URL was not found on the server'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        app.logger.error(f'Server Error: {error}')
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 errors"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication is required to access this resource'
        }), 401
    
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for monitoring"""
        return jsonify({
            'status': 'healthy',
            'service': 'Qpurpose Task Manager API',
            'version': '0.0.0'
        }), 200
    
    @app.route('/', methods=['GET'])
    def home():
        """Root endpoint with API information"""
        return jsonify({
            'message': 'Welcome to Qpurpose Task Manager API',
            'version': '0.0.0',
            'documentation': '/docs',
            'endpoints': {
                'auth': {
                    'register': 'api/register (POST)',
                    'login': 'api/login (POST)'
                },
                'tasks':{
                    'list_tasks': '/api/tasks (GET)',
                    'create_task': '/api/tasks (POST)',
                    'get_task': '/api/tasks/<id> (GET)',
                    'update_task': '/api/tasks/<id> (PUT)',
                    'delete_task': '/api/tasks/<id> (DELETE)'
                },
            }
        }), 200
    
    return app


def register_routes(app, api):
    """Register all API routes"""
    print("this is still to be created")
    pass
        
def initialize_extensions(app):
    """Initialize database and other extensions"""
    from src.database import db
    db.init_app(app)

    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")

    return app

if __name__ == '__main__':
    app = create_app()

    initialize_extensions(app)

    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = app.config.get('DEBUG', False)

    print(f"Starting Task Manager API")
    print(f"Environment: {app.config.get('ENV', 'development')}")
    print(f"Debug mode: {debug}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    print(f"Server: http://{host}:{port}")
    print(f"Health check: http://{host}:{port}/health")

    app.run(host=host, port=port, debug=debug)