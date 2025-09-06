import pytest
from app import create_app, db
from app.models import User, Student, Teacher, Parent, SchoolClass, Subject
from config import TestConfig

@pytest.fixture(scope='function')
def test_client():
    flask_app = create_app(TestConfig)

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            db.create_all()
            yield testing_client
            db.drop_all()

def create_and_login_user(client, role):
    """Helper function to create and log in a user of a specific role."""
    password = 'password'
    user = User(username=f'{role}user', email=f'{role}@test.com', role=role, is_verified=True)
    user.set_password(password)

    if role == 'student':
        profile = Student(admission_no=f's_{role}', user=user)
        db.session.add(profile)
    elif role == 'teacher':
        profile = Teacher(user=user)
        db.session.add(profile)
    elif role == 'parent':
        profile = Parent(user=user)
        db.session.add(profile)

    db.session.add(user)
    db.session.commit()

    client.post('/auth/login', data=dict(
        username=f'{role}user',
        password=password
    ), follow_redirects=True)
    return user

@pytest.mark.parametrize("page", [
    "/admin/students",
    "/admin/teachers",
    "/admin/parents",
    "/admin/classes",
    "/admin/subjects",
])
def test_admin_pages_unauthorized_access(test_client, page):
    """Test that non-admin users get a 403 Forbidden error."""
    # Test with a teacher user
    create_and_login_user(test_client, 'teacher')
    response = test_client.get(page)
    assert response.status_code == 403

    # Test with a student user
    create_and_login_user(test_client, 'student')
    response = test_client.get(page)
    assert response.status_code == 403

def test_list_students_page(test_client):
    """Test that the admin can see a list of students."""
    create_and_login_user(test_client, 'admin')

    # Create a sample student to look for
    user = User(username='teststudent', email='student@test.com', role='student', is_verified=True)
    user.set_password('password')
    student = Student(admission_no='S123', user=user)
    db.session.add(user)
    db.session.add(student)
    db.session.commit()

    response = test_client.get('/admin/students')
    assert response.status_code == 200
    assert b'Students' in response.data
    assert b'S123' in response.data # Check for the admission number

def test_list_classes_page(test_client):
    """Test that the admin can see a list of classes."""
    create_and_login_user(test_client, 'admin')

    # Create a sample class
    school_class = SchoolClass(name='Grade 5', academic_year='2023-2024')
    db.session.add(school_class)
    db.session.commit()

    response = test_client.get('/admin/classes')
    assert response.status_code == 200
    assert b'Classes' in response.data
    assert b'Grade 5' in response.data
