"""Add superadmin column to client.

Revision ID: 631f37f8c085
Revises: c43ffe7b4001
Create Date: 2021-06-11 12:52:04.459481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '631f37f8c085'
down_revision = 'c43ffe7b4001'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('oauth2_clients', sa.Column('grant_super_admin', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('oauth2_clients', 'grant_super_admin')
