from os import environ, path
from dotenv import load_dotenv

load_dotenv()

class DevConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SECRET_KEY = environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # FLASK_APP = '__init__.py'

class ProdConfig:
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL')
    SECRET_KEY = environ.get('SECRET_KEY')