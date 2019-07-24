"""Test Fixtures"""

import pytest
from authserver import create_app
from authserver.utilities import PostgreSQLContainer
from authserver.config import ConfigurationFactory


@pytest.fixture
def client():
    client = create_app('TESTING').test_client()
    return client


@pytest.fixture
def postgres():
    postgres = PostgreSQLContainer()
    postgres.start_container()
    yield postgres
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
