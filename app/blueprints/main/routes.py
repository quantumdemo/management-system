from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.blueprints.main import bp
from app.models import User, Student, Teacher, Parent, SchoolClass, Subject, ClassTeacherSubjectLink

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html', title='Home')

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
