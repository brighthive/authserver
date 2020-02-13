"""Seed AuthServer based on environment

Revision ID: 1794e645d265
Revises: 49bfe630a344
Create Date: 2020-02-12 17:37:49.538592

"""

import os
import sqlalchemy as sa
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


def upgrade():
    environment = os.getenv('APP_ENV', None)
    data_trust_id = str(uuid4()).replace('-', '')
    if environment == 'TESTING':
        op.bulk_insert(data_trust_table, [
            {
                'id': data_trust_id,
                'data_trust_name': 'Test Data Trust',
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


def downgrade():
    op.execute('DELETE FROM data_trusts CASCADE')
