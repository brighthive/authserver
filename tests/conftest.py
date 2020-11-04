"""Test Fixtures"""

import json
import os
from time import sleep

import pytest
import requests
from flask import Response
from flask_migrate import upgrade

from authserver import create_app
from authserver.config import ConfigurationFactory
from authserver.db import User, db
from authserver.utilities import PostgreSQLContainer


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


@pytest.fixture(scope='session', autouse=True)
def app():
    """Setup the PostgreSQL database instance and return the Flask application.

    Returns:
        app (object): The Flask application.

    """
    os.environ['APP_ENV'] = 'TESTING'
    app = create_app('TESTING')

    is_jenkins = bool(int(os.getenv('IS_JENKINS_TEST', '0')))
    postgres = None

    if not is_jenkins:
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

    if not is_jenkins:
        postgres.stop_container()


# @pytest.fixture
# def user(client, organization):
#     '''
#     The migrations insert a User ("brighthive_admin") that relates to the "BrightHive" Organization.
#     This fixture simply finds and returns this user.
#     '''
#     user = User.query.filter_by(organization_id=organization.id).first()

#     return user


@pytest.fixture
def environments():
    return [
        'DEVELOPMENT',
        'TESTING',
        'STAGING',
        'SANDBOX',
        'PRODUCTION'
    ]
