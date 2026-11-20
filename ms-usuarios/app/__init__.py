import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.config import factory

# Extensiones creadas una sola vez a nivel de módulo y vinculadas a la app en
# create_app (inyección): cualquier capa las importa sin crear instancias nuevas.
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()


def create_app(entorno: str | None = None) -> Flask:
    """Construye la aplicación Flask (patrón Factory).

    :param entorno: "development", "testing" o "production". Si no se indica,
        se toma de la variable de entorno FLASK_CONTEXT.
    :return: aplicación configurada con sus extensiones y recursos.
    """
    entorno = entorno or os.getenv("FLASK_CONTEXT", "development")
    app = Flask(__name__)
    app.config.from_object(factory(entorno))

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)

    # Imports diferidos: models y resources importan db y ma desde este módulo,
    # por eso se cargan después de crearlos. Importar models explícitamente
    # garantiza que Flask-Migrate detecte todas las tablas.
    from app import models  # noqa: F401
    from app.resources import registrar_recursos

    registrar_recursos(app)
    return app
