"""empty message

Revision ID: ef21ce391d69
Revises: 86fd0c0da58d
Create Date: 2024-08-28 13:43:21.211897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef21ce391d69'
down_revision = '86fd0c0da58d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('armario', schema=None) as batch_op:
        batch_op.alter_column('numero',
               existing_type=sa.INTEGER(),
               type_=sa.String(),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('armario', schema=None) as batch_op:
        batch_op.alter_column('numero',
               existing_type=sa.String(),
               type_=sa.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
