from app import db
from app.models.audit_mixin import AuditMixin


class Usuario(AuditMixin, db.Model):
    """Datos persistidos de un usuario. No cifra ni valida: el cifrado vive en
    services/security.py para que el modelo tenga una sola responsabilidad (SRP)."""

    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # 255 caracteres: guarda el hash (scrypt de Werkzeug, ~160 caracteres), no la contraseña.
    password = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    # lazy="joined": el rol se trae en la misma consulta porque toda respuesta lo muestra.
    rol = db.relationship("Rol", lazy="joined")
