"""New Migration

Revision ID: 1ab4dc84f4b7
Revises: 40b5a0ac5a26
Create Date: 2024-06-15 07:10:02.984700

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ab4dc84f4b7'
down_revision = '40b5a0ac5a26'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('businessrequest', sa.Column('approved_status', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('businessrequest', 'approved_status')
    # ### end Alembic commands ###
