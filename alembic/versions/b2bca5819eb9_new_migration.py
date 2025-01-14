"""New Migration

Revision ID: b2bca5819eb9
Revises: 6494592dae22
Create Date: 2024-02-15 01:16:03.367747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2bca5819eb9'
down_revision = '6494592dae22'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('updowncomment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('comment_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('upvote', sa.Boolean(), nullable=True),
    sa.Column('downvote', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_updowncomment_id'), 'updowncomment', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_updowncomment_id'), table_name='updowncomment')
    op.drop_table('updowncomment')
    # ### end Alembic commands ###
