"""add column image_name

Revision ID: 7038fe779151
Revises: 4fe6ec54e179
Create Date: 2019-02-25 16:52:22.503856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7038fe779151'
down_revision = '8e622386e11b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('upload_image', sa.Column('image_name', sa.String(length=48), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('upload_image', 'image_path',
               existing_type=sa.String(length=256),
               type_=sa.VARCHAR(length=64),
               existing_nullable=True)
    op.drop_column('upload_image', 'image_name')
    op.alter_column('regist_code', 'verify_code',
               existing_type=sa.String(length=16),
               type_=sa.INTEGER(),
               existing_nullable=True)
    op.alter_column('post', 'title',
               existing_type=sa.String(length=128),
               type_=sa.VARCHAR(length=100),
               existing_nullable=True)
    op.alter_column('post', 'content',
               existing_type=sa.String(length=20000),
               type_=sa.VARCHAR(length=140),
               existing_nullable=True)
    op.alter_column('leave_message', 'email',
               existing_type=sa.String(length=48),
               type_=sa.VARCHAR(length=32),
               existing_nullable=True)
    op.alter_column('leave_message', 'content',
               existing_type=sa.String(length=210),
               type_=sa.VARCHAR(length=140),
               existing_nullable=True)
    # ### end Alembic commands ###
