"""empty message

Revision ID: 35f1e31ceb30
Revises: a82b1a6ec9ad
Create Date: 2019-09-03 16:51:09.849694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35f1e31ceb30'
down_revision = 'a82b1a6ec9ad'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('active', sa.BOOLEAN(), nullable=False, default=True))


def downgrade():
    op.drop_column('users', 'active')