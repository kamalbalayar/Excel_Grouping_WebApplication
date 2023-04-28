from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_session import Session, FileSystemSessionInterface
import os

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'anchde'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = './flask_session'
    app.config['SESSION_FILE_THRESHOLD'] = 500
    app.config['SESSION_FILE_MODE'] = 0o600
    app.config['SESSION_KEY_PREFIX'] = 'session:'

    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.makedirs(app.config['SESSION_FILE_DIR'])

    session_interface = FileSystemSessionInterface(app.config['SESSION_FILE_DIR'], threshold=app.config['SESSION_FILE_THRESHOLD'], mode=app.config['SESSION_FILE_MODE'], key_prefix=app.config['SESSION_KEY_PREFIX'])
    app.session_interface = session_interface

    db.init_app(app)

    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User

    with app.app_context():
        db.create_all()


    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    

    return app
    
def create_database(app):
     if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
