from marshmallow import fields

from app import ma
from app.mapping.formatos import FORMATO_HORA


class ReservaSchema(ma.Schema):
    """Valida el pedido de reserva (solo entrada).

    No tiene box ni usuario_id: el box lo asigna el sistema (RN-10) y el dueño
    sale del token. Si el pedido los trae, marshmallow los rechaza como campos
    desconocidos (400).
    """

    # strict: rechaza "10" como texto; el id debe llegar como número JSON.
    vehiculo_id = fields.Integer(required=True, strict=True)
    fecha = fields.Date(required=True)
    hora = fields.Time(required=True, format=FORMATO_HORA)
