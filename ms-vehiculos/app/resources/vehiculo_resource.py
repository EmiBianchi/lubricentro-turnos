from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.mapping import VehiculoSchema
from app.services.fabrica import crear_vehiculo_service

vehiculo_bp = Blueprint("vehiculos", __name__)
vehiculo_schema = VehiculoSchema()
vehiculos_schema = VehiculoSchema(many=True)


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


@vehiculo_bp.route("", methods=["GET"])
@jwt_required()
def listar():
    """GET /api/v1/vehiculos — vehículos activos del cliente del token (HU-06)."""
    vehiculos = crear_vehiculo_service().listar_de_usuario(_cliente_del_token())
    return vehiculos_schema.dump(vehiculos), 200


@vehiculo_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def modificar(id: int):
    """PUT /api/v1/vehiculos/<id> — corrige los datos de un vehículo propio (HU-07)."""
    # PUT y no PATCH: se envía el vehículo completo y pasa por el mismo schema que
    # el registro, así las validaciones son idénticas (criterio de HU-07).
    datos = vehiculo_schema.load(request.get_json(silent=True) or {})
    vehiculo = crear_vehiculo_service().modificar(id, _cliente_del_token(), datos)
    return vehiculo_schema.dump(vehiculo), 200


@vehiculo_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def dar_de_baja(id: int):
    """DELETE /api/v1/vehiculos/<id> — baja lógica de un vehículo propio (HU-08)."""
    crear_vehiculo_service().dar_de_baja(id, _cliente_del_token())
    # 204: la operación salió bien y no hay contenido que devolver.
    return "", 204
