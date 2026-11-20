from caso_base import CasoBase

from app.repository import UsuarioRepository
from app.services.security import EncriptadorWerkzeug


class RegistroTestCase(CasoBase):
    """Criterios de aceptación de HU-01 (Registrar cuenta)."""

    def test_registro_exitoso_devuelve_201_y_rol_cliente(self):
        respuesta = self.registrar()
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.get_json()["rol"], "cliente")

    def test_la_respuesta_no_incluye_la_password(self):
        respuesta = self.registrar()
        self.assertNotIn("password", respuesta.get_json())

    def test_campos_obligatorios(self):
        completos = {"nombre": "Juan Perez", "email": "juan@mail.com", "password": "clave123"}
        for campo in completos:
            with self.subTest(campo_faltante=campo):
                datos = {clave: valor for clave, valor in completos.items() if clave != campo}
                respuesta = self.cliente_http.post("/api/v1/usuarios", json=datos)
                self.assertEqual(respuesta.status_code, 400)

    def test_campos_vacios_devuelven_400(self):
        respuesta = self.registrar(nombre="", password="")
        self.assertEqual(respuesta.status_code, 400)

    def test_email_con_formato_invalido_devuelve_400(self):
        respuesta = self.registrar(email="no-es-un-email")
        self.assertEqual(respuesta.status_code, 400)

    def test_email_ya_registrado_devuelve_409(self):
        self.registrar()
        respuesta = self.registrar(nombre="Otro Nombre")
        self.assertEqual(respuesta.status_code, 409)

    def test_la_password_se_guarda_cifrada(self):
        self.registrar(password="clave123")
        usuario = UsuarioRepository().buscar_por_email("juan@mail.com")
        self.assertNotEqual(usuario.password, "clave123")
        self.assertTrue(EncriptadorWerkzeug().verificar("clave123", usuario.password))
