"""empty message

Revision ID: 91fb9f00304b
Revises: 4173e6fe893f
Create Date: 2019-07-25 11:49:45.804185

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91fb9f00304b'
down_revision = '4173e6fe893f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('data_trusts',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('data_trust_name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('data_trust_name')
    )
    op.drop_table('data_trust')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('data_trust',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('data_trust_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='data_trust_pkey'),
    sa.UniqueConstraint('data_trust_name', name='data_trust_data_trust_name_key')
    )
    op.drop_table('data_trusts')
    # ### end Alembic commands ###
