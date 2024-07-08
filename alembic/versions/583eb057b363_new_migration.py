"""New Migration

Revision ID: 583eb057b363
Revises: 5125683141a9
Create Date: 2024-06-19 01:26:01.525693

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '583eb057b363'
down_revision = '5125683141a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('business', sa.Column('place_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('business', 'place_id')
    # ### end Alembic commands ###
