from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

from RentalManager.website.database.models import Flat
from .database import db, DB_NAME


def create_app():
    app = Flask(__name__)

    # load config
    app.config.from_object("config.Config")
    db.init_app(app)


    
    from .auth import auth
    from .homepage import homepage
    from .guests import guests
    from .bookings import bookings

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(homepage, url_prefix='/')
    app.register_blueprint(guests, url_prefix='/')
    app.register_blueprint(bookings, url_prefix='/')

    from .database.models import Database

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Database.query.get(int(id))

    create_database(app)
    return app


def create_database(app):
    if not path.exists(app.config['DB_PATH'] + app.config['DB_NAME'] + '.db'):
        with app.app_context():
            db.create_all(app=app)

            for name in app.config['FLATS']:
                if not bool(Flat.query.filter_by(name=name).first()):
                    flat = Flat(name=name)
                    db.session.add(flat)
            db.session.commit()
            print('Created Database!')