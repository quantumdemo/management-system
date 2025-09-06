import pytest
from app import create_app, db
from app.models import User, Student, Teacher, Parent
from config import TestConfig

@pytest.fixture(scope='function')
def test_client():
    flask_app = create_app(TestConfig)

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()

def create_and_login_user(client, role, username, email):
    """Helper function to create and log in a user of a specific role."""
    password = 'password'
    user = User(username=username, email=email, role=role, is_verified=True)
    user.set_password(password)

    if role == 'student':
        profile = Student(admission_no=f's_{username}', user=user, contact_phone='111', address='addr1')
        db.session.add(profile)
    elif role == 'teacher':
        profile = Teacher(user=user, contact_phone='222', address='addr2', qualifications='q1')
        db.session.add(profile)
    elif role == 'parent':
        profile = Parent(user=user, contact_phone='333', address='addr3')
        db.session.add(profile)

    db.session.add(user)
    db.session.commit()

    client.post('/auth/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)
    return user

def test_view_student_profile(test_client):
    """Test that a student can view their own profile."""
    create_and_login_user(test_client, 'student', 'student1', 'student1@test.com')
    response = test_client.get('/profile')
    assert response.status_code == 200
    assert b'Your Profile' in response.data
    assert b'Admission Number' in response.data
    assert b'111' in response.data # Check for initial phone number

def test_edit_student_profile(test_client):
    """Test that a student can edit their own profile."""
    create_and_login_user(test_client, 'student', 'student1', 'student1@test.com')

    # First, visit the edit page
    response = test_client.get('/profile/edit')
    assert response.status_code == 200
    assert b'Edit Your Profile' in response.data

    # Now, post the updated data
    response = test_client.post('/profile/edit', data={
        'contact_phone': '999-999-9999',
        'address': 'New Address 123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your profile has been updated' in response.data
    assert b'999-999-9999' in response.data
    assert b'New Address 123' in response.data

def test_view_teacher_profile(test_client):
    """Test that a teacher can view their own profile."""
    create_and_login_user(test_client, 'teacher', 'teacher1', 'teacher1@test.com')
    response = test_client.get('/profile')
    assert response.status_code == 200
    assert b'Qualifications' in response.data
    assert b'q1' in response.data

def test_edit_teacher_profile(test_client):
    """Test that a teacher can edit their own profile."""
    create_and_login_user(test_client, 'teacher', 'teacher1', 'teacher1@test.com')

    response = test_client.post('/profile/edit', data={
        'contact_phone': '888-888-8888',
        'address': 'New Teacher Address',
        'qualifications': 'PhD in Awesomeness'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your profile has been updated' in response.data
    assert b'PhD in Awesomeness' in response.data
