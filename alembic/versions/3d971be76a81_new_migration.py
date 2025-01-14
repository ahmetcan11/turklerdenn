"""New Migration

Revision ID: 3d971be76a81
Revises: 59effd1ddefe
Create Date: 2023-08-29 23:38:37.897001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d971be76a81'
down_revision = '59effd1ddefe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('free', 'image_url')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('free', sa.Column('image_url', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
