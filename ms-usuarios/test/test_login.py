from caso_base import CasoBase
from flask_jwt_extended import decode_token


class LoginTestCase(CasoBase):
    """Criterios de aceptación de HU-02 (Iniciar sesión)."""

    def setUp(self):
        super().setUp()
        self.registrar(email="juan@mail.com", password="clave123")

    def test_credenciales_correctas_devuelven_token(self):
        respuesta = self.iniciar_sesion("juan@mail.com", "clave123")
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("access_token", respuesta.get_json())

    def test_password_incorrecta_devuelve_401(self):
        respuesta = self.iniciar_sesion("juan@mail.com", "incorrecta")
        self.assertEqual(respuesta.status_code, 401)

    def test_email_no_registrado_devuelve_401(self):
        respuesta = self.iniciar_sesion("nadie@mail.com", "clave123")
        self.assertEqual(respuesta.status_code, 401)

    def test_campos_faltantes_devuelven_400(self):
        respuesta = self.cliente_http.post("/api/v1/auth/login", json={})
        self.assertEqual(respuesta.status_code, 400)

    def test_el_token_tiene_fecha_de_expiracion(self):
        token = self.iniciar_sesion().get_json()["access_token"]
        datos = decode_token(token)
        self.assertIn("exp", datos)
        self.assertGreater(datos["exp"], datos["iat"])

    def test_el_token_identifica_al_usuario_y_su_rol(self):
        token = self.iniciar_sesion().get_json()["access_token"]
        datos = decode_token(token)
        self.assertEqual(datos["rol"], "cliente")
        self.assertTrue(datos["sub"])
