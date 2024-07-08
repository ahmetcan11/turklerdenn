"""postid for house

Revision ID: c94c7eb4c042
Revises: c84f0441d155
Create Date: 2023-09-16 19:48:33.872264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c94c7eb4c042'
down_revision = 'c84f0441d155'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    result = conn.execute(sa.text("UPDATE house SET post_id = 'house-' || id WHERE post_id IS NULL"))


def downgrade():
    pass  # If needed, implement a downgrade script
