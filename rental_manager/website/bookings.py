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


bookings = Blueprint('bookings', __name__)


@bookings.route('/bookings')
def booking_overview():
    data = []
    bookings = db_service.get_all_bookings()

    for booking in bookings:
        guest = db_service.get_guest_by_id(booking.guest_id)
        flat = db_service.get_flat_by_id(booking.flat_id)
        entry = {
            "id" : booking.id,
            "flat" : flat.name,
            "guest" : guest.prename + " " + guest.surname,
            "number_persons" : booking.number_persons,
            "number_pets" : booking.number_persons,
            "start_date" : booking.start_date.strftime("%d.%m.%Y"),
            "end_date" : booking.end_date.strftime("%d.%m.%Y"),
            "price" : str(booking.price) + " €"
        }
        data.append(entry)
    return render_template("booking_overview.html", data=data)

@bookings.route('/create-booking', methods=['GET', 'POST'])
def create_booking():
    if request.method == 'POST':
        guest = request.form.get('guest')
        flat = request.form.get('flat')
        number_persons = request.form.get('numberPersons')
        number_pets = request.form.get('numberPets')
        start_date = request.form.get('startDate')
        end_date = request.form.get('endDate')
        price = request.form.get('price')
        
        guest = db_service.get_guest_by_surname(guest)
        if guest is not None:
            path = app.config["CLIENT_AGREEMENTS"]
            print(path)
            file_name = db_service.add_booking(path= path, flat=flat, guest_id=guest.id, number_persons=number_persons, number_pets=number_pets, start_date=start_date, end_date=end_date, price=price)
            if file_name is not None:
                try:
                    return send_from_directory(path, filename=file_name, as_attachment=True)
                except Exception as e:
                    return abort(404)
        else:
            flash("Der angegebene Gast existiert nicht, bitte tragen Sie diesen erst ein.", category='error')

    guests = db_service.get_all_guests()
    flats = db_service.get_all_flats()
    return render_template("create_booking.html", guests = guests, flats = flats)


@bookings.route("show-agreement/<int:booking_id>")
def show_agreement(booking_id):
    agreement = db_service.get_agreement_by_booking_id(booking_id)
    print(agreement)
    try:
        return send_from_directory(app.config["CLIENT_AGREEMENTS"], filename=agreement.file_name, as_attachment=False)
    except Exception as e:
        print(e)
        #print(agreement.file_name)
        return abort(404)

@bookings.route("/search/<string:box>")
def search(box):
    query = request.args.get('query')
    suggestions = []
    if box == 'guest':
        data = db_service.get_all_guests() 
        for entry in data:
            suggestions.append({'value': entry.prename,'text': entry.surname})
        
    if box == 'flat':
        suggestions = [{'value': 'song1','data': '123'}, {'value': 'song2','data': '234'}]
    return jsonify({"suggestions":suggestions})

@bookings.route("/delete/<int:booking_id>")
def delete(booking_id):
    if db_service.delete_agreement(booking_id):
        flash("Die Buchung wurde erfolgreich gelöscht", category='success')
    else:
        flash("Ein Fehler ist aufgetreten", category='error')
    return redirect("/bookings")