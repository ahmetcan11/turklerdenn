"""postid for event

Revision ID: c84f0441d155
Revises: ef1587509890
Create Date: 2023-09-16 19:47:08.442168

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c84f0441d155'
down_revision = 'ef1587509890'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    result = conn.execute(sa.text("UPDATE event SET post_id = 'event-' || id WHERE post_id IS NULL"))


def downgrade():
    pass  # If needed, implement a downgrade script
