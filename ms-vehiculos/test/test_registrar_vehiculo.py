from datetime import date

from caso_base import URL_VEHICULOS, VEHICULO_VALIDO, CasoBase


class RegistrarVehiculoTestCase(CasoBase):
    """Criterios de aceptación de HU-05 (Registrar vehículo)."""

    def test_registro_exitoso_devuelve_201_con_los_datos(self):
        respuesta = self.registrar_vehiculo()
        self.assertEqual(respuesta.status_code, 201)
        datos = respuesta.get_json()
        self.assertIn("id", datos)
        for campo, valor in VEHICULO_VALIDO.items():
            self.assertEqual(datos[campo], valor)

    def test_sin_token_devuelve_401(self):
        respuesta = self.cliente_http.post(URL_VEHICULOS, json=VEHICULO_VALIDO)
        self.assertEqual(respuesta.status_code, 401)

    def test_token_invalido_devuelve_401(self):
        respuesta = self.cliente_http.post(
            URL_VEHICULOS, json=VEHICULO_VALIDO,
            headers={"Authorization": "Bearer token-inventado"},
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_campos_obligatorios(self):
        for campo in VEHICULO_VALIDO:
            with self.subTest(campo_faltante=campo):
                datos = {clave: valor for clave, valor in VEHICULO_VALIDO.items() if clave != campo}
                respuesta = self.cliente_http.post(
                    URL_VEHICULOS, json=datos, headers=self.encabezado_de()
                )
                self.assertEqual(respuesta.status_code, 400)

    def test_campos_de_texto_vacios_devuelven_400(self):
        respuesta = self.registrar_vehiculo(marca="", modelo="")
        self.assertEqual(respuesta.status_code, 400)

    def test_acepta_los_cuatro_tipos_validos(self):
        patentes = {"moto": "A123BCD", "auto": "AB123CD", "camioneta": "AC456DE", "camion": "AD789EF"}
        for tipo, patente in patentes.items():
            with self.subTest(tipo=tipo):
                respuesta = self.registrar_vehiculo(tipo=tipo, patente=patente)
                self.assertEqual(respuesta.status_code, 201)
                self.assertEqual(respuesta.get_json()["tipo"], tipo)

    def test_tipo_invalido_devuelve_400(self):
        respuesta = self.registrar_vehiculo(tipo="bicicleta")
        self.assertEqual(respuesta.status_code, 400)

    def test_anio_fuera_de_rango_devuelve_400(self):
        for anio in (1800, date.today().year + 2):
            with self.subTest(anio=anio):
                respuesta = self.registrar_vehiculo(anio=anio)
                self.assertEqual(respuesta.status_code, 400)

    def test_patente_con_formato_invalido_devuelve_400(self):
        for patente in ("AB1", "AB-12#CD", "ABCDEFGHIJK"):
            with self.subTest(patente=patente):
                respuesta = self.registrar_vehiculo(patente=patente)
                self.assertEqual(respuesta.status_code, 400)

    def test_patente_repetida_devuelve_409(self):
        self.registrar_vehiculo(usuario_id=1)
        respuesta = self.registrar_vehiculo(usuario_id=2, marca="Fiat", modelo="Palio")
        self.assertEqual(respuesta.status_code, 409)

    def test_la_patente_se_normaliza_antes_de_comparar(self):
        self.registrar_vehiculo(patente="AB123CD")
        respuesta = self.registrar_vehiculo(patente="ab 123 cd")
        self.assertEqual(respuesta.status_code, 409)

    def test_la_patente_se_guarda_en_mayusculas_y_sin_espacios(self):
        respuesta = self.registrar_vehiculo(patente="ab-123 cd")
        self.assertEqual(respuesta.get_json()["patente"], "AB123CD")

    def test_queda_asociado_al_cliente_del_token(self):
        respuesta = self.registrar_vehiculo(usuario_id=7)
        self.assertEqual(respuesta.get_json()["usuario_id"], 7)

    def test_no_se_puede_elegir_el_dueno_desde_el_cuerpo(self):
        respuesta = self.cliente_http.post(
            URL_VEHICULOS, json={**VEHICULO_VALIDO, "usuario_id": 99},
            headers=self.encabezado_de(usuario_id=1),
        )
        self.assertEqual(respuesta.status_code, 400)
