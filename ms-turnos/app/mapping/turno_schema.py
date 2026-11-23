from marshmallow import fields

from app import ma
from app.mapping.formatos import FORMATO_HORA


class TurnoSchema(ma.Schema):
    """Convierte Turno a JSON (solo salida). Las ocupaciones y la auditoría no se
    exponen: son detalles internos de cómo se bloquean los boxes."""

    id = fields.Integer()
    fecha = fields.Date()
    hora_inicio = fields.Time(format=FORMATO_HORA)
    hora_fin = fields.Time(format=FORMATO_HORA)
    box = fields.Integer()
    usuario_id = fields.Integer()
    vehiculo_id = fields.Integer()
    patente = fields.String()
    tipo_vehiculo = fields.String()
