"""postid for sharedroom

Revision ID: 820ff26bd8bd
Revises: afe07009d755
Create Date: 2023-09-16 19:50:24.017221

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '820ff26bd8bd'
down_revision = 'afe07009d755'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    result = conn.execute(sa.text("UPDATE sharedroom SET post_id = 'shared_room-' || id WHERE post_id IS NULL"))


def downgrade():
    pass  # If needed, implement a downgrade script
