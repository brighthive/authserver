"""empty message

Revision ID: 5c6f9c67de45
Revises: 1794e645d265
Create Date: 2020-07-20 14:27:37.563744

"""
from datetime import datetime
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '5c6f9c67de45'
down_revision = '1794e645d265'
branch_labels = None
depends_on = None

organizations_table = table('organizations',
    column('id', sa.String),
    column('name', sa.String),
    column('date_created', sa.TIMESTAMP),
    column('date_last_updated', sa.TIMESTAMP))

users_table = table('users',
    column('organization', sa.String),
    column('organization_id', sa.String, sa.ForeignKey))


def upgrade():
    # Create an Organization table.
    op.create_table('organizations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=40), nullable=False),
        sa.Column('date_created', sa.TIMESTAMP(), nullable=True),
        sa.Column('date_last_updated', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    # Add a NULLABLE organization_id to the User table, and create a foreign key relation with Organization table.
    op.add_column('users', sa.Column('organization_id', sa.String(), nullable=True))
    op.create_foreign_key(None, 'users', 'organizations', ['organization_id'], ['id'], ondelete='CASCADE')

    # Select values of 'organization' from User, and insert new Organizations (based on the 'organization' value).
    connection = op.get_bind()
    organizations = connection.execute('SELECT DISTINCT organization from users')
    for org in organizations:
        org_id = str(uuid4()).replace('-', '')
        op.bulk_insert(organizations_table, [
            {
                'id': org_id,
                'name': org['organization'],
                'date_created': datetime.utcnow(),
                'date_last_updated': datetime.utcnow()
            }
        ])

        connection.execute(
            users_table.update().where(users_table.c.organization==org['organization']).values({'organization_id':org_id})
        )

    # Drop 'organization' column, and make 'organization_id' a REQUIRED value.
    op.drop_column('users', 'organization')
    op.alter_column('users', 'organization_id', nullable=False)


def downgrade():
    op.add_column('users', sa.Column('organization', sa.VARCHAR(length=120), autoincrement=False, nullable=True))

    select_and_update_users = '''
        WITH org_data as
        (
            SELECT name as org_name, id as org_id
            FROM organizations
        )
        UPDATE users 
        SET organization = org_data.org_name
        FROM org_data
        WHERE org_data.org_id = organization_id
    '''
    op.execute(select_and_update_users)

    op.alter_column('users', 'organization', nullable=False)
    op.drop_constraint('users_organization_id_fkey', 'users', type_='foreignkey')
    op.drop_column('users', 'organization_id')
    op.drop_table('organizations')