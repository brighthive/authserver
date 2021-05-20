"""Brighthive OAuth 2.0 Authorization Server.

"""

from authlib.integrations.flask_oauth2 import AuthorizationServer
from flask import request as flask_req
from authlib.oauth2 import OAuth2Request
from authlib.common.encoding import to_unicode
from authlib.oauth2.rfc6749 import InvalidGrantError, OAuth2Error

import jwt

from authserver.config import ConfigurationFactory
from datetime import datetime, timedelta
class BrighthiveJWT(object):
    def __init__(self):
        self.private_key = ConfigurationFactory.from_env().signature_key

    def generated_claims(self) -> object:
        return {
            "iss": "brighthive-authserver",
            "aud": [
                "brighthive-data-trust-manager",
                "brighthive-data-catalog-manager",
                "brighthive-governance-api",
                "brighthive-permissions-service",
                "brighthive-data-uploader-service"
                "brighthive-authserver"
            ],
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(24) # TODO: Set to now + 15 minutes
        }

    def make_jwt(self, json_claims: object) -> object:
        claims = self.generated_claims()
        claims.update(json_claims)

        jwt_token = jwt.encode(claims, self.private_key, algorithm='RS256')

        print(f'data {claims}')
        print(f'jwt_token {jwt_token}')

        return jwt_token


def generate_jwt(access_token):
    try:
        json_claims = {"brighthive-access-token": access_token, "brighthive-org-role": "???"}
        a_jwt = BrighthiveJWT().make_jwt(json_claims)
    except Exception as e:
        print('JWT exception', e)

    return a_jwt

class BrighthiveAuthorizationServer(AuthorizationServer):
    """Brighthive Authorization Server.

    Overrides the base Authlib AuthorizationServer class to provide a custom method
    for passing the OAuth 2.0 grant type as a field in the JSON request body, but still
    maintains the ability to handle the grant type as a query parameter.

    """

    def create_oauth2_request_from_json(self, request):
        """Build the OAuth2Request object from the JSON request body.

        Args:
            request (obj): The request object to parse for the necessary elements to build the OAuth2Request.

        Returns:
            (obj): The OAuth2Request object.

        """

        request_cls = OAuth2Request

        if isinstance(request, request_cls):
            return request

        if not request:
            request = flask_req

        # in case we cannot determine if the header is json, we hand the workload off to the base method.
        try:
            if request.headers['Content-Type'] != 'application/json':
                return self.create_authorization_request(request)
        except Exception:
            return self.create_oauth2_request(request)

        if request.method == 'POST':
            body = request.json
        else:
            body = None

        url = request.base_url
        if request.query_string:
            url = url + '?' + to_unicode(request.query_string)
        return request_cls(request.method, url, body, request.headers)

    def create_token_response(self, request=None):
        """Validate token request and create token response.

        Args:
            request (obj): OAuth2Request instance.

        Returns:
            (func): An error handler in the event of an InvalidGrantError or OAuth2Error.
        """
        request = self.create_oauth2_request_from_json(request)

        try:
            grant = self.get_token_grant(request)
        except InvalidGrantError as error:
            return self.handle_error_response(request, error)

        try:
            grant.validate_token_request()
            status, body, headers = grant.create_token_response()

            # TODO: Call permissions service with user id
            bh_jwt = generate_jwt(body['access_token'])
            body['jwt'] = bh_jwt

            # del body['access_token']

            return self.handle_response(status, body, headers)
        except OAuth2Error as error:
            return self.handle_error_response(request, error)
