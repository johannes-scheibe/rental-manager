from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func



class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(150))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flat_id = db.Column(db.Integer, db.ForeignKey('flat.id'))
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'))
    number_persons = db.Column(db.Integer)
    number_pets = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    price = db.Column(db.Float)
    
class Flat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique= True)
    bookings = db.relationship('Booking')

class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    prename = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    street_name = db.Column(db.String(150))
    house_number = db.Column(db.String(150))
    postcode = db.Column(db.Integer)
    city = db.Column(db.String(150))
    agreements = db.relationship('Booking')



class RentalAgreement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    file_name = db.Column(db.String(150))


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')