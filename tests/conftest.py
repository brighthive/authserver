"""Test Fixtures"""

import pytest
from time import sleep
from flask_migrate import upgrade
from authserver import create_app
from authserver.utilities import PostgreSQLContainer
from authserver.config import ConfigurationFactory
from authserver.db import db
from authserver.db import db, DataTrust, User


@pytest.fixture(scope='session')
def data_trust(app):
    with app.app_context():
        data_trust = DataTrust(**{'data_trust_name': "trusty trust"})
        db.session.add(data_trust)
        db.session.commit()
        
        new_data_trust = DataTrust.query.filter_by(data_trust_name="trusty trust").first()
    return new_data_trust

@pytest.fixture(scope='session')
def user(app, data_trust):
    with app.app_context():
        user_data = {
            'username': 'test-user-1',
            'email_address': 'demo@me.com',
            'password': 'password',
            'firstname': 'David',
            'lastname': 'Michaels',
            'organization': 'BrightHive',
            'telephone': '304-555-1234',
            'data_trust_id': data_trust.id,
        }
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()

        new_user = User.query.filter_by(username="test-user-1").first()
    
    return user

@pytest.fixture(scope='session')
def client():
    """Setup the Flask application and return an instance of its test client.

    Returns:
        client (object): The Flask test client for the application.

    """
    app = create_app('TESTING')
    client = app.test_client()
    return client


@pytest.fixture(scope='session', autouse=True)
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
