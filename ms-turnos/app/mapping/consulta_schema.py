from marshmallow import fields

from app import ma


class ConsultaFechaSchema(ma.Schema):
    """Valida el parámetro ?fecha=AAAA-MM-DD de las consultas por día.

    Formato ISO: es el que devuelve date.isoformat() y el que usa JSON en el
    resto de la API, así cliente y servidor no interpretan distinto "01/02".
    """

    fecha = fields.Date(required=True)
