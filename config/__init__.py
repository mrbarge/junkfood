import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    if 'SECRET_KEY' in os.environ:
        SECRET_KEY = os.environ['SECRET_KEY']
    if 'DATABASE_URI' in os.environ:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URI']


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'development'


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SECRET_KEY = 'testing'
    WTF_CSRF_ENABLED = False
    CSRF_ENABLED = False
