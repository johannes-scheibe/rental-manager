from flask import Blueprint, render_template, request, flash, redirect, url_for
from .database.models import Database
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db
from flask_login import login_user, login_required, logout_user as logout_profile, current_user as current_profile


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')

        profile = Database.query.first()
        if profile:
            if check_password_hash(profile.password, password):
                flash('Logged in successfully!', category='success')
                login_user(profile, remember=True)
                return redirect(url_for('homepage.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Profile does not exist.', category='error')

    if len(Database.query.all()) == 0:
        return redirect(url_for('auth.setup'))
    return render_template("login.html", profile=current_profile)


@auth.route('/logout')
@login_required
def logout():
    logout_profile()
    return redirect(url_for('auth.login'))


@auth.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')


        passwords = Database.query.all()
        if len(passwords) > 0:
            flash('Already setup')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 3:
            flash('Password must be at least 3 characters.', category='error')
        else:
            new_profile = Database(password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_profile)
            db.session.commit()
            login_user(new_profile, remember=True)
            flash('Datenbankpasswort gesetzt!', category='success')
            return redirect(url_for('homepage.home'))

    return render_template("sign_up.html", profile=current_profile)