"""Test Fixtures"""

import pytest
from authserver import create_app
from authserver.utilities import PostgreSQL


@pytest.fixture
def client():
    client = create_app().test_client()
    return client
