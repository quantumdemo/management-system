from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.blueprints.main import bp
from app.models import User, Student, Teacher, Parent, SchoolClass, Subject, ClassTeacherSubjectLink
from app.extensions import db
from app.forms import EditStudentProfileForm, EditTeacherProfileForm, EditParentProfileForm

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', title='Home')

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile/view_profile.html', title='Your Profile')

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Determine which form to use based on user role
    if current_user.role == 'student':
        form = EditStudentProfileForm(obj=current_user.student)
    elif current_user.role == 'teacher':
        form = EditTeacherProfileForm(obj=current_user.teacher)
    elif current_user.role == 'parent':
        form = EditParentProfileForm(obj=current_user.parent)
    else:
        flash('You do not have a profile to edit.')
        return redirect(url_for('main.dashboard'))

    if form.validate_on_submit():
        # The `obj` in the form constructor pre-populates the form,
        # but we need to update the model from the submitted form data.
        if current_user.role == 'student':
            profile = current_user.student
            profile.contact_phone = form.contact_phone.data
            profile.address = form.address.data
        elif current_user.role == 'teacher':
            profile = current_user.teacher
            profile.contact_phone = form.contact_phone.data
            profile.address = form.address.data
            profile.qualifications = form.qualifications.data
        elif current_user.role == 'parent':
            profile = current_user.parent
            profile.contact_phone = form.contact_phone.data
            profile.address = form.address.data

        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.profile'))

    return render_template('profile/edit_profile.html', title='Edit Profile', form=form)

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        student_count = Student.query.count()
        teacher_count = Teacher.query.count()
        parent_count = Parent.query.count()
        return render_template('dashboard_admin.html',
                               title='Admin Dashboard',
                               student_count=student_count,
                               teacher_count=teacher_count,
                               parent_count=parent_count)
    elif current_user.role == 'teacher':
        # This query is a bit more complex, we can refine it later
        teacher_links = current_user.teacher.class_subject_links
        return render_template('dashboard_teacher.html', title='Teacher Dashboard', links=teacher_links)
    elif current_user.role == 'student':
        student_profile = current_user.student
        return render_template('dashboard_student.html', title='Student Dashboard', student=student_profile)
    elif current_user.role == 'parent':
        parent_profile = current_user.parent
        return render_template('dashboard_parent.html', title='Parent Dashboard', parent=parent_profile)
    else:
        # Fallback for unknown roles or users without a role
        flash('Your role is not set. Please contact an administrator.')
        return redirect(url_for('auth.logout'))
