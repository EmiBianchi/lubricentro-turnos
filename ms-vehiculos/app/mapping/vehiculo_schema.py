import re
from datetime import date

from marshmallow import ValidationError, fields, pre_load, validate, validates

from app import ma
from app.models import TipoVehiculo

ANIO_MINIMO = 1900
# Formatos argentinos sin separadores: ABC123, AB123CD (Mercosur), A123BCD y 123ABC (motos).
FORMATO_PATENTE = r"^[A-Z0-9]{6,7}$"


class VehiculoSchema(ma.Schema):
    """Convierte Vehiculo <-> JSON y valida los datos de entrada.

    Registrar (HU-05) y modificar (HU-07) usan este mismo schema: así se aplican
    exactamente las mismas validaciones en ambos casos sin repetirlas (DRY).
    """

    id = fields.Integer(dump_only=True)
    patente = fields.String(required=True, validate=validate.Regexp(
        FORMATO_PATENTE, error="Patente inválida: deben ser 6 o 7 letras y números."))
    # by_value: el JSON usa "auto" (el valor), no "AUTO" (el nombre del Enum).
    tipo = fields.Enum(TipoVehiculo, by_value=True, required=True, error_messages={
        "unknown": "Tipo inválido. Valores posibles: {choices}."})
    marca = fields.String(required=True, validate=validate.Length(min=1, max=50))
    modelo = fields.String(required=True, validate=validate.Length(min=1, max=50))
    anio = fields.Integer(required=True)
    # dump_only: si el pedido trae "usuario_id", marshmallow lo rechaza como campo
    # desconocido (400). El dueño sale siempre del token, nunca del cuerpo.
    usuario_id = fields.Integer(dump_only=True)

    @pre_load
    def normalizar_patente(self, datos, **kwargs):
        # Sin normalizar, "ab 123 cd" y "AB123CD" pasarían como patentes distintas
        # y se violaría la regla de patente única.
        if isinstance(datos, dict) and isinstance(datos.get("patente"), str):
            datos = {**datos, "patente": re.sub(r"[\s-]", "", datos["patente"]).upper()}
        return datos

    @validates("anio")
    def validar_anio(self, valor: int, **kwargs) -> None:
        # Hasta el año próximo: los 0 km se patentan con el modelo del año siguiente.
        anio_maximo = date.today().year + 1
        if not ANIO_MINIMO <= valor <= anio_maximo:
            raise ValidationError(f"El año debe estar entre {ANIO_MINIMO} y {anio_maximo}.")
