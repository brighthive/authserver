import json
from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from expects import be_empty, equal, expect
from flask import Response, session

from authserver.db import User, db


USER_DATA = {
    "username": "greg_henry",
    "password": "passw0rd!",
    "role_id": None,
    "person_id": None,
    "can_login": True,
    "active": True
}


class TestLogin:
    def test_valid_user_login_with_redirect(self, client):
        user = User(**USER_DATA)
        db.session.add(user)

        response = client.post(
            '/', data={"username": "greg_henry", "password": "passw0rd!"})

        assert "<title>Redirecting...</title>" in str(response.data)

    def test_invalid_username_password(self, client):
        response = client.post(
            '/', data={"username": "not_a_username", "password": "invalid_password"})

        assert "You did not enter valid login credentials." in str(
            response.data)

    def test_user_can_login_as_false(self, client):
        USER_DATA["can_login"] = False
        user = User(**USER_DATA)
        db.session.add(user)

        response = client.post(
            '/', data={"username": "greg_henry", "password": "passw0rd!"})

        assert "You did not enter valid login credentials." in str(
            response.data)

    def test_user_active_as_false(self, client):
        USER_DATA["can_login"] = True
        USER_DATA["active"] = False
        user = User(**USER_DATA)
        db.session.add(user)

        response = client.post(
            '/', data={"username": "greg_henry", "password": "passw0rd!"})

        assert "You did not enter valid login credentials." in str(
            response.data)

    @pytest.mark.skip(reason=None)
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
