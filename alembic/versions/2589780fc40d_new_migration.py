"""New Migration

Revision ID: 2589780fc40d
Revises: 1314cd3c7150
Create Date: 2024-07-02 05:50:29.637189

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2589780fc40d'
down_revision = '1314cd3c7150'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('otp', sa.Column('first_name', sa.String(length=100), nullable=True))
    op.add_column('otp', sa.Column('last_name', sa.String(length=100), nullable=True))
    op.add_column('otp', sa.Column('encrypted_password', sa.String(length=100), nullable=True))
    op.drop_column('otpblocks', 'encrypted_password')
    op.drop_column('otpblocks', 'last_name')
    op.drop_column('otpblocks', 'first_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('otpblocks', sa.Column('first_name', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('otpblocks', sa.Column('last_name', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.add_column('otpblocks', sa.Column('encrypted_password', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
    op.drop_column('otp', 'encrypted_password')
    op.drop_column('otp', 'last_name')
    op.drop_column('otp', 'first_name')
    # ### end Alembic commands ###
