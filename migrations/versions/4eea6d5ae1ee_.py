"""empty message

Revision ID: 4eea6d5ae1ee
Revises: 339d47a41f8c
Create Date: 2019-07-26 16:56:30.607554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4eea6d5ae1ee'
down_revision = '339d47a41f8c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('oauth2_authorization_codes',
    sa.Column('code', sa.String(length=120), nullable=False),
    sa.Column('client_id', sa.String(length=48), nullable=True),
    sa.Column('redirect_uri', sa.Text(), nullable=True),
    sa.Column('response_type', sa.Text(), nullable=True),
    sa.Column('scope', sa.Text(), nullable=True),
    sa.Column('auth_time', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_table('oauth2_clients',
    sa.Column('client_id', sa.String(length=48), nullable=True),
    sa.Column('client_secret', sa.String(length=120), nullable=True),
    sa.Column('issued_at', sa.Integer(), nullable=False),
    sa.Column('expires_at', sa.Integer(), nullable=False),
    sa.Column('redirect_uri', sa.Text(), nullable=True),
    sa.Column('token_endpoint_auth_method', sa.String(length=48), nullable=True),
    sa.Column('grant_type', sa.Text(), nullable=False),
    sa.Column('response_type', sa.Text(), nullable=False),
    sa.Column('scope', sa.Text(), nullable=False),
    sa.Column('client_name', sa.String(length=100), nullable=True),
    sa.Column('client_uri', sa.Text(), nullable=True),
    sa.Column('logo_uri', sa.Text(), nullable=True),
    sa.Column('contact', sa.Text(), nullable=True),
    sa.Column('tos_uri', sa.Text(), nullable=True),
    sa.Column('policy_uri', sa.Text(), nullable=True),
    sa.Column('jwks_uri', sa.Text(), nullable=True),
    sa.Column('jwks_text', sa.Text(), nullable=True),
    sa.Column('i18n_metadata', sa.Text(), nullable=True),
    sa.Column('software_id', sa.String(length=36), nullable=True),
    sa.Column('software_version', sa.String(length=48), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_oauth2_clients_client_id'), 'oauth2_clients', ['client_id'], unique=False)
    op.create_table('oauth2_tokens',
    sa.Column('client_id', sa.String(length=48), nullable=True),
    sa.Column('token_type', sa.String(length=40), nullable=True),
    sa.Column('access_token', sa.String(length=255), nullable=False),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.Column('scope', sa.Text(), nullable=True),
    sa.Column('revoked', sa.Boolean(), nullable=True),
    sa.Column('issued_at', sa.Integer(), nullable=False),
    sa.Column('expires_in', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('access_token')
    )
    op.create_index(op.f('ix_oauth2_tokens_refresh_token'), 'oauth2_tokens', ['refresh_token'], unique=False)
    op.drop_index('ix_oauth2_client_client_id', table_name='oauth2_client')
    op.drop_table('oauth2_client')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('oauth2_client',
    sa.Column('client_id', sa.VARCHAR(length=48), autoincrement=False, nullable=True),
    sa.Column('client_secret', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('issued_at', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('expires_at', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('redirect_uri', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('token_endpoint_auth_method', sa.VARCHAR(length=48), autoincrement=False, nullable=True),
    sa.Column('grant_type', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('response_type', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('scope', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('client_name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('client_uri', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('logo_uri', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('contact', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('tos_uri', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('policy_uri', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('jwks_uri', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('jwks_text', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('i18n_metadata', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('software_id', sa.VARCHAR(length=36), autoincrement=False, nullable=True),
    sa.Column('software_version', sa.VARCHAR(length=48), autoincrement=False, nullable=True),
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='oauth2_client_user_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='oauth2_client_pkey')
    )
    op.create_index('ix_oauth2_client_client_id', 'oauth2_client', ['client_id'], unique=False)
    op.drop_index(op.f('ix_oauth2_tokens_refresh_token'), table_name='oauth2_tokens')
    op.drop_table('oauth2_tokens')
    op.drop_index(op.f('ix_oauth2_clients_client_id'), table_name='oauth2_clients')
    op.drop_table('oauth2_clients')
    op.drop_table('oauth2_authorization_codes')
    # ### end Alembic commands ###