from flask import Blueprint, render_template, request, flash, redirect, url_for
from .database.models import Admin
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')

        admin = Admin.query.first()
        if admin:
            if check_password_hash(admin.password, password):
                flash('Logged in successfully!', category='success')
                login_user(admin, remember=True)
                return redirect(url_for('homepage.home'))
            else:
                flash('Incorrect password, try again.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
