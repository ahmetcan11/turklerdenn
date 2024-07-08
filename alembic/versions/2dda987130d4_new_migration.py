"""New Migration

Revision ID: 2dda987130d4
Revises: c184a5b4ec5b
Create Date: 2023-09-04 02:38:56.624857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2dda987130d4'
down_revision = 'c184a5b4ec5b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('business', sa.Column('is_online', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('business', 'is_online')
    # ### end Alembic commands ###
