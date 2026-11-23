from app import db
from app.models.audit_mixin import AuditMixin
from app.models.soft_delete_mixin import SoftDeleteMixin


class Turno(AuditMixin, SoftDeleteMixin, db.Model):
    """Reserva de un vehículo en un box. No valida: las validaciones de entrada
    viven en mapping y las reglas de negocio en services (SRP)."""

    __tablename__ = "turnos"

    id = db.Column(db.Integer, primary_key=True)
    # Fecha y horas en hora local del lubricentro, sin zona: la grilla (RN-02 y
    # RN-03) se define en horario de Argentina y así se compara directamente.
    fecha = db.Column(db.Date, nullable=False, index=True)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    box = db.Column(db.Integer, nullable=False)
    # Enteros sin clave foránea: usuarios y vehículos viven en las bases de
    # ms-usuarios y ms-vehiculos; los microservicios no comparten base (RNF-01).
    usuario_id = db.Column(db.Integer, nullable=False, index=True)
    vehiculo_id = db.Column(db.Integer, nullable=False)
    # Copia de patente y tipo al momento de reservar: la agenda (HU-14) los muestra
    # sin consultar a ms-vehiculos por cada turno. Texto y no Enum: la lista de
    # tipos válidos pertenece a ms-vehiculos.
    patente = db.Column(db.String(7), nullable=False)
    tipo_vehiculo = db.Column(db.String(10), nullable=False)

    # Composición (diagrama de clases): las ocupaciones no existen sin su turno,
    # se guardan junto con él y delete-orphan borra las que se quitan de la lista.
    ocupaciones = db.relationship("Ocupacion", cascade="all, delete-orphan")
