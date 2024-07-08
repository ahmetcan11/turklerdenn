"""New Migration

Revision ID: 107ac3656539
Revises: 2c5fcac0bb1e
Create Date: 2024-02-06 03:50:40.312521

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '107ac3656539'
down_revision = '2c5fcac0bb1e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('likedgeneralpost', sa.Column('user_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('likedgeneralpost', 'user_id')
    # ### end Alembic commands ###
