"""New Migration

Revision ID: ebfca97c2672
Revises: 28e502f86041
Create Date: 2024-02-27 20:35:45.240795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ebfca97c2672'
down_revision = '28e502f86041'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('general', sa.Column('created_on', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('general', 'created_on')
    # ### end Alembic commands ###
