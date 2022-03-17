from pathlib import Path
import time
from flask import Blueprint, make_response, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, abort
from flask_login import login_required, current_user as current_profile
import json

from RentalManager.website.database.models import Booking, Flat, Guest
from .database import db_service
from flask import current_app as app
from datetime import datetime
import os


bookings = Blueprint('bookings', __name__)


@bookings.route('/bookings')
@login_required
def booking_overview():
    return render_template('booking_overview.html', profile=current_profile)

@bookings.route("/bookings/load")
@login_required
def load():
    time.sleep(0.2)  # Used to simulate delay
    
    guests = db_service.list_result_to_dict(db_service.get_guests())
    flats = db_service.list_result_to_dict(db_service.get_flats())
    
    if request.args:
        counter = int(request.args.get("c"))  # The 'counter' value sent in the QS
        quantity = int(request.args.get("q"))
        bookings = db_service.get_bookings(offset=counter, limit=counter+quantity, order_by=[Booking.id])
  
    data = []
    for item in bookings:
        item = item.as_dict()
        item['guest'] = guests[item['guest_id']].as_dict()
        item['flat'] = flats[item['flat_id']].as_dict()
        item['start_date'] = item['start_date'].strftime('%d.%m.%Y')
        item['end_date'] = item['end_date'].strftime('%d.%m.%Y')
        item['booking_status'] = app.config['BOOKING_STATES'][item['booking_status']]
        item['payment_status'] = app.config['PAYMENT_STATES'][item['payment_status']]
        item['tourist_tax_status'] = app.config['TOURIST_TAX_STATES'][item['tourist_tax_status']]
        data.append(item)

    return make_response(jsonify(data), 200)

@bookings.route("/bookings/search")
@login_required
def search():
    time.sleep(0.2)  # Used to simulate delay
        
    if request.args:
        filter = str(request.args.get("f"))
        print(filter)
    
        bookings = db_service.get_bookings(filter=filter, order_by=[Booking.id])
        guests = db_service.list_result_to_dict(db_service.get_guests())
        flats = db_service.list_result_to_dict(db_service.get_flats())
        data = []
        for item in bookings:
            item = item.as_dict()
            item['guest'] = guests[item['guest_id']].as_dict()
            item['flat'] = flats[item['flat_id']].as_dict()
            item['start_date'] = item['start_date'].strftime('%d.%m.%Y')
            item['end_date'] = item['end_date'].strftime('%d.%m.%Y')
            item['booking_status'] = app.config['BOOKING_STATES'][item['booking_status']]
            item['payment_status'] = app.config['PAYMENT_STATES'][item['payment_status']]
            item['tourist_tax_status'] = app.config['TOURIST_TAX_STATES'][item['tourist_tax_status']]
            data.append(item)

        return make_response(jsonify(data), 200)


@bookings.route('/bookings/show/<string:id>')
@login_required
def booking_details(id):
    booking = db_service.get_booking(id=id)
    guest = db_service.get_guest(id=booking.guest_id)
    flat = db_service.get_flat(id=booking.flat_id)

    return render_template('booking_details.html', profile=current_profile, guest=guest, booking=booking, flat=flat, booking_states = app.config['BOOKING_STATES'],payment_states = app.config['PAYMENT_STATES'], tourist_tax_states = app.config['TOURIST_TAX_STATES'])

@bookings.route('/bookings/form')
@login_required
def booking_form(data=None):
    guests = db_service.get_guests(order_by=[Guest.surname, Guest.prename])
    flats = db_service.get_flats(order_by=[Flat.name])
    return render_template('booking_form.html', profile=current_profile, data = data, guests = guests, flats = flats)

@bookings.route('/bookings/create', methods=['GET', 'POST'])
@bookings.route('/bookings/update/<string:id>', methods=['GET', 'POST'])
@login_required
def update_booking(id=None):
    if request.method == 'POST':
        data = {
            'guest_id' : request.form.get('guestId'),
            'flat_id' : request.form.get('flatId'),
            'number_persons' : request.form.get('numberPersons'),
            'number_pets' : request.form.get('numberPets'),
            'start_date' : request.form.get('startDate'),
            'end_date' : request.form.get('endDate'),
            'price' : request.form.get('price')
        }
        
        if id:
            booking = db_service.update_booking(id=id, **data)
            if booking:
                return redirect(url_for('bookings.booking_details', id=id)) 
        else:
            booking = db_service.add_booking(**data)
            if booking:
                return redirect(url_for('bookings.booking_overview')) 
        return booking_form(data)

    data = db_service.get_booking(id=id) if id else None
    return booking_form(data)

@bookings.route('/bookings/delete/<string:booking_id>')
@login_required
def delete_booking(booking_id):

    db_service.delete_booking(booking_id)
   
    return redirect('/bookings')

@bookings.route('/bookings/download/<string:booking_id>')
@login_required
def download_booking(booking_id):
    agreement = db_service.get_agreement(booking_id=booking_id)
    year = datetime.now().year
    path = Path(app.config['AGREEMENT_PATH']) / str(year)
    try:
        return send_from_directory(path, filename=agreement.file_name, as_attachment=True)
    except Exception as e:
        print(app.config['AGREEMENT_PATH'] + str(current_profile.profile_name) + '/' + agreement.file_name)
        return abort(404)

@bookings.route('/bookings/agreement/<string:booking_id>')
@login_required
def show_agreement(booking_id):
    agreement = db_service.get_agreement(booking_id=booking_id)
    year = booking_id.split('-')[1]
    try:
        return send_from_directory(app.config['AGREEMENT_PATH'] + str(current_profile.profile_name) + '/' + str(year) , filename=agreement.file_name, as_attachment=False)
    except Exception as e:
        print(e)
        return abort(404)

@bookings.route('/bookings/complete-task/<string:task>/<string:booking_id>')
@login_required       
def complete_task(task, booking_id):
    functions = {
        'booking-task': [booking_id, 'booking_status', len(app.config['BOOKING_STATES'])-1],
        'payment-task': [booking_id, 'payment_status', len(app.config['PAYMENT_STATES'])-1],
        'tourist-tax-task': [booking_id, 'tourist_tax_status', len(app.config['TOURIST_TAX_STATES'])-1]
    }

    db_service.increase_status(*functions[task])

    return redirect(url_for('bookings.booking_details', id=booking_id))

@bookings.route('/bookings/undo-task/<string:task>/<string:booking_id>')
@login_required       
def undo_task(task, booking_id):
    functions = {
        'booking-task': [booking_id, 'booking_status', 0],
        'payment-task': [booking_id, 'payment_status', 0],
        'tourist-tax-task': [booking_id, 'tourist_tax_status', 0]
    }

    db_service.decrease_status(*functions[task])

    return redirect(url_for('bookings.booking_details', id=booking_id))
