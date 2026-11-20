from datetime import timedelta

from caso_base import CasoBase
from flask_jwt_extended import create_access_token

URL_PERFIL = "/api/v1/usuarios/perfil"


class PerfilTestCase(CasoBase):
    """Criterios de aceptación de HU-03 (Ver mi perfil)."""

    def setUp(self):
        super().setUp()
        self.registrar(nombre="Juan Perez", email="juan@mail.com", password="clave123")

    def test_con_token_valido_devuelve_nombre_email_y_rol(self):
        respuesta = self.cliente_http.get(URL_PERFIL, headers=self.encabezado_con_token())
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.get_json()
        self.assertEqual(datos["nombre"], "Juan Perez")
        self.assertEqual(datos["email"], "juan@mail.com")
        self.assertEqual(datos["rol"], "cliente")

    def test_no_devuelve_la_password(self):
        respuesta = self.cliente_http.get(URL_PERFIL, headers=self.encabezado_con_token())
        self.assertNotIn("password", respuesta.get_json())

    def test_sin_token_devuelve_401(self):
        respuesta = self.cliente_http.get(URL_PERFIL)
        self.assertEqual(respuesta.status_code, 401)

    def test_token_invalido_devuelve_401(self):
        respuesta = self.cliente_http.get(
            URL_PERFIL, headers={"Authorization": "Bearer token-inventado"}
        )
        self.assertEqual(respuesta.status_code, 401)

    def test_token_vencido_devuelve_401(self):
        token_vencido = create_access_token(identity="1", expires_delta=timedelta(seconds=-1))
        respuesta = self.cliente_http.get(
            URL_PERFIL, headers={"Authorization": f"Bearer {token_vencido}"}
        )
        self.assertEqual(respuesta.status_code, 401)
