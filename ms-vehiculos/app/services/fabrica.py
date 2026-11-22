"""Armado de servicios con sus dependencias concretas (patrón Factory).

Es el único lugar que elige las implementaciones reales; los servicios solo
conocen lo que reciben por constructor (DIP).
"""
from app.repository import VehiculoRepository
from app.services.vehiculo_service import VehiculoService


def crear_vehiculo_service() -> VehiculoService:
    return VehiculoService(VehiculoRepository())
