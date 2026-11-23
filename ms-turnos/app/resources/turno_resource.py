from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.mapping import ConsultaFechaSchema, HorarioDisponibleSchema, ReservaSchema, TurnoSchema
from app.services.fabrica import crear_turno_service

turno_bp = Blueprint("turnos", __name__)
consulta_schema = ConsultaFechaSchema()
horarios_schema = HorarioDisponibleSchema(many=True)
reserva_schema = ReservaSchema()
turno_schema = TurnoSchema()


def _cliente_del_token() -> int:
    # El dueño sale siempre del token y nunca de la URL ni del cuerpo: un cliente
    # no puede reservar ni operar turnos haciéndose pasar por otro.
    return int(get_jwt_identity())


def _token_del_pedido() -> str:
    # jwt_required ya verificó que el encabezado sea "Bearer <token>". Se reenvía
    # el mismo token a ms-vehiculos para que identifique al mismo cliente.
    return request.headers["Authorization"].removeprefix("Bearer ").strip()


@turno_bp.route("/disponibilidad", methods=["GET"])
@jwt_required()
def consultar_disponibilidad():
    """GET /api/v1/turnos/disponibilidad?fecha=AAAA-MM-DD — boxes libres por horario (HU-09)."""
    # La fecha viaja en la URL y no en un cuerpo JSON: GET es una consulta sin cuerpo.
    fecha = consulta_schema.load(request.args)["fecha"]
    horarios = crear_turno_service().consultar_disponibilidad(fecha)
    return {"fecha": fecha.isoformat(), "horarios": horarios_schema.dump(horarios)}, 200


@turno_bp.route("", methods=["POST"])
@jwt_required()
def reservar():
    """POST /api/v1/turnos — reserva un turno con box asignado automáticamente (HU-10)."""
    # silent=True: un cuerpo vacío o que no es JSON llega como {} y marshmallow
    # responde 400 indicando los campos obligatorios, en vez de un error genérico.
    datos = reserva_schema.load(request.get_json(silent=True) or {})
    turno = crear_turno_service().reservar(_cliente_del_token(), token=_token_del_pedido(), **datos)
    return turno_schema.dump(turno), 201
