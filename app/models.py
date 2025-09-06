import datetime
from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Association Table for Parent-Student Many-to-Many relationship
parent_student_association = db.Table('parent_student_association',
    db.Column('parent_id', db.Integer, db.ForeignKey('parent.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(10), index=True) # Admin, Teacher, Student, Parent
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    otp_code_hash = db.Column(db.String(128), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)

    # Relationships for each role
    student = db.relationship('Student', backref='user', uselist=False, cascade="all, delete-orphan")
    teacher = db.relationship('Teacher', backref='user', uselist=False, cascade="all, delete-orphan")
    parent = db.relationship('Parent', backref='user', uselist=False, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.String(20), unique=True, nullable=False)
    admission_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    parents = db.relationship(
        'Parent', secondary=parent_student_association,
        back_populates='children')

    def __repr__(self):
        return f'<Student {self.admission_no}>'

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_joined = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    def __repr__(self):
        # It's safer to check if user exists before accessing attributes
        if self.user:
            return f'<Teacher {self.user.username}>'
        return '<Teacher (no user)>'

class Parent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    children = db.relationship(
        'Student', secondary=parent_student_association,
        back_populates='parents')

    def __repr__(self):
        if self.user:
            return f'<Parent {self.user.username}>'
        return '<Parent (no user)>'
