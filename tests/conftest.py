"""Test Fixtures"""

import json
import os
from time import sleep, time
from uuid import uuid4

import pytest
import requests
from flask import Response
from flask_migrate import upgrade
from werkzeug.security import gen_salt

from authserver import create_app
from authserver.config import ConfigurationFactory
from authserver.db import db, User, OAuth2Client, OAuth2Token
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
        response: Response = client.post(
            '/oauth/token', data=json.dumps(body), headers=self.headers)
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


@pytest.fixture
def environments():
    return [
        'DEVELOPMENT',
        'TESTING',
        'STAGING',
        'SANDBOX',
        'PRODUCTION'
    ]


@pytest.fixture
def user():
    data = {
        "username": "greg_henry",
        "password": "passw0rd!",
        "can_login": True,
        "active": True
    }
    user = User(**data)

    db.session.add(user)

    return user


@pytest.fixture
def oauth_client(user):
    data = {
        "id": str(uuid4()).replace('-', ''),
        "user_id": user.id,
        "client_id": gen_salt(24),
        "client_secret": gen_salt(48)
    }
    oauth_client = OAuth2Client(**data)

    db.session.add(oauth_client)

    return oauth_client


@pytest.fixture
def oauth_token(user):
    data = {
        "access_token": str(uuid4()).replace("-", ""),
        "issued_at": int(time()) - 865000,
        "expires_in": 965000,
        "user_id": user.id
    }
    token = OAuth2Token(**data)

    db.session.add(token)

    return token
