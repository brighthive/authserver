"""Auth Server Database Models."""

import json
import time
from datetime import datetime, timedelta
from uuid import uuid4

import bcrypt
from authlib.integrations.sqla_oauth2 import (OAuth2AuthorizationCodeMixin,
                                              OAuth2ClientMixin,
                                              OAuth2TokenMixin)
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, pre_load, validate
from sqlalchemy import text as sa_text
from sqlalchemy.dialects.postgresql.json import JSONB


db = SQLAlchemy()
ma = Marshmallow()


roles = db.Table('roles',
                 db.Column('client_id', db.String, db.ForeignKey(
                     'oauth2_clients.id'), primary_key=True),
                 db.Column('role_id', db.String, db.ForeignKey('oauth2_roles.id'), primary_key=True))


class User(db.Model):
    """Data Trust User."""
    __tablename__ = 'users'
    __table_args__ = (db.UniqueConstraint('username'), )

    id = db.Column(db.String, primary_key=True)
    person_id = db.Column(db.String)
    username = db.Column(db.String(40), unique=True, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    can_login = db.Column(db.Boolean, nullable=True, default=False)
    role_id = db.Column(db.String, db.ForeignKey(
        'oauth2_roles.id'), nullable=True)
    role = db.relationship('Role', backref='users', lazy='subquery')
    password_hash = db.Column(db.String(128), nullable=False)
    date_created = db.Column(db.TIMESTAMP)
    date_last_updated = db.Column(db.TIMESTAMP)

    @property
    def password(self):
        raise AttributeError('Password cannot be read')

    @password.setter
    def password(self, password: str):
        self.password_hash = bcrypt.hashpw(password.encode(
            'utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify_password(self, password: str):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception as e:
            return False

    def get_user_id(self):
        return self.id

    def __init__(self, username, password, person_id=None, role_id=None, active=False, can_login=False):
        self.id = str(uuid4()).replace('-', '')
        self.username = username
        self.password = password
        self.person_id = person_id
        self.role_id = role_id
        self.active = active
        self.can_login = can_login
        self.date_created = datetime.utcnow()
        self.date_last_updated = datetime.utcnow()

    def __str__(self):
        return f"{self.id} {self.username}"


class JSONField(fields.Field):
    """A custom JSON field.

    """

    default_error_messages = {"invalid": "Not a valid JSON document."}

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return []
        return json.loads(json.dumps(value))

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return json.dumps(value, ensure_ascii=True)
        except Exception:
            return []


class Role(db.Model):
    """OAuth 2.0 Role."""

    __tablename__ = 'oauth2_roles'
    __table_args__ = (db.UniqueConstraint('role'), )

    id = db.Column(db.String, primary_key=True)
    role = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    rules = db.Column(JSONB)
    active = db.Column(db.Boolean)
    date_created = db.Column(db.TIMESTAMP)
    date_last_updated = db.Column(db.TIMESTAMP)

    def __init__(self, role, description, rules=None, active=True):
        self.id = str(uuid4()).replace('-', '')
        self.role = role
        self.description = description
        self.rules = rules
        self.active = active
        self.date_created = datetime.utcnow()
        self.date_last_updated = datetime.utcnow()

    def __str__(self):
        return self.id


class RoleSchema(ma.SQLAlchemySchema):
    """User Schema

    A marshmallow schema for validating the Role model.
    """

    class Meta:
        ordered = True
        model = Role

    id = ma.auto_field(dump_only=True)
    role = ma.auto_field(required=True)
    description = ma.auto_field(required=True)
    rules = ma.auto_field()
    active = ma.auto_field()
    date_created = ma.auto_field(dump_only=True)
    date_last_updated = ma.auto_field(dump_only=True)


class UserSchema(ma.SQLAlchemySchema):
    """User Schema

    A marshmallow schema for validating the User model.
    """

    class Meta:
        ordered = True
        model = User

    id = ma.auto_field(dump_only=True)
    username = ma.auto_field(required=True)
    password = fields.String(required=True)
    person_id = ma.auto_field()
    role_id = ma.auto_field()
    role = fields.Nested(RoleSchema(), dump_only=True)
    active = ma.auto_field()
    can_login = ma.auto_field()
    date_created = ma.auto_field(dump_only=True)
    date_last_updated = ma.auto_field(dump_only=True)


class OAuth2Client(db.Model, OAuth2ClientMixin):
    """OAuth 2.0 Client"""

    __tablename__ = 'oauth2_clients'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(
        db.String, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')
    roles = db.relationship('Role', secondary=roles, lazy='subquery',
                            backref=db.backref('clients', lazy=True))


class OAuth2ClientSchema(ma.SQLAlchemySchema):
    """Schema for OAuth 2.0 Client."""

    class Meta:
        ordered = True
        model = OAuth2Client

    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(required=True)
    client_id = ma.auto_field(dump_only=True)
    client_secret = ma.auto_field(dump_only=True)
    client_id_issued_at = ma.auto_field(dump_only=True)
    expires_at = fields.Integer(dump_only=True)
    redirect_uris = fields.List(fields.String())
    token_endpoint_auth_method = fields.String()
    grant_type = fields.String()
    response_type = fields.String()
    scope = fields.String()
    roles = fields.List(fields.String)
    client_name = fields.String(required=True)
    client_uri = fields.String()
    logo_uri = fields.String()
    contact = fields.String()
    tos_uri = fields.String()
    policy_uri = fields.String()
    jwks_uri = fields.String()
    i18n_metadata = fields.String()
    software_id = fields.String()
    software_version = fields.String()
    grant_types = fields.List(fields.String())
    response_types = fields.List(fields.String())
    contacts = fields.List(fields.String())
    jwks = fields.List(fields.String())


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    """OAuth 2.0 Authorization Code"""

    __tablename__ = 'oauth2_authorization_codes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')
    code_challenge = db.Column(db.VARCHAR())
    code_challenge_method = db.Column(db.VARCHAR())


class OAuth2Token(db.Model, OAuth2TokenMixin):
    """OAuth 2.0 Token"""

    __tablename__ = 'oauth2_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')

    def is_access_token_expired(self):
        expires_at = self.get_expires_at()
        return expires_at < time.time()

    def is_refresh_token_expired(self):
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at < time.time()


class AuthorizedClient(db.Model):
    """Clients authorized by a user.

    This class maintains a list of clients that a user has authorized to act on their behalf.

    """

    __tablename__ = 'authorized_clients'

    user_id = db.Column(db.String, db.ForeignKey('users.id'), primary_key=True)
    client_id = db.Column(db.String, primary_key=True)
    authorized = db.Column(db.Boolean, nullable=False, default=False)


class Scope(db.Model):
    """OAuth2 scopes associated with users and clients.

    This class provides an abstraction of an OAuth2 scope. The OAuth2Client entity has a scope
    field provided by its OAuth2ClientMixin class; however this level of abstraction is
    needed in order to expose this to clients in an easier way as well as to facilitate the linkage
    of scopes between clients and users.

    """

    __tablename__ = 'oauth2_scopes'
    __table_args__ = (db.UniqueConstraint('scope'), )

    id = db.Column(db.String, primary_key=True)
    scope = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String)
    date_created = db.Column(db.TIMESTAMP)
    date_last_updated = db.Column(db.TIMESTAMP)

    def __init__(self, scope, description):
        self.id = str(uuid4()).replace('-', '')
        self.scope = scope
        self.description = description
        self.date_created = datetime.utcnow()
        self.date_last_updated = datetime.utcnow()

    def __str__(self):
        return self.id


class ScopeSchema(ma.SQLAlchemySchema):
    """Scope schema

    A marshmallow schema for validating the Scope model.
    """

    class Meta:
        ordered = True
        model = Scope

    id = ma.auto_field(dump_only=True)
    scope = ma.auto_field(required=True)
    description = ma.auto_field(required=True)
    date_created = ma.auto_field(dump_only=True)
    date_last_updated = ma.auto_field(dump_only=True)


class AuthorizedScope(db.Model):
    """Map scopes to roles.

    This class links roles to scopes in order to provide a mapping of
    what scopes should be associated with a given user.

    """

    __tablename__ = 'authorized_scopes'
    role_id = db.Column(db.String, db.ForeignKey(
        'oauth2_roles.id'), nullable=False, primary_key=True)
    scope_id = db.Column(db.String, db.ForeignKey(
        'oauth2_scopes.id'), nullable=False, primary_key=True)
    role = db.relationship(
        'Role', backref='authorized_scopes', lazy='subquery')
    scope = db.relationship(
        'Scope', backref='authorized_scopes', lazy='subquery')
    date_created = db.Column(db.TIMESTAMP)
    date_last_updated = db.Column(db.TIMESTAMP)

    def __init__(self, role_id, scope_id):
        self.role_id = role_id
        self.scope_id = scope_id
        self.date_created = datetime.utcnow()
        self.date_last_updated = datetime.utcnow()

    def __str__(self):
        return f'{self.role_id} - {self.scope_id}'


class AuthorizedScopeSchema(ma.SQLAlchemySchema):
    """Scope schema

    A marshmallow schema for validating the AuthorizedScope model.
    """

    class Meta:
        ordered = True
        model = AuthorizedScope

    role_id = ma.auto_field(dump_only=True)
    scope_id = ma.auto_field(required=True)
    role = fields.Nested(RoleSchema(), dump_only=True)
    scope = fields.Nested(ScopeSchema(), dump_only=True)
    date_created = ma.auto_field(dump_only=True)
    date_last_updated = ma.auto_field(dump_only=True)


class PasswordRecovery(db.Model):
    """Password recovery nonce."""

    __tablename__ = 'password_recovery'
    nonce = db.Column(db.String, unique=True, nullable=False, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), primary_key=True)
    date_created = db.Column(db.TIMESTAMP)
    expiration_date = db.Column(db.TIMESTAMP)
    date_recovered = db.Column(db.TIMESTAMP)

    def __init__(self, nonce, user_id):
        self.nonce = nonce
        self.user_id = user_id
        self.date_created = datetime.utcnow()
        self.expiration_date = self.date_created + timedelta(hours=1)

    def is_expired(self):
        return datetime.utcnow() > self.expiration_date
