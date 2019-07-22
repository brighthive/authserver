"""Flask Application."""

from flask import Flask


def create_app(config=None):
    """Create the Flask application.

    Args:
        config (obj): An application configuration object.

    Returns:
        obj: The configured Flask application context.

    """
    app = Flask(__name__)

    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    return app
