from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, abort
from flask_login import login_required, current_user as current_profile
import json
from app.database import db_service
from app.database import db
from app.utils.pdf_creator import Agreement 
from configparser import ConfigParser
from flask import current_app as app

from os import path


homepage = Blueprint('homepage', __name__)

@homepage.route('/')
@login_required
def home():
    return render_template("home.html", profile=current_profile)

@homepage.route('/sample-data')
def sample_data():
    db_service.insert_sample_data()
    return redirect(url_for('homepage.home'))