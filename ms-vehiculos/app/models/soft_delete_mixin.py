from app import db


class SoftDeleteMixin:
    """Baja lógica compartida (DRY): en lugar de un DELETE se completa deleted_at.

    El registro se conserva porque ms-turnos guarda el id del vehículo en turnos
    ya reservados; borrarlo dejaría esos turnos apuntando a un vehículo inexistente.
    """

    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
