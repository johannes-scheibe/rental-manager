import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

from app.database import db

from config import Config
from app.database.models import *
basedir = os.path.abspath(os.path.dirname(__file__))
def create_app(config_class=Config):
    
    if getattr(sys, 'frozen', False):
        template_folder = os.path.join(sys._MEIPASS, 'templates')
        app = Flask(__name__, template_folder=template_folder)
    else:
        app = Flask(__name__)
    
    # load config
    app.config.from_object(config_class)
    

    # init flask extensions
    db.init_app(app)

    # register blueprints
    from app.main.auth import auth
    app.register_blueprint(auth, url_prefix='/')

    from app.main.homepage import homepage
    app.register_blueprint(homepage, url_prefix='/')

    from app.main.guests import guests
    app.register_blueprint(guests, url_prefix='/')

    from app.main.bookings import bookings
    app.register_blueprint(bookings, url_prefix='/')


    from app.database.models import Database

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Database.query.get(int(id))

    create_database(app)

    return app


def create_database(app):
    with app.app_context():
        db.create_all()
        for name in app.config['FLATS']:
            if not bool(Flat.query.filter_by(name=name).first()):
                    flat = Flat(name=name)
                    db.session.add(flat)
            db.session.commit()
            print('Created Database!')

