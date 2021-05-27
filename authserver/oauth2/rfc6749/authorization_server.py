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
from authserver.db import OAuth2Token

import requests
from requests.structures import CaseInsensitiveDict
import os
import logging

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
            "exp": datetime.utcnow() + timedelta(24) # TODO: timedelta(minutes=15)
        }

    def make_jwt(self, json_claims: object) -> object:
        claims = self.generated_claims()
        claims.update(json_claims)

        jwt_token = jwt.encode(claims, self.private_key, algorithm='RS256')

        # logging.info(f'data {claims}')
        # logging.info(f'jwt_token: {jwt_token}')

        return jwt_token

def get_perms_for_user(person_id: str):
    # Get user perms
    permissions_api = ConfigurationFactory.from_env().permission_service_url

    get_user_perms_by_id = f'{permissions_api}/users/{person_id}/permissions'

    # Generate a token for Perms API
    super_admin_jwt = generate_jwt("none", {"brighthive-super-admin": True})

    # Make perms api call
    perm_headers = CaseInsensitiveDict()
    perm_headers["Accept"] = "application/json"
    perm_headers["Authorization"] = f"Bearer {super_admin_jwt}"

    logging.info('Authserver -> PermsAPI: Contacting...')

    perms_response = {}

    try:
        perms_response = requests.get(
            get_user_perms_by_id,
            headers=perm_headers)
        perms_response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        logging.exception(f'Authserver -> PermsAPI: HTTP Error: {http_err}')
    except Exception as err:
        logging.exception(f'Authserver -> PermsAPI: Uncaught error: {err}')
    else:
        logging.info('Authserver -> PermsAPI: Perms API call succeeded!')

    # TODO: handle the following errors
    # not enough permissions to make this request
    # invalid access token
    # invalid credentials
    # expired credentials
    # no user found

    # Extract user perms
    return perms_response.json()['response'].get('brighthive-platform-permissions') if perms_response else {}

def generate_jwt(access_token: str, claims: dict = {}, person_id: str='non provided'):
    if type(claims) is not dict:
        logging.warn('While trying to generate a JWT, the claims given were not a dict.')

    try:
        claims.update({"brighthive-access-token": access_token, "person-id": person_id})

        a_jwt = BrighthiveJWT().make_jwt(claims)
    except Exception:
        logging.exception('Uncaught exception when generating JWT.')
        return 'none'

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
            
            perms_for_user = {}

            if os.getenv('APP_ENV') == 'PRODUCTION':
                access_token = body['access_token']

                db_token = OAuth2Token.query.filter_by(access_token=access_token).first()
                user = db_token.user

                try:
                    person_id = user.person_id
                    perms_for_user = get_perms_for_user(person_id)
                except Exception as e:
                    logging.exception(f"person_id not found on user {user.username}!")

            bh_jwt = generate_jwt(body['access_token'], perms_for_user)
            body['jwt'] = bh_jwt

            # del body['access_token']

            return self.handle_response(status, body, headers)
        except OAuth2Error as error:
            return self.handle_error_response(request, error)
