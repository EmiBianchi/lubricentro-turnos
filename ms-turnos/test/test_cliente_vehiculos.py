import unittest
from unittest.mock import Mock, patch

import requests

from app.services.cliente_vehiculos import ClienteVehiculosHTTP
from app.services.excepciones import ServicioVehiculosNoDisponible

URL_BASE = "http://ms-vehiculos:5002"
VEHICULOS_DEL_CLIENTE = [
    {"id": 10, "patente": "AB123CD", "tipo": "auto"},
    {"id": 11, "patente": "AD789EF", "tipo": "camion"},
]


def respuesta_http(cuerpo, codigo: int = 200) -> Mock:
    """Simula la respuesta de requests.get sin hacer un pedido real."""
    respuesta = Mock(status_code=codigo)
    respuesta.json.return_value = cuerpo
    if codigo >= 400:
        respuesta.raise_for_status.side_effect = requests.HTTPError(f"{codigo}")
    return respuesta


@patch("app.services.cliente_vehiculos.requests.get")
class ClienteVehiculosHTTPTestCase(unittest.TestCase):
    """Comunicación con ms-vehiculos (RNF-09) probada sin levantarlo."""

    def setUp(self):
        self.cliente = ClienteVehiculosHTTP(URL_BASE)

    def test_devuelve_el_vehiculo_si_esta_entre_los_del_cliente(self, get):
        get.return_value = respuesta_http(VEHICULOS_DEL_CLIENTE)
        vehiculo = self.cliente.obtener_vehiculo(11, "token")
        self.assertEqual(vehiculo["tipo"], "camion")

    def test_devuelve_none_si_no_es_del_cliente(self, get):
        get.return_value = respuesta_http(VEHICULOS_DEL_CLIENTE)
        self.assertIsNone(self.cliente.obtener_vehiculo(999, "token"))

    def test_reenvia_el_token_del_cliente(self, get):
        get.return_value = respuesta_http([])
        self.cliente.obtener_vehiculo(10, "abc")
        url = get.call_args.args[0]
        self.assertEqual(url, f"{URL_BASE}/api/v1/vehiculos")
        self.assertEqual(get.call_args.kwargs["headers"], {"Authorization": "Bearer abc"})

    def test_usa_un_tiempo_de_espera(self, get):
        get.return_value = respuesta_http([])
        self.cliente.obtener_vehiculo(10, "abc")
        self.assertIsNotNone(get.call_args.kwargs.get("timeout"))

    def test_sin_conexion_lanza_servicio_no_disponible(self, get):
        get.side_effect = requests.ConnectionError()
        with self.assertRaises(ServicioVehiculosNoDisponible):
            self.cliente.obtener_vehiculo(10, "token")

    def test_respuesta_de_error_lanza_servicio_no_disponible(self, get):
        get.return_value = respuesta_http({"error": "falla"}, codigo=500)
        with self.assertRaises(ServicioVehiculosNoDisponible):
            self.cliente.obtener_vehiculo(10, "token")
