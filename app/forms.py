from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import User, SchoolClass, Subject, Teacher

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class VerifyEmailForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify')


# Forms for Admin to create users
class AdminCreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class AdminCreateStudentForm(AdminCreateUserForm):
    admission_no = StringField('Admission Number', validators=[DataRequired()])
    submit = SubmitField('Create Student')

class AdminCreateTeacherForm(AdminCreateUserForm):
    submit = SubmitField('Create Teacher')

class AdminCreateParentForm(AdminCreateUserForm):
    submit = SubmitField('Create Parent')


class CreateClassForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired()])
    academic_year = StringField('Academic Year (e.g., 2023-2024)', validators=[DataRequired()])
    submit = SubmitField('Create Class')

class CreateSubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[DataRequired()])
    submit = SubmitField('Create Subject')

def get_teachers():
    return Teacher.query

def get_classes():
    return SchoolClass.query

def get_subjects():
    return Subject.query

class AssignTeacherForm(FlaskForm):
    teacher = QuerySelectField('Teacher', query_factory=get_teachers, get_label=lambda obj: obj.user.username, allow_blank=False)
    school_class = QuerySelectField('Class', query_factory=get_classes, get_label='name', allow_blank=False)
    subject = QuerySelectField('Subject', query_factory=get_subjects, get_label='name', allow_blank=False)
    submit = SubmitField('Assign')
