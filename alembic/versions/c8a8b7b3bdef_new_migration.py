"""New Migration

Revision ID: c8a8b7b3bdef
Revises: 784eff57d4fe
Create Date: 2023-09-16 19:35:04.923135

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8a8b7b3bdef'
down_revision = '784eff57d4fe'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    result = conn.execute(sa.text("UPDATE free SET post_id = 'free_item-' || id WHERE post_id IS NULL"))


def downgrade():
    pass  # If needed, implement a downgrade script
