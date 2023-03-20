import time
from flask import Blueprint, make_response, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, abort
from flask_login import login_required, current_user as current_profile
import json
from app.database import db_service
from app.database import db
from app.utils.pdf_creator import Agreement 
from configparser import ConfigParser
from flask import current_app as app
from app.database.models import Guest

from os import path


guests = Blueprint('guests', __name__)

@guests.route('/guests')
@login_required
def guest_overview():
    data = db_service.get_guests(order_by=[Guest.surname, Guest.prename])
    return render_template("guest_overview.html", profile=current_profile, data=data)

@guests.route("/guests/load")
@login_required
def load():
    time.sleep(0.2)  # Used to simulate delay
        
    if request.args:
        counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
        quantity = int(request.args.get("q"))
        guests = db_service.get_guests(offset=counter, limit=counter+quantity, order_by=[Guest.id])

    data = [guest.as_dict() for guest in guests]

    return make_response(jsonify(data), 200)

@guests.route("/guests/search")
@login_required
def search():
      
    if request.args:
        filter = str(request.args.get("f"))
        guests = db_service.get_guests(filter=filter, order_by=[Guest.id])
  
    data = [guest.as_dict() for guest in guests]
    return make_response(jsonify(data), 200)

@guests.route('/guests/show/<int:guest_id>')
@login_required
def guest_details(guest_id):
    guest = db_service.get_guest(id=guest_id)
    

    bookings = (db_service.get_bookings(guest_id=guest_id))
    flats = db_service.list_result_to_dict(db_service.get_flats())
    return render_template("guest_details.html", profile=current_profile, guest=guest, bookings=bookings, flats=flats)

@guests.route('/guests/form')
@login_required
def guest_form(data=None):
    return render_template('guest_form.html', profile=current_profile, data = data)


@guests.route('/guests/create', methods=['GET', 'POST'])
@guests.route('/guests/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_guest(id=None):
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

        if id:
            guest = db_service.update_guest(id=id, **data)
            if guest:
                return redirect(url_for('guests.guest_details', id=id)) 
        else:
            guest = db_service.add_guest(**data)
            if guest:
                return redirect(url_for('guests.guest_overview'))
        return guest_form(data)

    data = db_service.get_guest(id=id) if id else None
    return guest_form(data)

