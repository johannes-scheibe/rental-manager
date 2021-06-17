from .models import Guest, Flat, Booking, RentalAgreement
from flask import flash
import os
from . import db, DB_NAME
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_login import current_user as current_profile
from datetime import datetime
import re
from ..util.pdf_creator import Agreement 
from configparser import ConfigParser

def insert_default_entries():
    try:      
        # TODO dont accept duplicates  
        # default entries
        flat = Flat(profile_id=current_profile.id, name='Borkum')
        db.session.add(flat)

        flat = Flat(profile_id=current_profile.id, name='Baltrum')
        db.session.add(flat)

        flat = Flat(profile_id=current_profile.id, name='Langeoog')
        db.session.add(flat)

        flat = Flat(profile_id=current_profile.id, name='Memmert')
        db.session.add(flat)

        flat = Flat(profile_id=current_profile.id, name='Studio 1')
        db.session.add(flat)

        flat = Flat(profile_id=current_profile.id, name='Studio 2')
        db.session.add(flat)

        db.session.commit()
        
        flash('DB erfolgreich befüllt', category='success')
    except IntegrityError as e:
        print(e)
        pass

# Guests
def add_guest(data) -> bool:
    print(data)
    guest = Guest.query.filter_by(profile_id=current_profile.id, email=data['email'], prename = data['prename'], surname = data['surname']).first()
    if guest:
        flash('Es existiert bereits ein Gast mit diesen Angaben.', category='error')
    elif len(data['email']) < 4:
        flash('Die E-Mail muss mindestens eine Länge von 3 Zeichen besitzen.', category='error')
    elif len(data['prename']) < 2:
        flash('Der Vorname muss mindestens eine Länge von 2 Zeichen besitzen.', category='error')
    elif len(data['surname']) < 2:
        flash('Der Nachname muss mindestens eine Länge von 2 Zeichen besitzen', category='error')
    else:
        new_guest = Guest(profile_id=current_profile.id, prename=data['prename'], surname=data['surname'], email=data['email'], street_name=data['street_name'], house_number=data['house_number'], postcode=data['postcode'], city=data['city'])
        db.session.add(new_guest)
        db.session.commit()
        flash('Gast erfolgreich erstellt!', category='success')
        return True
    return False

def get_guest_by_surname(surname) -> Guest:
    return Guest.query.filter_by(profile_id=current_profile.id, surname=surname).first()

def get_guest_by_id(id) -> Guest:
    return Guest.query.filter_by(profile_id=current_profile.id,id=id).first()

def get_all_guests() -> Guest:
    return Guest.query.filter_by(profile_id=current_profile.id).all()

# Flat
def get_flat_by_id(id) -> Guest:
    return Flat.query.filter_by(profile_id=current_profile.id,id=id).first()


# Bookings
def add_booking(path, data) -> str:

    guest_id = data['guest_id']
    flat_id =data['flat_id']
    number_persons =data['number_persons']
    number_pets =data['number_pets']
    start_date =data['start_date']
    end_date =data['end_date']
    price =data['price']
    # check if flat exists
    flat = Flat.query.filter_by(profile_id=current_profile.id, id=flat_id).first()
    if not flat:
        flash('Die angegebene Wohnung existiert nicht.', category='error')
        return None

    # check if guest exists
    guest = Guest.query.filter_by(profile_id=current_profile.id, id=guest_id).first()
    if not guest:
        flash('Der angegebene Gast existiert nicht, bitte tragen Sie diesen erst ein.', category='error')
        return None

    # validate dates and convert to datetime
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    if not is_valid_period(start_date, end_date):
        flash('Der angegebene Zeitraum ist ungültig', category='error')
        return None

    # insert in db
    id = uid(Booking)
    new_booking = Booking(profile_id=current_profile.id, id=id, flat_id=flat_id, timestamp=timestamp(), guest_id=guest_id, number_persons=number_persons, number_pets=number_pets, start_date=start, end_date=end, price=price)
    db.session.add(new_booking)
    db.session.commit()
    flash('Buchung erfolgreich erstellt!', category='success')

    agreement = Agreement(new_booking)
    # Erstellen der Vereinbarung
    pdf = agreement.create_agreement()
    file_name = agreement.create_bill_name(id)
    parser = ConfigParser()
    parser.read('config.ini')
    year = datetime.now().year
    if not os.path.exists(path + str(year)):
        os.makedirs(path + str(year))
    file_path = str(path + str(year) + "/" + file_name)
    pdf.output(file_path, 'F').encode('latin-1')
    add_agreement(new_booking.id, file_name)

    flash('PDF erfolgreich erstellt!', category='success')

    return file_name


def delete_agreement(booking_id: int):
    bookings = Booking.query.filter_by(profile_id=current_profile.id, id=booking_id)
    if bookings.count() == 0:
        return None
    for b in bookings:
        agreement = RentalAgreement.query.filter_by(profile_id=current_profile.id, booking_id=b.id).first()
        db.session.delete(b)
        db.session.delete(agreement)
    db.session.commit() 
    return agreement


def get_all_bookings():
    return Booking.query.filter_by(profile_id=current_profile.id).order_by(Booking.timestamp.desc())


def is_valid_period(start_date, end_date):
    if start_date < end_date:
        return True
    return False


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
    new_agreement = RentalAgreement(profile_id=current_profile.id, booking_id=booking_id, timestamp=timestamp(), file_name=file_name)
    db.session.add(new_agreement)
    db.session.commit()

def get_agreement_by_booking_id(booking_id) -> RentalAgreement:
    return RentalAgreement.query.filter_by(profile_id=current_profile.id, booking_id=str(booking_id)).first()

def get_all_flats():
    return Flat.query.filter_by(profile_id=current_profile.id).all()

def uid(db_model):
    # Handle unique ids for all profiles
    last_entry = db_model.query.order_by(Booking.timestamp.desc()).first()
    if last_entry is None:
        running_number = 1
    else:
        running_number = int(last_entry.id.split("-")[0]) + 1
    return "{:03d}".format(running_number) + "-" + str(datetime.now().year)

def timestamp():
    return int(datetime.now().timestamp() * 1000)