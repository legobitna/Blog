"""empty message

Revision ID: 766e0cf839f6
Revises: 
Create Date: 2019-09-10 13:35:13.186921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '766e0cf839f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('view', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'view')
    # ### end Alembic commands ###
