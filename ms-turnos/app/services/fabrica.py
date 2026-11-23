"""Armado de servicios con sus dependencias concretas (patrón Factory).

Es el único lugar que elige las implementaciones reales; los servicios solo
conocen lo que reciben por constructor (DIP).
"""
from flask import current_app

from app.repository import OcupacionRepository, TurnoRepository
from app.services.cliente_vehiculos import ClienteVehiculosHTTP
from app.services.grilla_horaria import GrillaHoraria
from app.services.reglas_reserva import FabricaReglas
from app.services.reloj import Reloj
from app.services.turno_service import TurnoService


def crear_turno_service() -> TurnoService:
    return TurnoService(
        TurnoRepository(),
        OcupacionRepository(),
        ClienteVehiculosHTTP(current_app.config["VEHICULOS_URL"]),
        GrillaHoraria(),
        FabricaReglas(),
        Reloj(),
    )
