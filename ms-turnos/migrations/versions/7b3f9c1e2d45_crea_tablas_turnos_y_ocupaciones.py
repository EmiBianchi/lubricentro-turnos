"""Crea tablas turnos y ocupaciones

Revision ID: 7b3f9c1e2d45
Revises:
Create Date: 2026-11-23 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b3f9c1e2d45'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('turnos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.Date(), nullable=False),
    sa.Column('hora_inicio', sa.Time(), nullable=False),
    sa.Column('hora_fin', sa.Time(), nullable=False),
    sa.Column('box', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('vehiculo_id', sa.Integer(), nullable=False),
    sa.Column('patente', sa.String(length=7), nullable=False),
    sa.Column('tipo_vehiculo', sa.String(length=10), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_turnos_fecha', 'turnos', ['fecha'], unique=False)
    op.create_index('ix_turnos_usuario_id', 'turnos', ['usuario_id'], unique=False)
    op.create_table('ocupaciones',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha', sa.Date(), nullable=False),
    sa.Column('hora', sa.Time(), nullable=False),
    sa.Column('box', sa.Integer(), nullable=False),
    sa.Column('turno_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['turno_id'], ['turnos.id']),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('fecha', 'hora', 'box', name='uq_ocupaciones_casillero')
    )


def downgrade():
    # Primero ocupaciones: su clave foránea apunta a turnos.
    op.drop_table('ocupaciones')
    op.drop_index('ix_turnos_usuario_id', table_name='turnos')
    op.drop_index('ix_turnos_fecha', table_name='turnos')
    op.drop_table('turnos')
