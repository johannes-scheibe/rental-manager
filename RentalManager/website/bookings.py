from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, abort
from flask_login import login_required, current_user as current_profile
import json
from .database import db_service
from .database import db
from .util.pdf_creator import Agreement 
from configparser import ConfigParser
from flask import current_app as app
from datetime import datetime
import os




bookings = Blueprint('bookings', __name__)


@bookings.route('/bookings')
@login_required
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
            "number_pets" : booking.number_pets,
            "start_date" : booking.start_date.strftime("%d.%m.%Y"),
            "end_date" : booking.end_date.strftime("%d.%m.%Y"),
            "price" : str(booking.price) + " €"
        }
        data.append(entry)
    return render_template("booking_overview.html", profile=current_profile, data=data)

@bookings.route('/create-booking', methods=['GET', 'POST'])
@login_required
def create_booking():
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
        
        # Check if no data is none
        for d in data.values():
            if d is None or d == "":
                guests = db_service.get_all_guests()
                flats = db_service.get_all_flats()
                flash("Bitte alle Felder ausfüllen")
                return render_template("create_booking.html", profile=current_profile, guests = guests, flats = flats, data = data)

        path = app.config["CLIENT_AGREEMENTS"] + str(current_profile.profile_name) + "/"
        file_name = db_service.add_booking(path=path, data=data)
        if file_name is not None:
            flash("Die Buchung wurde erfolgreich erstellt")
            redirect("/bookings") 

    data = {
            'guest_id' : "",
            'flat_id' : "",
            'number_persons' : "",
            'number_pets' : "",
            'start_date' : "",
            'end_date' : "",
            'price' : ""
        }
    guests = db_service.get_all_guests()
    flats = db_service.get_all_flats()
    return render_template("create_booking.html", profile=current_profile, guests = guests, flats = flats, data = data)




@bookings.route("/bookings/delete/<string:booking_id>")
@login_required
def delete(booking_id):
    print("Delete")
    if not os.path.exists(app.config["CLIENT_AGREEMENTS"] + str(current_profile.profile_name) + "/" + "deleted"):
        os.makedirs(app.config["CLIENT_AGREEMENTS"] + str(current_profile.profile_name) + "/" + "deleted")
    deleted_agreement = db_service.delete_agreement(booking_id)
    if deleted_agreement is not None:
        year = booking_id.split("-")[1]
        print(year)
        os.replace(os.path.join(app.config["CLIENT_AGREEMENTS"] + str(current_profile.profile_name) + "/", str(year), deleted_agreement.file_name), os.path.join(app.config["CLIENT_AGREEMENTS"] + str(current_profile.profile_name) + "/", "deleted", deleted_agreement.file_name))
        flash("Die Buchung wurde erfolgreich gelöscht", category='success')
    else:
        flash("Ein Fehler ist aufgetreten", category='error')
    return redirect("/bookings")

@bookings.route("/bookings/download/<string:booking_id>")
@login_required
def download(booking_id):
    agreement = db_service.get_agreement_by_booking_id(booking_id)
    year = datetime.now().year
    try:
        return send_from_directory(app.config["CLIENT_AGREEMENTS"] + str(current_profile.profile_name) + "/"  + str(year), filename=agreement.file_name, as_attachment=True)
    except Exception as e:
        print(app.config["CLIENT_AGREEMENTS"] + str(current_profile.profile_name) + "/" + agreement.file_name)
        return abort(404)
    return redirect("/bookings")

@bookings.route("/bookings/show/<string:booking_id>")
@login_required
def show(booking_id):
    agreement = db_service.get_agreement_by_booking_id(booking_id)
    year = booking_id.split("-")[1]
    try:
        return send_from_directory(app.config["CLIENT_AGREEMENTS"] + str(current_profile.profile_name) + "/" + str(year) , filename=agreement.file_name, as_attachment=False)
    except Exception as e:
        print(e)
        return abort(404)