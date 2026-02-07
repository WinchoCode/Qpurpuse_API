import os
import sys
from pathlib import Path

current_dir = Path(__file__).parent

sys.path.insert(0, str(current_dir))

from src.app import create_app, initialize_extensions

if __name__ == '__main__':
    app = create_app()

    initialize_extensions(app)

    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = app.config.get('DEBUG', False)

    print(f"Starting Task Manager")
    print(f"Environment: {app.config.get(app.config.get('ENV', 'development'))}")
    print(f"Debug mode: {debug}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
    print(f"Server: http://{host}:{port}")
    print(f"Health check: http://{host}:{port}/health")
    print(f"API docs: http://{host}:{port}/")

    app.run(host=host, port=port, debug=debug)