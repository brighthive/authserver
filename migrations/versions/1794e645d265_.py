"""empty message

Revision ID: 1794e645d265
Revises: 49bfe630a344
Create Date: 2020-02-12 17:37:49.538592

"""

import os
import sqlalchemy as sa
from alembic import op
from authserver import create_app


# revision identifiers, used by Alembic.
revision = '1794e645d265'
down_revision = '49bfe630a344'
branch_labels = None
depends_on = None


def upgrade():
    environment = os
    pass


def downgrade():
    pass
