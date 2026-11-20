from app import db

ROL_CLIENTE = "cliente"


class Rol(db.Model):
    """Rol de aplicación (no de base de datos). Se modela como tabla para poder
    agregar roles nuevos sin modificar el código de Usuario (OCP)."""

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(30), unique=True, nullable=False)
