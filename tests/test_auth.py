import pytest
from app import create_app, db
from app.models import User
from config import TestConfig

@pytest.fixture(scope='function')
def test_client():
    flask_app = create_app(TestConfig)

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            db.create_all()
            yield testing_client  # this is where the testing happens!
            db.drop_all()


def test_register(test_client):
    response = test_client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password',
        'password2': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.role == 'student'


def test_login_logout(test_client):
    # First register a user
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    # Test login
    response = test_client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome to the School Management System' in response.data

    # Test logout
    response = test_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
