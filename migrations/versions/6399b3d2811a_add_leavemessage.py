"""add LeaveMessage

Revision ID: 6399b3d2811a
Revises: 832e1a5fcfa8
Create Date: 2019-02-16 21:10:20.935702

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6399b3d2811a'
down_revision = '832e1a5fcfa8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('leave_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=12), nullable=True),
    sa.Column('content', sa.String(length=140), nullable=True),
    sa.Column('email', sa.String(length=32), nullable=True),
    sa.Column('leave_time', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_message_email'), 'leave_message', ['email'], unique=True)
    op.create_index(op.f('ix_leave_message_leave_time'), 'leave_message', ['leave_time'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_leave_message_leave_time'), table_name='leave_message')
    op.drop_index(op.f('ix_leave_message_email'), table_name='leave_message')
    op.drop_table('leave_message')
    # ### end Alembic commands ###
