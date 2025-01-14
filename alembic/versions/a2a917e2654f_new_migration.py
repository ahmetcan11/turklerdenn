"""New Migration

Revision ID: a2a917e2654f
Revises: b95e99ecede8
Create Date: 2023-03-21 01:33:05.610922

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a2a917e2654f'
down_revision = 'b95e99ecede8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('business', sa.Column('created_on', sa.DateTime(), nullable=True))
    op.add_column('event', sa.Column('created_on', sa.DateTime(), nullable=True))
    op.add_column('sharedroom', sa.Column('created_on', sa.DateTime(), nullable=True))
    op.drop_column('sharedroom', 'date')
    op.add_column('user', sa.Column('created_on', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'created_on')
    op.add_column('sharedroom', sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('sharedroom', 'created_on')
    op.drop_column('event', 'created_on')
    op.drop_column('business', 'created_on')
    # ### end Alembic commands ###
