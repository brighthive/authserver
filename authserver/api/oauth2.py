"""OAuth 2.0 API

An API for handling OAuth 2.0 interactions.

"""

import json
import requests
from datetime import datetime
from flask import Blueprint, request, session, render_template
from flask_restful import Resource, Api, request
from werkzeug.security import gen_salt
from authlib.flask.oauth2 import current_token
from authlib.oauth2 import OAuth2Error, OAuth2Request
from authlib.oauth2.rfc6749 import InvalidGrantError

from authserver.utilities import ResponseBody
from authserver.db import db, User, OAuth2Client
from authserver.utilities.oauth2 import authorization, require_oauth

oauth2_bp = Blueprint('oauth2_ep', __name__, template_folder='templates')


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


@oauth2_bp.route('/oauth/authorize', methods=['GET', 'POST'])
def authorize():
    user = current_user()
    if request.method == 'GET':
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error
        return render_template('authorize.html', user=user, grant=grant)
    if not user and 'username' in request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user:
            if password == 'password':
                if request.form['confirm']:
                    grant_user = user
                else:
                    grant_user = None
                return authorization.create_authorization_response(grant_user=grant_user)
            else:
                return render_template('authorize.html', user=user, grant=grant)
    else:
        return render_template('authorize.html')


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


class RedirectResource(Resource):
    """A User Resource.

    This resource defines an Auth Service user who may have zero or more OAuth 2.0 clients
    associated with their accounts.

    """

    def get(self):
        try:
            code = request.args.get('code')
        except Exception:
            code = None
        if code:
            foo = requests.get(request.base_url + 'http://localhost:8000/oauth/token')
            print(foo.status_code)
            return {'message': 'ok'}, 200


oauth2_api = Api(oauth2_bp)
oauth2_api.add_resource(CreateOAuth2TokenResource, '/oauth/token')
oauth2_api.add_resource(RevokeOAuth2TokenResource, '/oauth/revoke')
oauth2_api.add_resource(RedirectResource, '/redirect')
