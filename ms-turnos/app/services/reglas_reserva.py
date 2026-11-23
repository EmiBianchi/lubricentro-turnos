from abc import ABC, abstractmethod
from datetime import time

from app.services.excepciones import HorarioFueraDeGrilla, TipoVehiculoNoAdmitido
from app.services.grilla_horaria import GrillaHoraria


class ReglaReserva(ABC):
    """Qué horario puede pedir un tipo de vehículo y qué casilleros ocupa.

    TurnoService solo conoce esta abstracción (DIP) y usa cualquier subclase sin
    preguntar cuál es (LSP): cada tipo de vehículo con otra regla es una clase
    nueva, sin modificar el servicio (OCP).
    """

    @abstractmethod
    def validar(self, hora: time, grilla: GrillaHoraria) -> None:
        """:raises ErrorDeNegocio: si el tipo de vehículo no puede reservar a esa hora."""

    @abstractmethod
    def horarios_a_ocupar(self, hora: time, grilla: GrillaHoraria) -> list[time]:
        """:return: los horarios que el turno ocupa en un mismo box, en orden."""


class ReglaTurnoComun(ReglaReserva):
    """Motos, autos y camionetas: cualquier horario de la grilla, un box durante
    30 minutos (RN-05)."""

    def validar(self, hora: time, grilla: GrillaHoraria) -> None:
        if grilla.franja_de(hora) is None:
            raise HorarioFueraDeGrilla(hora)

    def horarios_a_ocupar(self, hora: time, grilla: GrillaHoraria) -> list[time]:
        return [hora]


class FabricaReglas:
    """Elige la regla según el tipo de vehículo (patrón Factory)."""

    # Un tipo nuevo con otra regla es una entrada más en el diccionario (OCP).
    _REGLAS = {
        "moto": ReglaTurnoComun,
        "auto": ReglaTurnoComun,
        "camioneta": ReglaTurnoComun,
    }

    def crear(self, tipo_vehiculo: str) -> ReglaReserva:
        """:raises TipoVehiculoNoAdmitido: si no hay regla para ese tipo."""
        regla = self._REGLAS.get(tipo_vehiculo)
        if regla is None:
            raise TipoVehiculoNoAdmitido(tipo_vehiculo)
        return regla()
