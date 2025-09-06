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
            # Create a user for each role
            create_test_user('admin', 'admin@test.com')
            create_test_user('teacher', 'teacher@test.com')
            create_test_user('student', 'student@test.com')
            create_test_user('parent', 'parent@test.com')
            yield testing_client
            db.drop_all()

def create_test_user(role, email):
    """A helper function to create a user with a specific role and linked profile."""
    user = User(username=f'{role}user', email=email, role=role, is_verified=True)
    user.set_password('password')

    # Create the role-specific profile and link it to the user
    if role == 'student':
        student_profile = Student(admission_no=f'test{role}', user=user)
        db.session.add(student_profile)
    elif role == 'teacher':
        teacher_profile = Teacher(user=user)
        db.session.add(teacher_profile)
    elif role == 'parent':
        parent_profile = Parent(user=user)
        db.session.add(parent_profile)

    db.session.add(user)
    db.session.commit()
    return user

def login(client, username, password):
    return client.post('/auth/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def test_dashboard_unauthenticated_access(test_client):
    """Test that unauthenticated users are redirected from dashboard to login."""
    response = test_client.get('/dashboard', follow_redirects=True)
    assert response.status_code == 200
    assert b'Sign In' in response.data

def test_admin_dashboard_access(test_client):
    """Test that an admin user sees the admin dashboard."""
    login(test_client, 'adminuser', 'password')
    response = test_client.get('/dashboard')
    assert response.status_code == 200
    assert b'Admin Dashboard' in response.data
    assert b'Total Students' in response.data

def test_teacher_dashboard_access(test_client):
    """Test that a teacher user sees the teacher dashboard."""
    login(test_client, 'teacheruser', 'password')
    response = test_client.get('/dashboard')
    assert response.status_code == 200
    assert b'Teacher Dashboard' in response.data
    assert b'Your Classes & Subjects' in response.data

def test_student_dashboard_access(test_client):
    """Test that a student user sees the student dashboard."""
    login(test_client, 'studentuser', 'password')
    response = test_client.get('/dashboard')
    assert response.status_code == 200
    assert b'Student Dashboard' in response.data
    assert b'Your Information' in response.data

def test_parent_dashboard_access(test_client):
    """Test that a parent user sees the parent dashboard."""
    login(test_client, 'parentuser', 'password')
    response = test_client.get('/dashboard')
    assert response.status_code == 200
    assert b'Parent Dashboard' in response.data
    assert b'Your Child/Children' in response.data
