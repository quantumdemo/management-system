import random
import datetime
from flask import render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.blueprints.auth import bp
from app.forms import LoginForm, RegistrationForm, VerifyEmailForm
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        if not user.is_verified:
            flash('Your account is not verified. Please check your email for an OTP.')
            return redirect(url_for('auth.verify_email', email=user.email))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='student')
        user.set_password(form.password.data)

        # Generate and set OTP
        otp = str(random.randint(100000, 999999))
        user.otp_code_hash = generate_password_hash(otp)
        user.otp_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

        db.session.add(user)
        db.session.commit()

        # For now, we'll print the OTP to the console for debugging
        print(f"OTP for {user.email}: {otp}")
        flash('Registration successful! Please check your email for an OTP to verify your account.')
        return redirect(url_for('auth.verify_email', email=user.email))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    email = request.args.get('email')
    if not email:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.is_verified:
        flash('Your account is already verified. Please log in.')
        return redirect(url_for('auth.login'))

    form = VerifyEmailForm()
    if form.validate_on_submit():
        if user.otp_expiry < datetime.datetime.utcnow():
            flash('OTP has expired. Please request a new one.')
            return redirect(url_for('auth.verify_email', email=user.email))

        if check_password_hash(user.otp_code_hash, form.otp.data):
            user.is_verified = True
            user.otp_code_hash = None
            user.otp_expiry = None
            db.session.commit()
            flash('Your account has been successfully verified. Please log in.')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid OTP. Please try again.')

    return render_template('auth/verify_email.html', title='Verify Email', form=form, email=email)


@bp.route('/resend-otp')
def resend_otp():
    email = request.args.get('email')
    if not email:
        return redirect(url_for('main.index'))

    user = User.query.filter_by(email=email).first_or_404()
    if user.is_verified:
        flash('Your account is already verified. Please log in.')
        return redirect(url_for('auth.login'))

    # Generate and set new OTP
    otp = str(random.randint(100000, 999999))
    user.otp_code_hash = generate_password_hash(otp)
    user.otp_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    db.session.commit()

    # For now, we'll print the OTP to the console for debugging
    print(f"New OTP for {user.email}: {otp}")
    flash('A new OTP has been sent to your email.')
    return redirect(url_for('auth.verify_email', email=user.email))
