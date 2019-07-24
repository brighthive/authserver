"""Test Fixtures"""

import pytest
from time import sleep
from flask_migrate import upgrade
from authserver import create_app
from authserver.utilities import PostgreSQLContainer
from authserver.config import ConfigurationFactory


@pytest.fixture
def client():
    """Setup the Flask application and return an instance of its test client.

    Returns:
        client (object): The Flask test client for the application.

    """
    app = create_app('TESTING')
    client = app.test_client()
    return client


@pytest.fixture
def app():
    """Setup the PostgreSQL database instance and return the Flask application.

    Returns:
        app (object): The Flask application.

    """
    app = create_app('TESTING')
    postgres = PostgreSQLContainer()
    postgres.start_container()
    upgraded = False

    while not upgraded:
        try:
            with app.app_context():
                upgrade()
                upgraded = True
        except Exception as e:
            sleep(1)
    yield app
    postgres.stop_container()


@pytest.fixture
def environments():
    return [
        'DEVELOPMENT',
        'TESTING',
        'STAGING',
        'SANDBOX',
        'PRODUCTION'
    ]
