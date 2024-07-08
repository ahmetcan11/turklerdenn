"""New Migration

Revision ID: a7a9469f6ac2
Revises: 2e89f80d560d
Create Date: 2023-09-09 02:16:13.683499

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a7a9469f6ac2'
down_revision = '2e89f80d560d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('house',
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('price', sa.String(), nullable=True),
    sa.Column('square_feet', sa.Integer(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_house_id'), 'house', ['id'], unique=False)
    op.create_index(op.f('ix_house_title'), 'house', ['title'], unique=False)
    op.create_table('houseimage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('house_id', sa.Integer(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=False),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['house_id'], ['house.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_houseimage_id'), 'houseimage', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_houseimage_id'), table_name='houseimage')
    op.drop_table('houseimage')
    op.drop_index(op.f('ix_house_title'), table_name='house')
    op.drop_index(op.f('ix_house_id'), table_name='house')
    op.drop_table('house')
    # ### end Alembic commands ###