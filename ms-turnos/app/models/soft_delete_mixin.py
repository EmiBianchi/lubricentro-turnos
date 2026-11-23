from app import db


class SoftDeleteMixin:
    """Baja lógica compartida (DRY): en lugar de un DELETE se completa deleted_at.

    Un turno cancelado no se borra (RN-09): se conserva quién reservó, qué día y en
    qué box, aunque ya no ocupe el horario ni aparezca en los listados.
    """

    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
