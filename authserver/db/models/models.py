"""Auth Server Database Models."""

import json
import time
from datetime import datetime
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


class Organization(db.Model):
    """Data Trust Organization."""
    __tablename__ = 'organizations'

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=False)
    url = db.Column(db.String)
    date_created = db.Column(db.TIMESTAMP)
    date_last_updated = db.Column(db.TIMESTAMP)

    def __init__(self, name, url=None):
        self.id = str(uuid4()).replace('-', '')
        self.name = name
        self.url = url
        self.date_created = datetime.utcnow()
        self.date_last_updated = datetime.utcnow()

    def __str__(self):
        return '{} - {}'.format(self.id, self.name)


class OrganizationSchema(ma.SQLAlchemySchema):
    """Organization Schema

    A marshmallow schema for validating the Organization model.
    """

    class Meta:
        ordered = True
        model = Organization

    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(required=True)
    url = ma.auto_field()
    date_created = ma.auto_field(dump_only=True)
    date_last_updated = ma.auto_field(dump_only=True)


class User(db.Model):
    """Data Trust User."""
    __tablename__ = 'users'
    __table_args__ = (db.UniqueConstraint('username'), )

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    organization = db.relationship(
        'Organization', backref='users', lazy='subquery')
    organization_id = db.Column(
        db.String, db.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    email_address = db.Column(db.String(40), nullable=False)
    telephone = db.Column(db.String(20), nullable=True)
    active = db.Column(db.Boolean, nullable=False, default=True)
    role_id = db.Column(db.String, db.ForeignKey('oauth2_roles.id'), nullable=True)
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

    def __init__(self, username, password, firstname, lastname, organization_id, email_address, role_id=None, telephone=None):
        self.id = str(uuid4()).replace('-', '')
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.organization_id = organization_id
        self.role_id = role_id
        self.email_address = email_address
        self.telephone = telephone
        self.date_created = datetime.utcnow()
        self.date_last_updated = datetime.utcnow()

    def __str__(self):
        return '{} {} {}'.format(self.id, self.firstname, self.lastname)


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
    firstname = ma.auto_field(required=True)
    lastname = ma.auto_field(required=True)
    organization_id = ma.auto_field(required=True)
    organization = fields.Nested(OrganizationSchema(), dump_only=True)
    role_id = ma.auto_field()
    role = fields.Nested(RoleSchema(), dump_only=True)
    email_address = ma.auto_field(required=True)
    telephone = ma.auto_field()
    active = ma.auto_field()
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


# class RoleAuthorization(db.Model):
#     """OAuth2 scopes associated with roles.

#     This class provides a linkage between a role and an associated OAuth2 scope. This allows for the grouping
#     of scopes by a specific role.

#     """

#     __tablename__ = 'role_authorizations'

#     role_id = db.Column()
