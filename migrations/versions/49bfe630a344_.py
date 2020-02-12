"""empty message

Revision ID: 49bfe630a344
Revises: 410130b93b0f
Create Date: 2020-02-12 17:19:04.107818

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '49bfe630a344'
down_revision = '410130b93b0f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('authorized_clients',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('client_id', sa.String(), nullable=False),
    sa.Column('authorized', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['oauth2_clients.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'client_id')
    )
    op.add_column('oauth2_authorization_codes', sa.Column('nonce', sa.Text(), nullable=True))
    op.add_column('oauth2_clients', sa.Column('client_id_issued_at', sa.Integer(), nullable=False))
    op.add_column('oauth2_clients', sa.Column('client_metadata', sa.Text(), nullable=True))
    op.add_column('oauth2_clients', sa.Column('client_secret_expires_at', sa.Integer(), nullable=False))
    op.drop_column('oauth2_clients', 'client_name')
    op.drop_column('oauth2_clients', 'tos_uri')
    op.drop_column('oauth2_clients', 'token_endpoint_auth_method')
    op.drop_column('oauth2_clients', 'software_id')
    op.drop_column('oauth2_clients', 'response_type')
    op.drop_column('oauth2_clients', 'software_version')
    op.drop_column('oauth2_clients', 'logo_uri')
    op.drop_column('oauth2_clients', 'scope')
    op.drop_column('oauth2_clients', 'client_uri')
    op.drop_column('oauth2_clients', 'jwks_uri')
    op.drop_column('oauth2_clients', 'i18n_metadata')
    op.drop_column('oauth2_clients', 'expires_at')
    op.drop_column('oauth2_clients', 'issued_at')
    op.drop_column('oauth2_clients', 'jwks_text')
    op.drop_column('oauth2_clients', 'grant_type')
    op.drop_column('oauth2_clients', 'redirect_uri')
    op.drop_column('oauth2_clients', 'policy_uri')
    op.drop_column('oauth2_clients', 'contact')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('oauth2_clients', sa.Column('contact', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('policy_uri', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('redirect_uri', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('grant_type', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('oauth2_clients', sa.Column('jwks_text', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('issued_at', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('oauth2_clients', sa.Column('expires_at', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('oauth2_clients', sa.Column('i18n_metadata', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('jwks_uri', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('client_uri', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('scope', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('oauth2_clients', sa.Column('logo_uri', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('software_version', sa.VARCHAR(length=48), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('response_type', sa.TEXT(), autoincrement=False, nullable=False))
    op.add_column('oauth2_clients', sa.Column('software_id', sa.VARCHAR(length=36), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('token_endpoint_auth_method', sa.VARCHAR(length=48), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('tos_uri', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('oauth2_clients', sa.Column('client_name', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.drop_column('oauth2_clients', 'client_secret_expires_at')
    op.drop_column('oauth2_clients', 'client_metadata')
    op.drop_column('oauth2_clients', 'client_id_issued_at')
    op.drop_column('oauth2_authorization_codes', 'nonce')
    op.drop_table('authorized_clients')
    # ### end Alembic commands ###
