"""empty message

Revision ID: 562aea6fd6ed
Revises: c73182052d2d
Create Date: 2020-06-12 16:32:20.735633

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '562aea6fd6ed'
down_revision = 'c73182052d2d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todos', 'list_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('todos', 'list_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
