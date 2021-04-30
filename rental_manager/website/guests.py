from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, abort
from flask_login import login_required, current_user
import json
from .database import db_service
from .database import db
from .util.pdf_creator import Agreement 
from configparser import ConfigParser
from flask import current_app as app

from os import path


guests = Blueprint('guests', __name__)

@guests.route('/guests')
def guest_overview():
    data = db_service.get_all_guests()
    return render_template("guest_overview.html", data=data)

@guests.route('/guests/<int:guest_id>')
def guest_profile(guest_id):
    guest = db_service.get_guest_by_id(guest_id)
    return render_template("guest_profile.html", guest=guest)


@guests.route('/add-guest', methods=['GET', 'POST'])
def add_guest():
    if request.method == 'POST':

        prename = request.form.get('prename')
        surname = request.form.get('surname')
        email = request.form.get('email')
        street_name = request.form.get('streetName')
        house_number = request.form.get('houseNumber')
        postcode = request.form.get('postcode')
        city = request.form.get('city')

        if db_service.add_guest(prename=prename, surname=surname, email=email, street_name=street_name, house_number=house_number, postcode=postcode, city=city):
            return redirect(url_for('guests.guest_overview'))
        
    return render_template("add_guest.html")
