from typing import Dict, List, Union

from sqlalchemy import or_
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
from flask import current_app as app

# Guests
def add_guest(prename, surname, email, street_name, house_number, postcode, city) -> Guest:

    guest = Guest.query.filter_by(email=email, prename =prename, surname = surname).first()
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
        return new_guest
    
def update_guest(id, **kwargs) -> Guest:
    guest = Guest.query.filter_by(id=id).first()
    for key, value in kwargs.items():
        setattr(guest, key, value)
    db.session.commit()
    return guest

def get_guests(filter=None, offset=0, limit=None, order_by=[], **kwargs):
    if filter is None:
        return Guest.query.filter_by(**kwargs).order_by(*order_by).slice(offset,limit).all()
    filter = [c.ilike("%{}%".format(filter)) for c in Guest.__table__.columns]
    return Guest.query.filter_by(**kwargs).filter(or_(*filter)).order_by(*order_by).slice(offset,limit).all()
    

def get_guest(order_by=[], **kwargs):
    return Guest.query.filter_by(**kwargs).order_by(*order_by).first()


# Flat
def get_flats(filter=None, offset=0, limit=None, order_by=[], **kwargs):
    if filter is None:
        return Flat.query.filter_by(**kwargs).order_by(*order_by).slice(offset,limit).all()
    filter = [c.ilike("%{}%".format(filter)) for c in Flat.__table__.columns]
    return Flat.query.filter_by(**kwargs).filter(or_(*filter)).order_by(*order_by).slice(offset,limit).all()
    
def get_flat(order_by=[], **kwargs):
    return Flat.query.filter_by(**kwargs).order_by(*order_by).first()


# Bookings
def add_booking(flat_id, guest_id, number_persons, number_pets, start_date, end_date, price) -> Booking:
    # check if flat exists
    flat = Flat.query.filter_by(id=flat_id).first()
    if not flat:
        flash('Die angegebene Wohnung existiert nicht.', category='error')
        return None

    # check if guest exists
    guest = Guest.query.filter_by(id=guest_id).first()
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
    new_booking = Booking(id=id, flat_id=flat_id, timestamp=timestamp(), guest_id=guest_id, number_persons=number_persons, number_pets=number_pets, start_date=start, end_date=end, price=price)
    db.session.add(new_booking)
    db.session.commit()
    
    agreement = Agreement(new_booking)
    # Erstellen der Vereinbarung
    pdf = agreement.create_agreement()
    file_name = agreement.create_bill_name(id)
    parser = ConfigParser()
    parser.read('config.ini')
    year = datetime.now().year
    path = app.config['AGREEMENT_PATH']
    if not os.path.exists(path + str(year)):
        os.makedirs(path + str(year))
    file_path = str(path + str(year) + "/" + file_name)
    pdf.output(file_path, 'F').encode('latin-1')
    add_agreement(new_booking.id, file_name)

    return new_booking

def update_booking(id, **kwargs) -> Booking:
    booking = Booking.query.filter_by(id=id).first()
    for key, value in kwargs.items():
        if key == 'start_date' or key == 'end_date':
            value = datetime.strptime(value, '%Y-%m-%d')
        setattr(booking, key, value)
    db.session.commit()
    return booking

def increase_status(id, type, max):
    booking = Booking.query.filter_by(id=id).first()
    current_status = getattr(booking, type)
    if current_status < max:
        setattr(booking, type, current_status+1)
        db.session.commit()
        return booking

def decrease_status(id, type, min):
    booking = Booking.query.filter_by(id=id).first()
    current_status = getattr(booking, type)
    if current_status > min:
        setattr(booking, type, current_status-1)
        db.session.commit()
        return booking

def delete_booking(id: int) -> Agreement:
    bookings = Booking.query.filter_by(id=id)
    if bookings.count() == 0:
        return None
    for booking in bookings:
        agreement = RentalAgreement.query.filter_by(booking_id=booking.id).first()
        db.session.delete(booking)
        db.session.delete(agreement)
    db.session.commit() 

    if not os.path.exists(app.config['AGREEMENT_PATH'] + 'deleted'):
        os.makedirs(app.config['AGREEMENT_PATH'] + 'deleted')
    
    if agreement is not None:
        
        os.replace(os.path.join(app.config['AGREEMENT_PATH'], str(booking.timestamp.year), agreement.file_name), os.path.join(app.config['AGREEMENT_PATH'], 'deleted', agreement.file_name))
    else:
        flash('Ein Fehler ist aufgetreten', category='error')
    return agreement

def get_bookings(filter=None, offset=0, limit=None, order_by=[], **kwargs):
    if filter is None:
        return Booking.query.filter_by(**kwargs).order_by(*order_by).slice(offset,limit).all()


    filter_list = []
    for c in Booking.__table__.columns:
        if c.type == str:
            filter_list.append(c.ilike("%{}%".format(filter)))
        else:
            filter_list.append(c == filter)
    
    #filter = [c.ilike("%{}%".format(filter)) for c in Booking.__table__.columns]
    return Booking.query.filter_by(**kwargs).filter(or_(*filter_list)).order_by(*order_by).slice(offset,limit).all()

def get_booking(order_by=[], **kwargs):
    return Booking.query.filter_by(**kwargs).order_by(*order_by).first()


# Rental agreements
def add_agreement(booking_id, file_name):
    new_agreement = RentalAgreement(booking_id=booking_id, timestamp=timestamp(), file_name=file_name)
    db.session.add(new_agreement)
    db.session.commit()

def get_agreements(filter=None, offset=0, limit=None, order_by=[], **kwargs):
    if filter is None:
        return RentalAgreement.query.filter_by(**kwargs).order_by(*order_by).slice(offset,limit).all()
    filter = [c.ilike("%{}%".format(filter)) for c in RentalAgreement.__table__.columns]
    return RentalAgreement.query.filter_by(**kwargs).filter(or_(*filter)).order_by(*order_by).slice(offset,limit).all()

def get_agreement(order_by=[], **kwargs):
    return RentalAgreement.query.filter_by(**kwargs).order_by(*order_by).first()



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

def list_result_to_dict(result):
    return {r.id : r for r in result}

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


def insert_sample_data():
    from flask import current_app as app
    try:      
        # TODO dont accept duplicates  
        # default entries
        guest = Guest(prename='Max', surname='Mustermann', email='test@gmail.com', street_name='Straße', house_number='1a', postcode='11888', city='Stadthausen')
        db.session.add(guest)
        db.session.commit()
        for _ in range(100):
            data = {
                'guest_id': guest.id,
                'flat_id': 1,
                'number_persons': 2,
                'number_pets': 0,
                'start_date': '2022-10-10',
                'end_date': '2022-10-17',
                'price': 1000
            }
            add_booking(**data)
               
        db.session.commit()
        
        flash('DB erfolgreich befüllt', category='success')
    except IntegrityError as e:
        print(e)
        pass


