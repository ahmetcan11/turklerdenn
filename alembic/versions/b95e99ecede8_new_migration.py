"""New Migration

Revision ID: b95e99ecede8
Revises: cb96e4b94ea9
Create Date: 2023-03-20 02:09:41.004632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b95e99ecede8'
down_revision = 'cb96e4b94ea9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklists',
    sa.Column('token', sa.String(length=250), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('token')
    )
    op.create_table('codes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('reset_code', sa.String(length=50), nullable=True),
    sa.Column('status', sa.String(length=1), nullable=True),
    sa.Column('expired_in', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_codes_id'), 'codes', ['id'], unique=False)
    op.create_table('otp',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipient_id', sa.String(length=100), nullable=True),
    sa.Column('session_id', sa.String(length=100), nullable=True),
    sa.Column('otp_code', sa.String(length=6), nullable=True),
    sa.Column('status', sa.String(length=1), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('updated_on', sa.DateTime(), nullable=True),
    sa.Column('otp_failed_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_otp_id'), 'otp', ['id'], unique=False)
    op.create_table('otpblocks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('recipient_id', sa.String(length=100), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_otpblocks_id'), 'otpblocks', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_otpblocks_id'), table_name='otpblocks')
    op.drop_table('otpblocks')
    op.drop_index(op.f('ix_otp_id'), table_name='otp')
    op.drop_table('otp')
    op.drop_index(op.f('ix_codes_id'), table_name='codes')
    op.drop_table('codes')
    op.drop_table('blacklists')
    # ### end Alembic commands ###
