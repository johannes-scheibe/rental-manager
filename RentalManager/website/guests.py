from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, abort
from flask_login import login_required, current_user as current_profile
import json
from .database import db_service
from .database import db
from .util.pdf_creator import Agreement 
from configparser import ConfigParser
from flask import current_app as app

from os import path


guests = Blueprint('guests', __name__)

@guests.route('/guests')
@login_required
def guest_overview():
    data = db_service.get_all_guests()
    return render_template("guest_overview.html", profile=current_profile, data=data)

@guests.route('/guests/<int:guest_id>')
@login_required
def guest_profile(guest_id):
    guest = db_service.get_guest_by_id(guest_id)
    return render_template("guest_profile.html", profile=current_profile, guest=guest)


@guests.route('/add-guest', methods=['GET', 'POST'])
@login_required
def add_guest():
    if request.method == 'POST':
        data = {
            "prename" : request.form.get('prename'),
            "surname" : request.form.get('surname'),
            "email" : request.form.get('email'),
            "street_name" : request.form.get('streetName'),
            "house_number" : request.form.get('houseNumber'),
            "postcode" : request.form.get('postcode'),
            "city" : request.form.get('city')
        }

        # Check if no data is none
        for d in data.values():
            if d is None or d == "":
                guests = db_service.get_all_guests()
                flats = db_service.get_all_flats()
                flash("Bitte alle Felder ausfüllen")
                return render_template("add_guest.html", data=data)

        if db_service.add_guest(data = data):
            return redirect(url_for('guests.guest_overview'))
            
    data = {
        "prename" : "",
        "surname" : "",
        "email" : "",
        "street_name" : "",
        "house_number" : "",
        "postcode" : "",
        "city" : ""
    }    
    return render_template("add_guest.html", profile=current_profile, data=data)
