import os
from pathlib import Path

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'super duper secret key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


    FLATS = ["Memmert", "Borkum", "Kajo"]
    DOC_PATH = Path(basedir) / "documents"
    BOOKING_STATES = ["angefragt", "reserviert"]
    PAYMENT_STATES = ["offen", "Anzahlung", "bezahlt"]
    TOURIST_TAX_STATES = ["offen", "bezahlt"]