"""Auth Server Database Models."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text as sa_text
from uuid import uuid4

db = SQLAlchemy()


class DataTrust(db.Model):
    __tablename__ = 'data_trust'
    __table_args__ = (db.UniqueConstraint('data_trust_name'), )
    id = db.Column(db.String, primary_key=True)
    data_trust_name = db.Column(db.String)

    def __init__(self, data_trust_name):
        self.id = str(uuid4()).replace('-', '')
        self.data_trust_name = data_trust_name
