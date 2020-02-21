import pytest
import json
from flask import Response
from expects import expect, be, equal, raise_error, be_above_or_equal, have_key


class TestOAuth2Flows:
    def test_client_credentials_flow(self, client):
        """Test Client Credentials OAuth 2.0 flows.

        """
        body = {
            'client_id': 'd84UZXW7QcB5ufaVT15C9BtO',
            'client_secret': 'cTQfd67c5uN9df8g56U8T5CwbF9S0LDgl4imUDguKkrGSuzI',
            'grant_type': 'client_credentials'
        }
        headers = {'content-type': 'application/json'}
        response: Response = client.post('/oauth/token', data=json.dumps(body), headers=headers)
        expect(response.json).to(have_key('access_token'))
        expect(response.json['token_type']).to(equal('Bearer'))
