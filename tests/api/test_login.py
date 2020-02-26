import json
from flask import Response, session

import pytest
from unittest.mock import patch
from urllib.parse import urlencode
from expects import expect, equal, be_empty


@pytest.mark.skip(reason=None)
class TestLogin:
    def test_session_clear_after_consent(self, client, user):
        with client:
            # `session_transaction` provides a way to simulate a call to the current SecureCookieSession, allowing us to check or modify its value (before and after making an HTTP request)
            # https://flask.palletsprojects.com/en/0.12.x/testing/#accessing-and-modifying-sessions
            # https://github.com/pytest-dev/pytest-flask/issues/69
            with client.session_transaction() as session:
                # Update the SecureCookieSession
                session["id"] = user.id

            with client.session_transaction() as session:
                # Sanity check! Assert that SecureCookieSession has the correct key value
                expect(session["id"]).to(equal(user.id))

            form_data = urlencode({'consent': 'on'})
            response: Response = client.post(
                '/oauth/authorize',
                data=form_data,
                content_type="application/x-www-form-urlencoded"
            )

            with client.session_transaction() as session:
                # Assert that `authorize` cleared the session before redirecting
                expect(session).to(be_empty)
