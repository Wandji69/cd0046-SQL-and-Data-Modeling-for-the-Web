"""empty message

Revision ID: eae8fc048c11
Revises: 1424e1cbc3de
Create Date: 2022-08-14 20:04:06.516388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eae8fc048c11'
down_revision = '1424e1cbc3de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('show', sa.Column('start_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('show', 'start_time')
    # ### end Alembic commands ###
