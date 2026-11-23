"""Armado de servicios con sus dependencias concretas (patrón Factory).

Es el único lugar que elige las implementaciones reales; los servicios solo
conocen lo que reciben por constructor (DIP).
"""
from app.repository import OcupacionRepository
from app.services.grilla_horaria import GrillaHoraria
from app.services.reloj import Reloj
from app.services.turno_service import TurnoService


def crear_turno_service() -> TurnoService:
    return TurnoService(OcupacionRepository(), GrillaHoraria(), Reloj())
