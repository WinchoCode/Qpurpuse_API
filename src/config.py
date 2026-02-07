import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    """"Basic configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwtsecretkey'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    API_TITLE = "Qpurpose API"
    API_VERSION = "v0.0.0"
    OPENAPI_VERSION = "3.0.3"

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}