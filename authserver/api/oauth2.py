"""OAuth 2.0 API

An API for handling OAuth 2.0 interactions.

"""

import json
from datetime import datetime
from flask import Blueprint
from flask_restful import Resource, Api, request
from werkzeug.security import gen_salt
from authlib.flask.oauth2 import current_token
from authlib.oauth2 import OAuth2Error, OAuth2Request
from authlib.oauth2.rfc6749 import InvalidGrantError

from authserver.utilities import ResponseBody
from authserver.db import db, User, OAuth2Client
from authserver.utilities.oauth2 import authorization, require_oauth


class CreateOAuth2TokenResource(Resource):
    """A User Resource.

    This resource defines an Auth Service user who may have zero or more OAuth 2.0 clients
    associated with their accounts.

    """

    def post(self):
        return authorization.create_token_response()


class RevokeOAuth2TokenResource(Resource):
    """A User Resource.

    This resource defines an Auth Service user who may have zero or more OAuth 2.0 clients
    associated with their accounts.

    """

    def post(self):
        return authorization.create_endpoint_response('revocation')


class CreateOAuth2AuthorizationResource(Resource):
    """
    """

    def get(self):
        return authorization.create_authorization_response(grant_user=None)

    def post(self):
        return authorization.create_authorization_response(grant_user=None)


oauth2_bp = Blueprint('oauth2_ep', __name__)
oauth2_api = Api(oauth2_bp)
oauth2_api.add_resource(CreateOAuth2TokenResource, '/oauth/token')
oauth2_api.add_resource(RevokeOAuth2TokenResource, '/oauth/revoke')
oauth2_api.add_resource(CreateOAuth2AuthorizationResource, '/oauth/authorize')
