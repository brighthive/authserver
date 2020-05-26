"""Flask Application."""

from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from authserver.api import (client_bp, data_trust_bp, health_api_bp, oauth2_bp,
                            role_bp, user_bp, home_bp)
from authserver.config import ConfigurationFactory
from authserver.db import db
from authserver.utilities import config_oauth
from datetime import datetime as dt

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
        SQLALCHEMY_DATABASE_URI=ConfigurationFactory.get_config(
            environment).sqlalchemy_database_uri,
        OAUTH2_TOKEN_EXPIRES_IN={
            'authorization_code': 864000,
            'implicit': 3600,
            'password': 864000,
            'client_credentials': 60 * 5
        },
        SECRET_KEY=ConfigurationFactory.generate_secret_key()
    )

    @app.after_request
    def after_request(response):
        """ Logging every request. """
        print(request.remote_addr, dt.utcnow().strftime("%d/%b/%Y:%H:%M:%S.%f")[:-3],
            request.method, request.path, request.scheme.upper(), response.status,
            response.content_length, request.referrer, request.user_agent, flush=True)
        return response

    db.init_app(app)
    config_oauth(app)
    CORS(app)
    migrate = Migrate(app, db)
    app.register_blueprint(home_bp)
    app.register_blueprint(health_api_bp)
    app.register_blueprint(data_trust_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(oauth2_bp)
    app.register_blueprint(role_bp)

    return app
