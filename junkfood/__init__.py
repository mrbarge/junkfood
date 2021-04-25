import os

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

# add DB
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
metrics = None


def create_app():
    global metrics
    app = Flask(__name__)

    if app.config['ENV'] == 'production':
        app.config.from_object('config.ProductionConfig')
    elif app.config['ENV'] == 'test':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    if 'APP_CONFIG_FILE' in os.environ:
        app.config.from_envvar('APP_CONFIG_FILE')

    from junkfood.models import Transcript

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    migrate.init_app(app, db)
    bootstrap = Bootstrap(app)

    with app.app_context():
        from junkfood.base import base_bp
        from junkfood.episode import episode_bp
        from junkfood.search import search_bp
        from junkfood.auth import auth_bp
        from junkfood.like import like_bp
        from junkfood.terms import term_bp

        # add blueprints
        app.register_blueprint(base_bp, url_prefix='/')
        app.register_blueprint(episode_bp, url_prefix='/episode')
        app.register_blueprint(search_bp, url_prefix='/search')
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(like_bp, url_prefix='/favourites')
        app.register_blueprint(term_bp, url_prefix='/terms')

        return app
