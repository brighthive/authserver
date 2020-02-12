"""Custom authentication methods for authentication clients.

This module provides extensions to the standard client authentication methosds
provided by Authlib.

See: https://docs.authlib.org/en/latest/client/api.html#authlib.client.OAuth2Session.register_client_auth_method
See: https://docs.authlib.org/en/latest/specs/rfc6749.html

"""

import json
from flask import request as r
from authlib.oauth2.rfc6749 import InvalidClientError


def authenticate_client_secret_json(query_client, request):
    """Authenticate a client by extracting client details from a JSON request body."""

    data = r.json
    try:
        client_id = data['client_id']
        client_secret = data['client_secret']
        if client_id and client_secret:
            client = _validate_client(query_client, client_id, request.state)
            if client.check_token_endpoint_auth_method('client_secret_json') and client.check_client_secret(client_secret):
                return client
    except Exception:
        client_id = None
        client_secret = None


def _validate_client(query_client, client_id, state=None, status_code=400):
    if client_id is None:
        raise InvalidClientError(state=state, status_code=status_code)

    client = query_client(client_id)
    if not client:
        raise InvalidClientError(state=state, status_code=status_code)

    return client
