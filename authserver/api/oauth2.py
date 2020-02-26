"""OAuth 2.0 API

An API for handling OAuth 2.0 interactions.

"""

import json
import requests
from datetime import datetime
from flask import Blueprint, request, session, render_template, redirect, url_for
from flask_restful import Resource, Api, request
from werkzeug.security import gen_salt
from authlib.integrations.flask_oauth2 import current_token
from authlib.oauth2 import OAuth2Error, OAuth2Request
from authlib.oauth2.rfc6749 import InvalidGrantError

from authserver.utilities import ResponseBody
from authserver.db import db, User, OAuth2Client, AuthorizedClient
from authserver.utilities.oauth2 import authorization, require_oauth

oauth2_bp = Blueprint('oauth2_ep', __name__,
                      static_folder='static', template_folder='templates', url_prefix='/oauth')


def _current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


def _store_client_authorization(client_id, user_id):
    authorized_client = AuthorizedClient()
    authorized_client.client_id = client_id
    authorized_client.user_id = user_id
    authorized_client.authorized = True
    db.session.add(authorized_client)
    db.session.commit()


def _clear_user_session():
    '''
    This function clears the Authserver user session.
    The `authorize` endpoint calls it, immediately before the redirect, since
    the authorized user no longer needs the Authserver UI.
    '''
    if 'id' in session:
        session.pop('id')


def _client_authorized(client_id, user_id):
    return AuthorizedClient.query.filter_by(user_id=user_id, client_id=client_id, authorized=True).count() > 0


@oauth2_bp.route('/authorize', methods=['GET', 'POST'])
def authorize():
    errors = None
    user = _current_user()
    if not user:
        client_id = request.args.get('client_id')
        return redirect(url_for('home_ep.login', client_id=client_id, return_to=request.url))

    if request.method == 'GET':
        try:
            grant = authorization.validate_consent_request(end_user=user)
        except OAuth2Error as error:
            return error.error

        # Determine if the user has already given the client consent to act on their behalf.
        client_id = request.args.get('client_id')
        if _client_authorized(client_id, user.id):
            _clear_user_session()
            return authorization.create_authorization_response(grant_user=user)
        else:
            return render_template('authorize.html', user=user, grant=grant, errors=errors)

    try:
        request.form['consent']
        client_id = request.args.get('client_id')
        _store_client_authorization(client_id, user.id)
    except KeyError:
        grant = authorization.validate_consent_request(end_user=user)
        errors = "Please read and agree to the below statement to continue."
        return render_template('authorize.html', user=user, grant=grant, errors=errors)

    if not user and 'username' in request.form:
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()

    _clear_user_session()

    return authorization.create_authorization_response(grant_user=user)


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


oauth2_api = Api(oauth2_bp)
oauth2_api.add_resource(CreateOAuth2TokenResource, '/token')
oauth2_api.add_resource(RevokeOAuth2TokenResource, '/revoke')
