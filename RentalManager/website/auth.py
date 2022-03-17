from flask import Blueprint, render_template, request, flash, redirect, url_for
from .database.models import Profile
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db
from flask_login import login_user as login_profile, login_required, logout_user as logout_profile, current_user as current_profile


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')

        profile = Profile.query.filter_by(name=name).first()
        if profile:
            if check_password_hash(profile.password, password):
                flash('Logged in successfully!', category='success')
                login_profile(profile, remember=True)
                return redirect(url_for('homepage.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Profile does not exist.', category='error')

    return render_template("login.html", profile=current_profile)


@auth.route('/logout')
@login_required
def logout():
    logout_profile()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        profile = Profile.query.filter_by(name=name).first()
        if profile:
            flash('Profile name already exists.', category='error')
        elif len(name) < 4:
            flash('Profile name must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 3:
            flash('Password must be at least 3 characters.', category='error')
        else:
            new_profile = Profile(name=name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_profile)
            db.session.commit()
            login_profile(new_profile, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('homepage.home'))

    return render_template("sign_up.html", profile=current_profile)