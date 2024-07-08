"""New Migration

Revision ID: 784eff57d4fe
Revises: d3fb95adab03
Create Date: 2023-09-16 19:25:43.348419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '784eff57d4fe'
down_revision = 'd3fb95adab03'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('business', sa.Column('post_id', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'business', ['post_id'])
    op.add_column('event', sa.Column('post_id', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'event', ['post_id'])
    op.add_column('house', sa.Column('post_id', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'house', ['post_id'])
    op.add_column('sharedroom', sa.Column('post_id', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'sharedroom', ['post_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'sharedroom', type_='unique')
    op.drop_column('sharedroom', 'post_id')
    op.drop_constraint(None, 'house', type_='unique')
    op.drop_column('house', 'post_id')
    op.drop_constraint(None, 'event', type_='unique')
    op.drop_column('event', 'post_id')
    op.drop_constraint(None, 'business', type_='unique')
    op.drop_column('business', 'post_id')
    # ### end Alembic commands ###
