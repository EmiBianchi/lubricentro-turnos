from marshmallow import fields

from app import ma
from app.mapping.formatos import FORMATO_HORA


class HorarioDisponibleSchema(ma.Schema):
    """Convierte cada horario de la disponibilidad a JSON (solo salida)."""

    hora = fields.Time(format=FORMATO_HORA)
    boxes_libres = fields.Integer()
