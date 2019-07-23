"""Test Fixtures"""

import pytest
from authserver import create_app
from authserver.utilities import PostgreSQLContainer


@pytest.fixture
def client():
    client = create_app().test_client()
    return client


# @pytest.fixture
# def postgres():
#     postgres = PostgreSQLContainer()
#     return postgres


@pytest.fixture
def environments():
    return [
        'DEVELOPMENT',
        'TESTING',
        'STAGING',
        'SANDBOX',
        'PRODUCTION'
    ]
