"""postid for business

Revision ID: ef1587509890
Revises: c8a8b7b3bdef
Create Date: 2023-09-16 19:44:41.896470

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef1587509890'
down_revision = 'c8a8b7b3bdef'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    result = conn.execute(sa.text("UPDATE business SET post_id = 'business-' || id WHERE post_id IS NULL"))


def downgrade():
    pass  # If needed, implement a downgrade script
