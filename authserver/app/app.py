"""Flask Application."""

from operator import mod
from flask import Flask, g, request
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_injector import FlaskInjector

from datetime import datetime as dt

from authserver.api import (client_bp, health_api_bp, oauth2_bp,
                            role_bp, user_bp, home_bp,
                            scope_bp)

from authserver.modules import ConfigurationModule, GraphDatabaseModule
from authserver.config import ConfigurationFactory
from authserver.db import db
from authserver.utilities import config_oauth

import json
import os
import logging
from pprint import pformat
from elasticapm.contrib.flask import ElasticAPM


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

    is_testing = environment == 'TESTING'
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    @app.after_request
    def after_request(response):
        """ Logging every request. """
        if not is_testing:
            jsonstr = json.dumps({
                "remote_addr": request.remote_addr,
                "request_time": str(dt.utcnow()),
                "method": request.method,
                "path": request.path,
                "scheme": request.scheme.upper(),
                "statusCode": response.status_code,
                "status": response.status,
                "content_length": response.content_length,
                "user_agent": str(request.user_agent)
            })
            logging.info(jsonstr)
        return response

    if not is_testing:
        apm_enabled = bool(int(os.getenv('APM_ENABLED', '0')))
        if apm_enabled:
            app.config['ELASTIC_APM'] = {
                'SERVICE_NAME': 'authserver',
                'SECRET_TOKEN': os.getenv('APM_TOKEN', ''),
                'SERVER_URL': os.getenv('APM_HOSTNAME', ''),
            }
            apm = ElasticAPM(app)

    db.init_app(app)
    config_oauth(app)
    CORS(app)
    migrate = Migrate(app, db)
    app.register_blueprint(home_bp)
    app.register_blueprint(health_api_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(oauth2_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(scope_bp)

    FlaskInjector(app=app, modules=[ConfigurationModule, GraphDatabaseModule])

    return app
