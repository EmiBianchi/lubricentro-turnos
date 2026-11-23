import unittest

from app.models import TipoVehiculo
from app.services.excepciones import PatenteYaRegistrada, VehiculoAjeno
from app.services.vehiculo_service import VehiculoService


class RepositorioVehiculosFalso:
    """Doble de prueba en memoria: permite probar VehiculoService sin base de datos (DIP)."""

    def __init__(self):
        self.vehiculos = []

    def buscar_por_id(self, id):
        return next((v for v in self.vehiculos if v.id == id), None)

    def buscar_por_patente(self, patente):
        return next((v for v in self.vehiculos
                     if v.patente == patente and v.deleted_at is None), None)

    def guardar(self, vehiculo):
        if vehiculo not in self.vehiculos:
            vehiculo.id = len(self.vehiculos) + 1
            vehiculo.deleted_at = None
            self.vehiculos.append(vehiculo)
        return vehiculo

    def eliminar(self, vehiculo):
        vehiculo.deleted_at = "fecha de baja"


def datos_vehiculo(**cambios) -> dict:
    datos = {"patente": "AB123CD", "tipo": TipoVehiculo.AUTO, "marca": "Ford",
             "modelo": "Fiesta", "anio": 2018}
    return {**datos, **cambios}


class VehiculoServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.repo = RepositorioVehiculosFalso()
        self.servicio = VehiculoService(self.repo)

    def test_registrar_asocia_el_vehiculo_al_usuario(self):
        vehiculo = self.servicio.registrar(5, datos_vehiculo())
        self.assertEqual(vehiculo.usuario_id, 5)

    def test_registrar_patente_repetida_lanza_excepcion(self):
        self.servicio.registrar(1, datos_vehiculo())
        with self.assertRaises(PatenteYaRegistrada):
            self.servicio.registrar(2, datos_vehiculo(marca="Fiat"))

    def test_modificar_vehiculo_ajeno_lanza_excepcion(self):
        vehiculo = self.servicio.registrar(1, datos_vehiculo())
        with self.assertRaises(VehiculoAjeno):
            self.servicio.modificar(vehiculo.id, 2, datos_vehiculo(marca="Fiat"))

    def test_modificar_conservando_su_propia_patente(self):
        vehiculo = self.servicio.registrar(1, datos_vehiculo())
        modificado = self.servicio.modificar(vehiculo.id, 1, datos_vehiculo(marca="Fiat"))
        self.assertEqual(modificado.marca, "Fiat")

    def test_dar_de_baja_completa_deleted_at(self):
        vehiculo = self.servicio.registrar(1, datos_vehiculo())
        self.servicio.dar_de_baja(vehiculo.id, 1)
        self.assertIsNotNone(vehiculo.deleted_at)

    def test_dar_de_baja_vehiculo_ajeno_lanza_excepcion(self):
        vehiculo = self.servicio.registrar(1, datos_vehiculo())
        with self.assertRaises(VehiculoAjeno):
            self.servicio.dar_de_baja(vehiculo.id, 2)
        self.assertIsNone(vehiculo.deleted_at)
