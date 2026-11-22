from app import db
from app.models.audit_mixin import AuditMixin
from app.models.soft_delete_mixin import SoftDeleteMixin
from app.models.tipo_vehiculo import TipoVehiculo


class Vehiculo(AuditMixin, SoftDeleteMixin, db.Model):
    """Datos persistidos de un vehículo. No valida: las validaciones de entrada
    viven en mapping y las reglas de negocio en services (SRP)."""

    __tablename__ = "vehiculos"

    id = db.Column(db.Integer, primary_key=True)
    patente = db.Column(db.String(7), nullable=False)
    # values_callable: en la base se guarda el valor ("auto") y no el nombre ("AUTO").
    tipo = db.Column(
        db.Enum(TipoVehiculo, name="tipo_vehiculo",
                values_callable=lambda tipos: [tipo.value for tipo in tipos]),
        nullable=False,
    )
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    # Entero sin clave foránea: el usuario vive en la base de ms-usuarios y los
    # microservicios no comparten base de datos (RNF-01).
    usuario_id = db.Column(db.Integer, nullable=False, index=True)

    __table_args__ = (
        # Patente única solo entre vehículos activos: respalda en la base la
        # validación del servicio ante dos altas simultáneas y permite volver a
        # registrar la patente de un vehículo dado de baja (p. ej., si se vendió).
        db.Index("uq_vehiculos_patente_activa", "patente", unique=True,
                 postgresql_where=db.text("deleted_at IS NULL"),
                 sqlite_where=db.text("deleted_at IS NULL")),
    )
