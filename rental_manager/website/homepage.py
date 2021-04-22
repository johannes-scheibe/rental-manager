from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, abort
from flask_login import login_required, current_user
from .database.models import Note
import json
from .database import db_service
from .database import db
from .util.pdf_creator import Agreement 
from configparser import ConfigParser
from flask import current_app as app

from os import path


homepage = Blueprint('homepage', __name__)

@homepage.route('/')
def home():
    
    return render_template("home.html")

@homepage.route('/init-db')
def init_db():
    db_service.insert_default_entries()
    return redirect(url_for('homepage.home'))