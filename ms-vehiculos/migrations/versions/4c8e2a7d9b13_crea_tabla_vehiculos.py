"""Crea tabla vehiculos

Revision ID: 4c8e2a7d9b13
Revises:
Create Date: 2026-11-22 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c8e2a7d9b13'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('vehiculos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patente', sa.String(length=7), nullable=False),
    sa.Column('tipo', sa.Enum('moto', 'auto', 'camioneta', 'camion', name='tipo_vehiculo'), nullable=False),
    sa.Column('marca', sa.String(length=50), nullable=False),
    sa.Column('modelo', sa.String(length=50), nullable=False),
    sa.Column('anio', sa.Integer(), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vehiculos_usuario_id', 'vehiculos', ['usuario_id'], unique=False)
    op.create_index('uq_vehiculos_patente_activa', 'vehiculos', ['patente'], unique=True,
                    postgresql_where=sa.text('deleted_at IS NULL'),
                    sqlite_where=sa.text('deleted_at IS NULL'))


def downgrade():
    op.drop_index('uq_vehiculos_patente_activa', table_name='vehiculos')
    op.drop_index('ix_vehiculos_usuario_id', table_name='vehiculos')
    op.drop_table('vehiculos')
    # PostgreSQL crea el tipo ENUM aparte de la tabla: si no se borra, un nuevo
    # upgrade falla porque el tipo ya existe.
    sa.Enum(name='tipo_vehiculo').drop(op.get_bind(), checkfirst=True)
