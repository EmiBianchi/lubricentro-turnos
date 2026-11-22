from caso_base import URL_VEHICULOS, CasoBase


class ListarVehiculosTestCase(CasoBase):
    """Criterios de aceptación de HU-06 (Listar mis vehículos)."""

    def setUp(self):
        super().setUp()
        self.registrar_vehiculo(usuario_id=1, patente="AB123CD")
        self.registrar_vehiculo(usuario_id=1, patente="AC456DE", tipo="moto")
        self.registrar_vehiculo(usuario_id=2, patente="AD789EF")

    def test_devuelve_solo_los_vehiculos_del_cliente_del_token(self):
        respuesta = self.listar_vehiculos(usuario_id=1)
        self.assertEqual(respuesta.status_code, 200)
        patentes = {vehiculo["patente"] for vehiculo in respuesta.get_json()}
        self.assertEqual(patentes, {"AB123CD", "AC456DE"})

    def test_cliente_sin_vehiculos_recibe_lista_vacia(self):
        respuesta = self.listar_vehiculos(usuario_id=3)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json(), [])

    def test_no_muestra_vehiculos_dados_de_baja(self):
        vehiculo_id = self.registrar_vehiculo(usuario_id=1, patente="AE111FF").get_json()["id"]
        self.marcar_como_eliminado(vehiculo_id)
        patentes = {vehiculo["patente"] for vehiculo in self.listar_vehiculos(1).get_json()}
        self.assertNotIn("AE111FF", patentes)
        self.assertEqual(len(patentes), 2)

    def test_cada_vehiculo_muestra_sus_datos(self):
        vehiculo = self.listar_vehiculos(usuario_id=2).get_json()[0]
        for campo in ("id", "patente", "tipo", "marca", "modelo", "anio"):
            self.assertIn(campo, vehiculo)

    def test_sin_token_devuelve_401(self):
        respuesta = self.cliente_http.get(URL_VEHICULOS)
        self.assertEqual(respuesta.status_code, 401)
