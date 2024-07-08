"""New Migration

Revision ID: 331b5aeef1aa
Revises: 2589780fc40d
Create Date: 2024-07-07 18:38:47.907650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '331b5aeef1aa'
down_revision = '2589780fc40d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('general', sa.Column('total_comments_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('general', 'total_comments_count')
    # ### end Alembic commands ###
