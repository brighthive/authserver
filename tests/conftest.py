"""Test Fixtures"""

import pytest
from authservice import create_app


@pytest.fixture
def client():
    client = create_app().test_client()
    return client
