"""Flask Application."""

from flask import Flask
from flask_restful import Api

from authservice.api import health_api_bp


def create_app(config=None):
    """Create the Flask application.

    Args:
        config (obj): An application configuration object.

    Returns:
        obj: The configured Flask application context.

    """
    app = Flask(__name__)
    api = Api(app)

    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)
    app.register_blueprint(health_api_bp)

    return app
