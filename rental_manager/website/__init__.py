from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from .database import db, DB_NAME, db_service
from .database.models import Flat
import time

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Ddf3Dkf79s0'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    
    from .auth import auth
    from .homepage import homepage
    from .guests import guests
    from .bookings import bookings

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(homepage, url_prefix='/')
    app.register_blueprint(guests, url_prefix='/')
    app.register_blueprint(bookings, url_prefix='/')


    create_database(app)

    return app

def create_database(app):
    if not path.exists('website/database/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')