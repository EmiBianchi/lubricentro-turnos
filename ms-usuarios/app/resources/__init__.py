from flask import Flask

from app.resources.auth_resource import auth_bp
from app.resources.manejo_errores import registrar_manejadores_errores
from app.resources.usuario_resource import usuario_bp

PREFIJO_API = "/api/v1"


def registrar_recursos(app: Flask) -> None:
    """Registra los endpoints y los manejadores de errores en la aplicación."""
    app.register_blueprint(usuario_bp, url_prefix=f"{PREFIJO_API}/usuarios")
    app.register_blueprint(auth_bp, url_prefix=f"{PREFIJO_API}/auth")
    registrar_manejadores_errores(app)
