"""OAuth 2.0 Components.

This module makes use of Authlib to implement core services of AuthServer.

"""

from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.integrations.sqla_oauth2 import (
    create_query_client_func,
    create_save_token_func,
    create_revocation_endpoint,
    create_bearer_token_validator
)

from authlib.oauth2.rfc6749.errors import (
    UnauthorizedClientError,
    InvalidClientError,
    InvalidRequestError,
    AccessDeniedError,
)

from authlib.oauth2.rfc6749 import grants
from authlib.oauth2.rfc7636 import CodeChallenge
from authlib.integrations.flask_oauth2 import AuthorizationServer
from werkzeug.security import gen_salt
from authserver.oauth2 import BrighthiveAuthorizationServer, authenticate_client_secret_json
from authserver.db import db, User, OAuth2Client, OAuth2AuthorizationCode, OAuth2Token


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_basic', 'client_secret_post', 'none']

    def create_authorization_code(self, client, grant_user, request):
        code = gen_salt(48)
        code_challenge = request.data.get('code_challenge')
        code_challenge_method = request.data.get('code_challenge_method')
        item = OAuth2AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=grant_user.id,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method
        )
        db.session.add(item)
        db.session.commit()
        return code

    def parse_authorization_code(self, code, client):
        item = OAuth2AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id).first()
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        db.session.delete(authorization_code)
        db.session.commit()

    def authenticate_user(self, authorization_code):
        return User.query.get(authorization_code.user_id)


class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    def authenticate_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user.check_password(password):
            return user


class RefreshTokenGrant(grants.RefreshTokenGrant):
    def authenticate_refresh_token(self, refresh_token):
        token = OAuth2Token.query.filter_by(
            refresh_token=refresh_token).first()
        if token and not token.revoked and not token.is_refresh_token_expired():
            return token

    def authenticate_user(self, credential):
        return User.query.get(credential.user_id)


class ClientCredentialsGrant(grants.ClientCredentialsGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_json'
    ]


query_client = create_query_client_func(db.session, OAuth2Client)
save_token = create_save_token_func(db.session, OAuth2Token)
authorization = BrighthiveAuthorizationServer(
    query_client=query_client,
    save_token=save_token,
)
require_oauth = ResourceProtector()

# TODO: Verify: None of these need to be modified?
def config_oauth(app):
    authorization.init_app(app)
    authorization.register_client_auth_method(
        'client_secret_json', authenticate_client_secret_json)

    # supported grant types # TODO: grant.create_token_response() is calling this
    authorization.register_grant(ClientCredentialsGrant)
    authorization.register_grant(AuthorizationCodeGrant, [
                                 CodeChallenge(required=False)])

    # support revocation
    revocation_cls = create_revocation_endpoint(db.session, OAuth2Token)
    authorization.register_endpoint(revocation_cls)

    # protect resource
    bearer_cls = create_bearer_token_validator(db.session, OAuth2Token)
    require_oauth.register_token_validator(bearer_cls())
