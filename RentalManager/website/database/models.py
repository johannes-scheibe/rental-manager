from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func



class Profile(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    profile_name = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    flats = db.relationship('Flat')
    bookings = db.relationship('Booking')
    guests = db.relationship('Guest')
    settings = db.relationship('Settings')
    agreements = db.relationship('RentalAgreement')
    
class Flat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    name = db.Column(db.String(50), unique= True)
    bookings = db.relationship('Booking')

class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    email = db.Column(db.String(150))
    prename = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    street_name = db.Column(db.String(150))
    house_number = db.Column(db.String(150))
    postcode = db.Column(db.Integer)
    city = db.Column(db.String(150))
    agreements = db.relationship('Booking')

class Booking(db.Model):
    id = db.Column(db.String, primary_key=True)
    timestamp = db.Column(db.Integer)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    flat_id = db.Column(db.Integer, db.ForeignKey('flat.id'))
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'))
    number_persons = db.Column(db.Integer)
    number_pets = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    price = db.Column(db.Float)

class RentalAgreement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    file_name = db.Column(db.String(150))

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    backup_path = db.Column(db.String(150))