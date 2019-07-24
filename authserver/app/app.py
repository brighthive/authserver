"""Flask Application."""

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


from authserver.api import health_api_bp
from authserver.config import ConfigurationFactory


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
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    app.register_blueprint(health_api_bp)

    return app
