"""ks

Revision ID: 45597d585c32
Revises: 
Create Date: 2024-08-11 01:00:31.878206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '45597d585c32'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('armario',
    sa.Column('id_armario', sa.Integer(), nullable=False),
    sa.Column('numero', sa.Integer(), nullable=True),
    sa.Column('capacidade_ferramentas', sa.Integer(), nullable=False),
    sa.Column('foto_armario', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id_armario')
    )
    op.create_table('ferramentas',
    sa.Column('id_ferramentas', sa.Integer(), nullable=False),
    sa.Column('nome_ferramenta', sa.String(), nullable=False),
    sa.Column('total_ferramenta', sa.Integer(), nullable=False),
    sa.Column('foto_ferramenta', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id_ferramentas')
    )
    op.create_table('ferramentas_suporte',
    sa.Column('id_ferramentas_sup', sa.Integer(), nullable=False),
    sa.Column('nome_ferramenta_sup', sa.String(), nullable=False),
    sa.Column('sala_ferramenta_sup', sa.String(), nullable=False),
    sa.Column('defeito_ferramenta_sup', sa.String(), nullable=False),
    sa.Column('data_ocorrido_sup', sa.String(), nullable=False),
    sa.Column('ocorrido_ferramenta_sup', sa.String(), nullable=False),
    sa.Column('foto_ferramenta_sup', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id_ferramentas_sup')
    )
    op.create_table('salas',
    sa.Column('id_salas', sa.Integer(), nullable=False),
    sa.Column('nome_sala', sa.String(), nullable=False),
    sa.Column('capacidade_armario', sa.Integer(), nullable=False),
    sa.Column('foto_sala', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id_salas')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('senha', sa.String(), nullable=True),
    sa.Column('adm', sa.Boolean(), nullable=True),
    sa.Column('foto', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('salas')
    op.drop_table('ferramentas_suporte')
    op.drop_table('ferramentas')
    op.drop_table('armario')
    # ### end Alembic commands ###