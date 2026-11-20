import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# El .env está en la raíz del microservicio (ms-usuarios/.env). Las credenciales
# se leen del entorno y nunca quedan escritas en el código (12-Factor, RNF-07).
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Clave con la que se firman los tokens. ms-vehiculos y ms-turnos usarán la
    # misma para validarlos sin consultar a ms-usuarios en cada pedido.
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_EXPIRA_MINUTOS", "60")))


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DEV_DATABASE_URI")


class TestingConfig(Config):
    TESTING = True
    # SQLite en memoria: cada test crea y destruye sus tablas sin depender de
    # Docker ni ensuciar usuarios_db (tests rápidos, independientes e inocuos).
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    # Clave fija para que los tests no dependan del .env de cada máquina.
    JWT_SECRET_KEY = "clave-solo-para-tests-de-al-menos-32-caracteres"


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("PROD_DATABASE_URI")


def factory(entorno: str) -> type[Config]:
    """Devuelve la clase de configuración del entorno indicado.

    :param entorno: "development", "testing" o "production".
    :return: clase de configuración para app.config.from_object.
    """
    configuraciones = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    return configuraciones[entorno]
