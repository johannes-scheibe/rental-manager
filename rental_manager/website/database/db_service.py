from .models import Guest, Flat, Booking, RentalAgreement
from flask import flash
from os import path
from . import db, DB_NAME
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

from datetime import datetime
import re
from ..util.pdf_creator import Agreement 
from configparser import ConfigParser

def insert_default_entries():
    try:        
        # default entries
        flat = Flat(name='Borkum')
        db.session.add(flat)

        flat = Flat(name='Baltrum')
        db.session.add(flat)

        flat = Flat(name='Langeoog')
        db.session.add(flat)

        flat = Flat(name='Memmert')
        db.session.add(flat)

        flat = Flat(name='Studio 1')
        db.session.add(flat)

        flat = Flat(name='Studio 2')
        db.session.add(flat)

        db.session.commit()
        
        flash('DB erfolgreich befüllt', category='success')
    except IntegrityError:
        pass

# Guests
def add_guest(prename, surname, email, street_name, house_number, postcode, city) -> bool:

    guest = Guest.query.filter_by(email=email, prename = prename, surname = surname).first()
    if guest:
        flash('Es existiert bereits ein Gast mit diesen Angaben.', category='error')
    elif len(email) < 4:
        flash('Die E-Mail muss mindestens eine Länge von 3 Zeichen besitzen.', category='error')
    elif len(prename) < 2:
        flash('Der Vorname muss mindestens eine Länge von 2 Zeichen besitzen.', category='error')
    elif len(surname) < 2:
        flash('Der Nachname muss mindestens eine Länge von 2 Zeichen besitzen', category='error')
    else:
        new_guest = Guest(prename=prename, surname=surname, email=email, street_name=street_name, house_number=house_number, postcode=postcode, city=city)
        db.session.add(new_guest)
        db.session.commit()
        flash('Gast erfolgreich erstellt!', category='success')
        return True
    return False

def get_guest_by_surname(surname) -> Guest:
    return Guest.query.filter_by(surname = surname).first()

def get_guest_by_id(id) -> Guest:
    return Guest.query.filter_by(id = id).first()

def get_all_guests() -> Guest:
    return Guest.query.all()

# Flat
def get_flat_by_id(id) -> Guest:
    return Flat.query.filter_by(id = id).first()


# Bookings
def add_booking(path, flat, guest_id, number_persons, number_pets, start_date, end_date, price) -> str:

    # check if flat exists
    flat = Flat.query.filter_by(name=flat).first()
    if flat:
        flat_id = flat.id
    else:
        flash('Die angegebene Wohnung existiert nicht.', category='error')
        return None

    # check if guest exists
    guest = Guest.query.filter_by(id=guest_id).first()
    if not guest:
        flash('Der angegebene Gast existiert nicht, bitte tragen Sie diesen erst ein.', category='error')
        return None

    # validate dates and convert to datetime
    start = validate_date(start_date)
    end = validate_date(end_date)
    if not start:
        return None
    if not end:
        return None
    
    # insert in db
    new_booking = Booking(flat_id=flat_id, guest_id=guest_id, number_persons=number_persons, number_pets=number_pets, start_date=start, end_date=end, price=price)
    db.session.add(new_booking)
    db.session.commit()
    flash('Buchung erfolgreich erstellt!', category='success')

    agreement = Agreement(new_booking)
    # Erstellen der Vereinbarung
    pdf = agreement.create_agreement()
    file_name = agreement.create_bill_name()
    parser = ConfigParser()
    parser.read('config.ini')
    file_path = str(path + file_name)
    pdf.output(file_path, 'F').encode('latin-1')
    add_agreement(new_booking.id, file_name)

    flash('PDF erfolgreich erstellt!', category='success')

    return file_name


def get_all_bookings():
    return Booking.query.all()

def validate_date(text):
    pattern = r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](20|21)\d\d'
    match = re.search(pattern, text)
    if match:
        date = match.group().replace('-', '.')
        try:
            return datetime.strptime(date, '%d.%m.%Y')
        except:
            flash('Das angegebene Datum existiert nicht', category='error')
            return False
    else:
        flash('Bitte das Datum in eine richtigen Format eingeben! (DD.MM.YYYY)', category='error')
        return False

# Rental agreements
def add_agreement(booking_id, file_name):
    new_agreement = RentalAgreement(booking_id=booking_id, file_name=file_name)
    db.session.add(new_agreement)
    db.session.commit()

def get_agreement_by_booking_id(booking_id) -> RentalAgreement:
    return RentalAgreement.query.filter_by(booking_id=booking_id).first()
