import sys
import os

sys.path.insert(0, os.path.abspath('.'))

def test_flask_app_creation():
    """Test the creation of a Flask app"""
    try:
        from src.app import create_app

        app = create_app('development')

        assert app is not None, "App should not be None"
        assert app.name == 'src.app', f"App name should be 'src.app', got {app.name}'"
        assert app.config['DEBUG'] == True, "Debug should be True in developmnet"
        
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
        assert db_uri is not None, "Database URI should be set"

        print("Flask app creation test PASSED!")
        print(f"App name: {app.name}")
        print(f"Debug mode: {app.config['DEBUG']}")
        print(f"Database URI: {db_uri}")

        with app.test_client() as client:
            response = client.get('/health')
            assert response.status_code == 200, "Health check should return 200"
            data = response.get_json()
            assert data['status'] == 'healthy', "Health status shold be 'healthy'"

            print("Health check endpoint test PASSED!")

            return True
        
    except Exception as exept:
        print(f"Test FAILED: {exept}")
        import traceback
        traceback.print_exc()
        return False
    
def test_database_setup():
    """Test database initialization"""
    try:
        from src.app import create_app
        from src.database import db
        from src.models import User

        app = create_app('testing')

        with app.app_context():
            db.init_app(app)
            db.create_all()

            user = User(username="testuser")
            user.set_password("testpassword123")

            db.session.add(user)
            db.session.commit()

            saved_user = User.query.filter_by(username="testuser").first()

            assert saved_user is not None, "User should be saved to database"
            assert saved_user.username == "testuser", "Username should match"
            assert saved_user.check_password("testpassword123"), "Password should be verified"

            print("Database setup test PASSED!")
            print(f"User created: {saved_user.username}")
            print(f"User ID: {saved_user.id}")

            db.session.query(User).delete()
            db.session.commit()

        return True
    
    except Exception as exept:
        print(f"Database test FAILED: {exept}")
        import traceback
        traceback.print_exc()
        return False
    
if __name__ == "__main__":
    print("=" * 60)
    print("Running API Tests")
    print("=" * 60)

    test1_passed = test_flask_app_creation()
    test2_passed = test_database_setup()

    print("=" * 60)
    if test1_passed and test2_passed:
        print("All setup tests PASSED!")
        print("You can proceed to build the API routes.")
    else:
        print("Some tests FAILED!")
        print("Please fix the issues before proceeding")
    print("=" * 60)
