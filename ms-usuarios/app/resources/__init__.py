from flask import Flask

from app.resources.manejo_errores import registrar_manejadores_errores
from app.resources.usuario_resource import usuario_bp

PREFIJO_API = "/api/v1"


def registrar_recursos(app: Flask) -> None:
    """Registra los endpoints y los manejadores de errores en la aplicación."""
    app.register_blueprint(usuario_bp, url_prefix=f"{PREFIJO_API}/usuarios")
    registrar_manejadores_errores(app)
