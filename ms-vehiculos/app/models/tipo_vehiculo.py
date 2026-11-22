from enum import Enum


class TipoVehiculo(Enum):
    """Tipos aceptados (HU-05). Enum y no texto libre: ms-turnos decide la regla
    de reserva según el tipo (RN-05 y RN-06), así que no puede haber variantes
    como "Camión" o "camion " que esa regla no reconozca."""

    MOTO = "moto"
    AUTO = "auto"
    CAMIONETA = "camioneta"
    CAMION = "camion"
