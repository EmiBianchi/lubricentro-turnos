from flask import Flask
from marshmallow import ValidationError

from app.services.excepciones import ErrorDeNegocio

# Traducción de errores de negocio a HTTP en un único lugar: una regla nueva se
# agrega como otra entrada del diccionario, sin modificar los manejadores (OCP).
# Las reglas que no figuran responden 400 (pedido inválido).
CODIGOS_HTTP = {}


def registrar_manejadores_errores(app: Flask) -> None:

    @app.errorhandler(ValidationError)
    def datos_invalidos(error: ValidationError):
        return {"errores": error.messages}, 400

    @app.errorhandler(ErrorDeNegocio)
    def regla_de_negocio(error: ErrorDeNegocio):
        return {"error": str(error)}, CODIGOS_HTTP.get(type(error), 400)
