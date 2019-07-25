"""Auth Server Database Models."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text as sa_text
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from uuid import uuid4

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

    def __init__(self, data_trust_name):
        self.id = str(uuid4()).replace('-', '')
        self.data_trust_name = data_trust_name

    def __str__(self):
        return self.data_trust_name


class DataTrustSchema(ma.Schema):
    """Data Trust Schema.

    A marshmallow schema for validating the Data Trust model.

    """
    class Meta:
        ordered = True

    id = fields.String()
    data_trust_name = fields.String(required=True)


class User(db.Model):
    """A Data Trust User.

    """
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

    def __init__(self, username, firstname, lastname, organization, email_address, telephone=None):
        self.id = str(uuid4()).replace('-', '')
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.organization = organization
        self.email_address = email_address
        self.telephone = telephone

    def __str__(self):
        return '{} {} {}'.format(self.id, self.firstname, self.lastname)
