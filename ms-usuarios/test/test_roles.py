from caso_base import CasoBase

from app.repository import UsuarioRepository

URL_USUARIOS = "/api/v1/usuarios"


class ControlPorRolesTestCase(CasoBase):
    """Criterios de aceptación de HU-04 (Control por roles).

    Función de administrador usada para verificar el control:
    GET /api/v1/usuarios (listado de usuarios).
    """

    def setUp(self):
        super().setUp()
        self.registrar(email="juan@mail.com", password="clave123")
        self.crear_admin(email="admin@lubricentro.com", password="admin123")

    def test_cliente_en_funcion_de_admin_recibe_403(self):
        respuesta = self.cliente_http.get(
            URL_USUARIOS, headers=self.encabezado_con_token("juan@mail.com", "clave123")
        )
        self.assertEqual(respuesta.status_code, 403)

    def test_admin_accede_a_su_funcion(self):
        respuesta = self.cliente_http.get(
            URL_USUARIOS, headers=self.encabezado_con_token("admin@lubricentro.com", "admin123")
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.get_json()), 2)

    def test_el_listado_no_incluye_passwords(self):
        respuesta = self.cliente_http.get(
            URL_USUARIOS, headers=self.encabezado_con_token("admin@lubricentro.com", "admin123")
        )
        for usuario in respuesta.get_json():
            self.assertNotIn("password", usuario)

    def test_funcion_de_admin_sin_token_devuelve_401(self):
        respuesta = self.cliente_http.get(URL_USUARIOS)
        self.assertEqual(respuesta.status_code, 401)

    def test_el_registro_publico_no_permite_elegir_rol_admin(self):
        respuesta = self.cliente_http.post(URL_USUARIOS, json={
            "nombre": "Intruso", "email": "intruso@mail.com",
            "password": "clave123", "rol": "admin",
        })
        self.assertEqual(respuesta.status_code, 400)
        self.assertIsNone(UsuarioRepository().buscar_por_email("intruso@mail.com"))

    def test_el_admin_inicial_puede_iniciar_sesion(self):
        respuesta = self.iniciar_sesion("admin@lubricentro.com", "admin123")
        self.assertEqual(respuesta.status_code, 200)
