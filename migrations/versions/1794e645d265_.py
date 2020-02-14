"""Seed AuthServer based on environment

Revision ID: 1794e645d265
Revises: 49bfe630a344
Create Date: 2020-02-12 17:37:49.538592

"""

import os
import sqlalchemy as sa
import bcrypt
from sqlalchemy.sql import table, column
from alembic import op
from datetime import datetime
from uuid import uuid4
from authserver import create_app


# revision identifiers, used by Alembic.
revision = '1794e645d265'
down_revision = '49bfe630a344'
branch_labels = None
depends_on = None

data_trust_table = table('data_trusts',
                         column('id', sa.String),
                         column('data_trust_name', sa.String),
                         column('date_created', sa.TIMESTAMP),
                         column('date_last_updated', sa.TIMESTAMP))

user_table = table('users',
                   column('id', sa.String),
                   column('username', sa.String),
                   column('firstname', sa.String),
                   column('lastname', sa.String),
                   column('organization', sa.String),
                   column('email_address', sa.String),
                   column('active', sa.Boolean),
                   column('data_trust_id', sa.String, sa.ForeignKey('data_trusts.id', ondelete='CASCADE')),
                   column('password_hash', sa.String),
                   column('date_created', sa.TIMESTAMP),
                   column('date_last_updated', sa.TIMESTAMP))


def hash_password(password: str):
    return bcrypt.hashpw(password.encode(
        'utf-8'), bcrypt.gensalt()).decode('utf-8')


def upgrade():
    environment = os.getenv('APP_ENV', None)
    data_trust_id = str(uuid4()).replace('-', '')
    admin_user_id = str(uuid4()).replace('-', '')
    if environment == 'TESTING':
        # Set up data trust
        op.bulk_insert(data_trust_table, [
            {
                'id': data_trust_id,
                'data_trust_name': 'Test Data Trust',
                'date_created': datetime.utcnow(),
                'date_last_updated': datetime.utcnow()
            }
        ])

        # Set up test user
        op.bulk_insert(user_table, [
            {
                'id': admin_user_id,
                'username': 'test_user',
                'firstname': 'Test',
                'lastname': 'User',
                'organization': 'BrightHive',
                'email_address': 'test_user@brighthive.net',
                'active': True,
                'data_trust_id': data_trust_id,
                'password_hash': hash_password('passw0rd'),
                'date_created': datetime.utcnow(),
                'date_last_updated': datetime.utcnow()
            }
        ])
    elif not environment:
        op.bulk_insert(data_trust_table, [
            {
                'id': data_trust_id,
                'data_trust_name': 'Sample Data Trust',
                'date_created': datetime.utcnow(),
                'date_last_updated': datetime.utcnow()
            }
        ])

        op.bulk_insert(user_table, [
            {
                'id': admin_user_id,
                'username': 'facet_admin',
                'firstname': 'Facet',
                'lastname': 'Administrator',
                'organization': 'BrightHive',
                'email_address': 'brighthive_admin@brighthive.net',
                'active': True,
                'data_trust_id': data_trust_id,
                'password_hash': hash_password('143DATATRUST341'),
                'date_created': datetime.utcnow(),
                'date_last_updated': datetime.utcnow()
            }
        ])


def downgrade():
    op.execute('DELETE FROM data_trusts CASCADE')
