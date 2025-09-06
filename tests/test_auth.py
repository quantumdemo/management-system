import pytest
import datetime
from app import create_app, db
from app.models import User, Student
from config import TestConfig
from werkzeug.security import generate_password_hash, check_password_hash

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

def test_registration_flow(test_client):
    """Test that registration creates an unverified user and redirects to verify page."""
    response = test_client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password',
        'password2': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Verify Your Email' in response.data

    user = User.query.filter_by(email='test@example.com').first()
    assert user is not None
    assert user.is_verified is False
    assert user.otp_code_hash is not None

def test_login_unverified_user(test_client):
    """Test that an unverified user is redirected to the verify page on login."""
    # Manually create an unverified user
    user = User(username='unverified', email='unverified@test.com', is_verified=False)
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    response = test_client.post('/auth/login', data={
        'username': 'unverified',
        'password': 'password'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your account is not verified' in response.data
    assert b'Verify Your Email' in response.data

def test_successful_verification(test_client):
    """Test that a user can verify their account with a correct OTP."""
    # Manually create an unverified user with a known OTP
    otp = '123456'
    user = User(
        username='verify_me',
        email='verify@test.com',
        role='student',  # Set the role
        otp_code_hash=generate_password_hash(otp),
        otp_expiry=datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    )
    user.set_password('password')

    # Create the associated Student profile
    student_profile = Student(admission_no='v123', user=user)

    db.session.add(user)
    db.session.add(student_profile)
    db.session.commit()

    response = test_client.post(f'/auth/verify-email?email={user.email}', data={
        'otp': otp
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your account has been successfully verified' in response.data
    assert b'Student Dashboard' in response.data # Should be on the dashboard now

    verified_user = User.query.filter_by(email='verify@test.com').first()
    assert verified_user.is_verified is True
    assert verified_user.otp_code_hash is None

def test_incorrect_otp(test_client):
    """Test that using an incorrect OTP fails verification."""
    otp = '123456'
    user = User(
        username='verify_me',
        email='verify@test.com',
        otp_code_hash=generate_password_hash(otp),
        otp_expiry=datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    )
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    response = test_client.post(f'/auth/verify-email?email={user.email}', data={
        'otp': '654321' # Incorrect OTP
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Invalid OTP' in response.data

    unverified_user = User.query.filter_by(email='verify@test.com').first()
    assert unverified_user.is_verified is False

def test_expired_otp(test_client):
    """Test that using an expired OTP fails verification."""
    otp = '123456'
    user = User(
        username='verify_me',
        email='verify@test.com',
        otp_code_hash=generate_password_hash(otp),
        # Set expiry to the past
        otp_expiry=datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    )
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    response = test_client.post(f'/auth/verify-email?email={user.email}', data={
        'otp': otp
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'OTP has expired' in response.data

    unverified_user = User.query.filter_by(email='verify@test.com').first()
    assert unverified_user.is_verified is False

def test_resend_otp(test_client):
    """Test the resend OTP functionality."""
    user = User(username='resend', email='resend@test.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    old_hash = user.otp_code_hash

    response = test_client.get(f'/auth/resend-otp?email={user.email}', follow_redirects=True)

    assert response.status_code == 200
    assert b'A new OTP has been sent' in response.data

    updated_user = User.query.filter_by(email='resend@test.com').first()
    assert updated_user.otp_code_hash is not None
    assert updated_user.otp_code_hash != old_hash
