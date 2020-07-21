"""Test Fixtures"""

import os
import pytest
import requests
import json
from time import sleep
from flask_migrate import upgrade
from authserver import create_app
from authserver.utilities import PostgreSQLContainer
from authserver.config import ConfigurationFactory
from authserver.db import db
from authserver.db import db, DataTrust, User, Organization


class TokenGenerator:
    def __init__(self):
        self.client_id = 'd84UZXW7QcB5ufaVT15C9BtO'
        self.client_secret = 'cTQfd67c5uN9df8g56U8T5CwbF9S0LDgl4imUDguKkrGSuzI'
        self.grant_type = 'client_credentials'
        self.headers = {'content-type': 'application/json'}

    def get_token(self, client):
        body = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': self.grant_type
        }
        response: Response = client.post('/oauth/token', data=json.dumps(body), headers=self.headers)
        return response.json['access_token']


@pytest.fixture(scope='session')
def token_generator():
    return TokenGenerator()


@pytest.fixture(scope='session')
def data_trust(app):
    with app.app_context():
        data_trust = DataTrust(**{'data_trust_name': "trusty trust"})
        db.session.add(data_trust)
        db.session.commit()

        new_data_trust = DataTrust.query.filter_by(data_trust_name="trusty trust").first()
    return new_data_trust


@pytest.fixture()
def organization(app):
    '''
    The migrations insert an instance of an Organization with name "BrightHive."
    This fixture simply finds and returns this organization.
    '''
    with app.app_context():
        organization = Organization.query.filter_by(name="BrightHive").first()
    
    return organization


@pytest.fixture()
def user(app, organization):
    '''
    The migrations insert a User ("brighthive_admin") that relates to the "BrightHive" Organization.
    This fixture simply finds and returns this user.
    '''
    with app.app_context():
        user = User.query.filter_by(organization_id=organization.id).first()

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
    os.environ['APP_ENV'] = 'TESTING'
    app = create_app('TESTING')

    is_jenkins = bool(int(os.getenv('IS_JENKINS_TEST', '0')))

    if is_jenkins != True:
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

    if is_jenkins != True:
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
