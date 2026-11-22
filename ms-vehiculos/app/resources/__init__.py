from flask import Flask

from app import jwt
from app.resources.autorizacion import registrar_manejadores_jwt
from app.resources.manejo_errores import registrar_manejadores_errores
from app.resources.vehiculo_resource import vehiculo_bp

PREFIJO_API = "/api/v1"


def registrar_recursos(app: Flask) -> None:
    """Registra los endpoints y los manejadores de errores en la aplicación."""
    app.register_blueprint(vehiculo_bp, url_prefix=f"{PREFIJO_API}/vehiculos")
    registrar_manejadores_errores(app)
    registrar_manejadores_jwt(jwt)
