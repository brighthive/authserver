"""Auth Server Database Models."""

import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text as sa_text
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from uuid import uuid4
from authlib.flask.oauth2.sqla import OAuth2ClientMixin, OAuth2AuthorizationCodeMixin, OAuth2TokenMixin

db = SQLAlchemy()
ma = Marshmallow()


class DataTrust(db.Model):
    """Data Trust Model.

    The Data Trust is the highest-level entity of the auth server architecture.
    It represents a specific data trust that users can be assigned to in order
    to restrict their access to resources. The Data Trust entity is similar in
    effect to Auth0's tenant.

    """
    __tablename__ = 'data_trusts'
    __table_args__ = (db.UniqueConstraint('data_trust_name'), )
    id = db.Column(db.String, primary_key=True)
    data_trust_name = db.Column(db.String)
    date_created = db.Column(db.TIMESTAMP)
    date_last_updated = db.Column(db.TIMESTAMP)

    def __init__(self, data_trust_name):
        self.id = str(uuid4()).replace('-', '')
        self.data_trust_name = data_trust_name
        self.date_created = datetime.utcnow()
        self.date_last_updated = self.date_created

    def __str__(self):
        return self.data_trust_name


class DataTrustSchema(ma.Schema):
    """Data Trust Schema.

    A marshmallow schema for validating the Data Trust model.

    """
    class Meta:
        ordered = True

    id = fields.String(dump_only=True)
    data_trust_name = fields.String(required=True)
    date_created = fields.DateTime(dump_only=True)
    date_last_updated = fields.DateTime(dump_only=True)


class User(db.Model):
    """Data Trust User."""
    __tablename__ = 'users'
    __table_args__ = (db.UniqueConstraint('username'), )

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    organization = db.Column(db.String(120), nullable=False)
    email_address = db.Column(db.String(40), nullable=False)
    telephone = db.Column(db.String(20), nullable=True)
    data_trust_id = db.Column(db.String, db.ForeignKey('data_trusts.id', ondelete='CASCADE'), nullable=False)
    date_created = db.Column(db.TIMESTAMP)
    date_last_updated = db.Column(db.TIMESTAMP)

    def __init__(self, username, firstname, lastname, organization, email_address, data_trust_id, telephone=None):
        self.id = str(uuid4()).replace('-', '')
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.organization = organization
        self.email_address = email_address
        self.telephone = telephone
        self.data_trust_id = data_trust_id
        self.date_created = datetime.utcnow()
        self.date_last_updated = datetime.utcnow()

    def __str__(self):
        return '{} {} {}'.format(self.id, self.firstname, self.lastname)


class UserSchema(ma.Schema):
    """User Schema

    A marshmallow schema for validating the User model.
    """

    class Meta:
        ordered = True

    id = fields.String(dump_only=True)
    username = fields.String(required=True)
    firstname = fields.String(required=True)
    lastname = fields.String(required=True)
    organization = fields.String(required=True)
    email_address = fields.Email(required=True)
    telephone = fields.String()
    data_trust_id = fields.String(required=True)
    date_created = fields.DateTime(dump_only=True)
    date_last_updated = fields.DateTime(dump_only=True)


class OAuth2Client(db.Model, OAuth2ClientMixin):
    """OAuth 2.0 Client"""

    __tablename__ = 'oauth2_clients'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(
        db.String, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')


class OAuth2ClientSchema(ma.Schema):
    """Schema for OAuth 2.0 Client."""

    class Meta:
        ordered = True

    id = fields.String(dump_only=True)
    user_id = fields.String(required=True)
    client_id = fields.String(dump_only=True)
    client_secret = fields.String(dump_only=True)
    issued_at = fields.Integer(dump_only=True)
    expires_at = fields.Integer(dump_only=True)
    redirect_uri = fields.String()
    token_endpoint_auth_method = fields.String()
    grant_type = fields.String()
    response_type = fields.String()
    scope = fields.String()
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


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    """OAuth 2.0 Authorization Code"""

    __tablename__ = 'oauth2_authorization_codes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')


class OAuth2Token(db.Model, OAuth2TokenMixin):
    """OAuth 2.0 Token"""

    __tablename__ = 'oauth2_tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.String, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')

    def is_refresh_token_expired(self):
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at < time.time()
