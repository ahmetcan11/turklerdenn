"""New Migration

Revision ID: c184a5b4ec5b
Revises: 3d971be76a81
Create Date: 2023-08-29 23:39:37.504731

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c184a5b4ec5b'
down_revision = '3d971be76a81'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('freeimage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('free_item_id', sa.Integer(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['free_item_id'], ['free.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_freeimage_id'), 'freeimage', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_freeimage_id'), table_name='freeimage')
    op.drop_table('freeimage')
    # ### end Alembic commands ###