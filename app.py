from flask import Flask
import logging
from logging import Formatter, FileHandler
from cache_manager import cache

# extensions
from routes import routes

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
        
    if not app.debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(
            Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')

    return app

def register_extensions(app):
    """Register all Extensions
    This registers all the add-ons of the app,
    to be instantiated with the instance of the flask app
    Add your extensions to this functions e.g Mail

    :param app: Flask app instance
    :return: None
    :rtype: NoneType
    """

    routes(app)
    with app.app_context():
        cache.init_app(app)
