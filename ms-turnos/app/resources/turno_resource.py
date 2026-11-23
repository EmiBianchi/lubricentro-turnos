from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.mapping import ConsultaFechaSchema, HorarioDisponibleSchema
from app.services.fabrica import crear_turno_service

turno_bp = Blueprint("turnos", __name__)
consulta_schema = ConsultaFechaSchema()
horarios_schema = HorarioDisponibleSchema(many=True)


@turno_bp.route("/disponibilidad", methods=["GET"])
@jwt_required()
def consultar_disponibilidad():
    """GET /api/v1/turnos/disponibilidad?fecha=AAAA-MM-DD — boxes libres por horario (HU-09)."""
    # La fecha viaja en la URL y no en un cuerpo JSON: GET es una consulta sin cuerpo.
    fecha = consulta_schema.load(request.args)["fecha"]
    horarios = crear_turno_service().consultar_disponibilidad(fecha)
    return {"fecha": fecha.isoformat(), "horarios": horarios_schema.dump(horarios)}, 200
