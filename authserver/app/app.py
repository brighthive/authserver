"""Flask Application."""

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from authserver.api import (client_bp, data_trust_bp, delete_client_secret_bp,
                            health_api_bp, oauth2_bp, role_bp,
                            rotate_client_secret_bp, user_bp)
from authserver.config import ConfigurationFactory
from authserver.db import db
from authserver.utilities import config_oauth


def create_app(environment: str = None):
    """Create the Flask application.

    Returns:
        obj: The configured Flask application context.

    """

    app = Flask(__name__)
    if environment is None:
        app.config.from_object(ConfigurationFactory.from_env())
    else:
        app.config.from_object(ConfigurationFactory.get_config(environment))
    app.config.update(
        SQLALCHEMY_DATABASE_URI=ConfigurationFactory.get_config(environment).sqlalchemy_database_uri
    )
    db.init_app(app)
    config_oauth(app)
    CORS(app)
    migrate = Migrate(app, db)
    app.register_blueprint(health_api_bp)
    app.register_blueprint(data_trust_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(delete_client_secret_bp)
    app.register_blueprint(rotate_client_secret_bp)
    app.register_blueprint(oauth2_bp)
    app.register_blueprint(role_bp)

    return app
