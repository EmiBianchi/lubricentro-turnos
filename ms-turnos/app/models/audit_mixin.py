from datetime import datetime, timezone

from app import db


def ahora() -> datetime:
    return datetime.now(timezone.utc)


class AuditMixin:
    """Columnas de auditoría compartidas (DRY): los modelos las heredan en lugar
    de repetirlas. updated_at se renueva sola en cada UPDATE (onupdate)."""

    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=ahora,
                           onupdate=ahora)
