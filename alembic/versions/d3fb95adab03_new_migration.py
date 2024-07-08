"""New Migration

Revision ID: d3fb95adab03
Revises: 90c3f8f3bcf9
Create Date: 2023-09-16 07:54:45.318297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3fb95adab03'
down_revision = '90c3f8f3bcf9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('free', sa.Column('post_id', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'free', ['post_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'free', type_='unique')
    op.drop_column('free', 'post_id')
    # ### end Alembic commands ###