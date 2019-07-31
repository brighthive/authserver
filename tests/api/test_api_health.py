"""Unit tests for API Health Check"""

from expects import expect, be, have_key, equal
from flask import Response


class TestAPIHealth():
    def test_health_endpoint(self, client):
        """Ensure that the API is available and reachable."""
        response: Response = client.get('/health')
        body = response.json
        expect(response.status_code).to(be(200))
        expect(body).to(have_key('api_status'))
        expect(body['api_status']).to(equal('OK'))
