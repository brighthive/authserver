import pytest
from uuid import uuid4
import json
import time
from flask import Response
from expects import expect, be, equal, raise_error, be_above_or_equal, have_key

from authserver.db import db, OAuth2Token


class TestOAuth2Flows:
    def _get_access_token(self, client):
        body = {
            'client_id': 'd84UZXW7QcB5ufaVT15C9BtO',
            'client_secret': 'cTQfd67c5uN9df8g56U8T5CwbF9S0LDgl4imUDguKkrGSuzI',
            'grant_type': 'client_credentials'
        }
        headers = {'content-type': 'application/json'}
        response: Response = client.post('/oauth/token', data=json.dumps(body), headers=headers)

        return response.json

    def _validate_token(self, client, token):
        body = {'token': token}
        headers = {'content-type': 'application/json'}
        response: Response = client.post('/oauth/validate', data=json.dumps(body), headers=headers)
        
        return response.json["messages"]["valid"]

    def test_client_credentials_flow(self, client):
        """Test Client Credentials OAuth 2.0 flows.

        """
        response = self._get_access_token(client)

        expect(response).to(have_key('access_token'))
        expect(response['token_type']).to(equal('Bearer'))

    def test_non_existent_token(self, client):
        is_valid = self._validate_token(client, "i am a bad token")
        expect(is_valid).to(be(False))

    def test_expired_token(self, client, app):
        with app.app_context():
            access_token = str(uuid4()).replace("-", "")
            issued_at = int(time.time()) - 865000
            expires_in = 864000
            expired_token = OAuth2Token(access_token=access_token, issued_at=issued_at, expires_in=expires_in)

            db.session.add(expired_token)
            db.session.commit()

            is_valid = self._validate_token(client, access_token)
            expect(is_valid).to(be(False))

            db.session.delete(expired_token)
            db.session.commit()

    def test_valid_token(self, client, app):
        response = self._get_access_token(client)
        is_valid = self._validate_token(client, response['access_token'])
        expect(is_valid).to(be(True))
