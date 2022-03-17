from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.schema import UniqueConstraint


class Base():
    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            attr = getattr(self, c.name)
            if isinstance(attr, Base):
                attr = attr.as_dict()
            d[c.name] = attr
        return d


class Profile(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Flat(Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    bookings = db.relationship('Booking')
    __table_args__ = (UniqueConstraint('name'),)


class Guest(Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    prename = db.Column(db.String(150))
    surname = db.Column(db.String(150))
    street_name = db.Column(db.String(150))
    house_number = db.Column(db.String(150))
    postcode = db.Column(db.Integer)
    city = db.Column(db.String(150))
    agreements = db.relationship('Booking')


class Booking(Base, db.Model):
    id = db.Column(db.String, primary_key=True)
    timestamp = db.Column(db.Integer)
    flat_id = db.Column(db.Integer, db.ForeignKey('flat.id'))
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.id'))
    number_persons = db.Column(db.Integer)
    number_pets = db.Column(db.Integer)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    price = db.Column(db.Float)
    booking_status = db.Column(db.Integer, default=0)
    payment_status = db.Column(db.Integer, default=0)
    tourist_tax_status = db.Column(db.Integer, default=0)


class RentalAgreement(Base, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer)

    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    file_name = db.Column(db.String(150))
