"""Add a password recovery table for tracking nonces

Revision ID: ba055915d6e9
Revises: 3c9238327009
Create Date: 2021-02-03 15:48:47.361678

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ba055915d6e9'
down_revision = '3c9238327009'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('password_recovery',
                    sa.Column('nonce', sa.String(), nullable=False),
                    sa.Column('user_id', sa.String(), nullable=False),
                    sa.Column('date_created', sa.TIMESTAMP(), nullable=True),
                    sa.Column('expiration_date', sa.TIMESTAMP(), nullable=True),
                    sa.Column('date_recovered', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('nonce', 'user_id'),
                    sa.UniqueConstraint('nonce')
                    )
    # ### end Alembic commands ###


def downgrade():
    op.drop_table('password_recovery')
