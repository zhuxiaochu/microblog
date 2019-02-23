"""cancel email unique

Revision ID: 4fe6ec54e179
Revises: 6399b3d2811a
Create Date: 2019-02-16 21:29:51.396649

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4fe6ec54e179'
down_revision = '6399b3d2811a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_leave_message_email', table_name='leave_message')
    op.create_index(op.f('ix_leave_message_email'), 'leave_message', ['email'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_leave_message_email'), table_name='leave_message')
    op.create_index('ix_leave_message_email', 'leave_message', ['email'], unique=1)
    # ### end Alembic commands ###