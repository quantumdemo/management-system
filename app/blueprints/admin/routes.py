from flask import render_template, redirect, url_for, flash
from app.blueprints.admin import bp
from app.utils.decorators import role_required
from app.extensions import db
from app.models import User, Student, Teacher, Parent
from app.forms import AdminCreateStudentForm, AdminCreateTeacherForm, AdminCreateParentForm

@bp.route('/')
@role_required('admin')
def admin_dashboard():
    # This will be the main admin dashboard view
    return "Welcome to the Admin Dashboard"

# Student Management
@bp.route('/students')
@role_required('admin')
def list_students():
    return "List of Students"

@bp.route('/students/add', methods=['GET', 'POST'])
@role_required('admin')
def add_student():
    form = AdminCreateStudentForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role='student'
        )
        new_user.set_password(form.password.data)

        # Create the student profile
        new_student = Student(
            admission_no=form.admission_no.data,
            user=new_user  # This links the student to the user
        )

        db.session.add(new_user)
        db.session.add(new_student)
        db.session.commit()

        flash('Student account created successfully.')
        return redirect(url_for('admin.list_students'))

    return render_template('admin/create_user.html', form=form, title='Create Student')

# Teacher Management
@bp.route('/teachers')
@role_required('admin')
def list_teachers():
    return "List of Teachers"

@bp.route('/teachers/add', methods=['GET', 'POST'])
@role_required('admin')
def add_teacher():
    form = AdminCreateTeacherForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role='teacher'
        )
        new_user.set_password(form.password.data)

        # Create the teacher profile
        new_teacher = Teacher(user=new_user)

        db.session.add(new_user)
        db.session.add(new_teacher)
        db.session.commit()

        flash('Teacher account created successfully.')
        return redirect(url_for('admin.list_teachers'))

    return render_template('admin/create_user.html', form=form, title='Create Teacher')

# Parent Management
@bp.route('/parents')
@role_required('admin')
def list_parents():
    return "List of Parents"

@bp.route('/parents/add', methods=['GET', 'POST'])
@role_required('admin')
def add_parent():
    form = AdminCreateParentForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role='parent'
        )
        new_user.set_password(form.password.data)

        # Create the parent profile
        new_parent = Parent(user=new_user)

        db.session.add(new_user)
        db.session.add(new_parent)
        db.session.commit()

        flash('Parent account created successfully.')
        return redirect(url_for('admin.list_parents'))

    return render_template('admin/create_user.html', form=form, title='Create Parent')
