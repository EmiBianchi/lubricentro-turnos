from caso_base import URL_VEHICULOS, VEHICULO_VALIDO, CasoBase

DATOS_CORREGIDOS = {
    "patente": "AB123CD",
    "tipo": "camioneta",
    "marca": "Toyota",
    "modelo": "Hilux",
    "anio": 2020,
}


class ModificarVehiculoTestCase(CasoBase):
    """Criterios de aceptación de HU-07 (Modificar vehículo)."""

    def setUp(self):
        super().setUp()
        self.vehiculo_id = self.registrar_vehiculo(usuario_id=1).get_json()["id"]

    def modificar(self, usuario_id: int = 1, vehiculo_id: int | None = None, **cambios):
        url = f"{URL_VEHICULOS}/{vehiculo_id or self.vehiculo_id}"
        return self.cliente_http.put(
            url, json={**DATOS_CORREGIDOS, **cambios}, headers=self.encabezado_de(usuario_id)
        )

    def test_el_dueno_modifica_su_vehiculo(self):
        respuesta = self.modificar(usuario_id=1)
        self.assertEqual(respuesta.status_code, 200)
        for campo, valor in DATOS_CORREGIDOS.items():
            self.assertEqual(respuesta.get_json()[campo], valor)

    def test_los_cambios_se_ven_en_el_listado(self):
        self.modificar(usuario_id=1)
        vehiculo = self.listar_vehiculos(usuario_id=1).get_json()[0]
        self.assertEqual(vehiculo["marca"], "Toyota")

    def test_otro_cliente_recibe_403(self):
        respuesta = self.modificar(usuario_id=2)
        self.assertEqual(respuesta.status_code, 403)

    def test_otro_cliente_no_altera_los_datos(self):
        self.modificar(usuario_id=2)
        vehiculo = self.listar_vehiculos(usuario_id=1).get_json()[0]
        self.assertEqual(vehiculo["marca"], VEHICULO_VALIDO["marca"])

    def test_vehiculo_inexistente_devuelve_404(self):
        respuesta = self.modificar(usuario_id=1, vehiculo_id=999)
        self.assertEqual(respuesta.status_code, 404)

    def test_sin_token_devuelve_401(self):
        respuesta = self.cliente_http.put(f"{URL_VEHICULOS}/{self.vehiculo_id}",
                                          json=DATOS_CORREGIDOS)
        self.assertEqual(respuesta.status_code, 401)

    def test_campos_obligatorios_igual_que_al_registrar(self):
        for campo in DATOS_CORREGIDOS:
            with self.subTest(campo_faltante=campo):
                datos = {clave: valor for clave, valor in DATOS_CORREGIDOS.items() if clave != campo}
                respuesta = self.cliente_http.put(
                    f"{URL_VEHICULOS}/{self.vehiculo_id}", json=datos,
                    headers=self.encabezado_de(1),
                )
                self.assertEqual(respuesta.status_code, 400)

    def test_tipo_invalido_devuelve_400(self):
        respuesta = self.modificar(tipo="bicicleta")
        self.assertEqual(respuesta.status_code, 400)

    def test_anio_invalido_devuelve_400(self):
        respuesta = self.modificar(anio=1800)
        self.assertEqual(respuesta.status_code, 400)

    def test_patente_de_otro_vehiculo_devuelve_409(self):
        self.registrar_vehiculo(usuario_id=2, patente="AC456DE")
        respuesta = self.modificar(patente="AC456DE")
        self.assertEqual(respuesta.status_code, 409)

    def test_puede_cambiar_su_patente_por_una_libre(self):
        respuesta = self.modificar(patente="ZZ999ZZ")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json()["patente"], "ZZ999ZZ")

    def test_no_puede_cambiar_el_dueno(self):
        respuesta = self.cliente_http.put(
            f"{URL_VEHICULOS}/{self.vehiculo_id}", json={**DATOS_CORREGIDOS, "usuario_id": 2},
            headers=self.encabezado_de(1),
        )
        self.assertEqual(respuesta.status_code, 400)
