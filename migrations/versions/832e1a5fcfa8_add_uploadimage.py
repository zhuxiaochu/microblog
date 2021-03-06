"""add UploadImage

Revision ID: 832e1a5fcfa8
Revises: dd91bf6531e6
Create Date: 2019-02-14 16:50:33.940059

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '832e1a5fcfa8'
down_revision = 'dd91bf6531e6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('upload_image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image_path', sa.String(length=64), nullable=True),
    sa.Column('upload_time', sa.DateTime(), nullable=True),
    sa.Column('mark', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_upload_image_mark'), 'upload_image', ['mark'], unique=False)
    op.create_index(op.f('ix_upload_image_upload_time'), 'upload_image', ['upload_time'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_upload_image_upload_time'), table_name='upload_image')
    op.drop_index(op.f('ix_upload_image_mark'), table_name='upload_image')
    op.drop_table('upload_image')
    # ### end Alembic commands ###
