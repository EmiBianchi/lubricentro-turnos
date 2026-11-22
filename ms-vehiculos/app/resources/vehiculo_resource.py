from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.mapping import VehiculoSchema
from app.services.fabrica import crear_vehiculo_service

vehiculo_bp = Blueprint("vehiculos", __name__)
vehiculo_schema = VehiculoSchema()


def _cliente_del_token() -> int:
    # El dueño sale siempre del token y nunca de la URL ni del cuerpo: un cliente
    # no puede operar sobre vehículos de otro haciéndose pasar por él.
    return int(get_jwt_identity())


@vehiculo_bp.route("", methods=["POST"])
@jwt_required()
def registrar():
    """POST /api/v1/vehiculos — alta de un vehículo del cliente (HU-05)."""
    # silent=True: un cuerpo vacío o que no es JSON llega como {} y marshmallow
    # responde 400 indicando los campos obligatorios, en vez de un error genérico.
    datos = vehiculo_schema.load(request.get_json(silent=True) or {})
    vehiculo = crear_vehiculo_service().registrar(_cliente_del_token(), datos)
    return vehiculo_schema.dump(vehiculo), 201
