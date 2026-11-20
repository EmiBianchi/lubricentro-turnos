import unittest

from app import create_app, db
from app.services.fabrica import crear_usuario_service


class CasoBase(unittest.TestCase):
    """Base de los tests que necesitan la aplicación y la base de datos.

    Usa la configuración "testing" (SQLite en memoria): cada test parte de tablas
    vacías con los roles cargados y al terminar se destruye todo. Así los tests
    son independientes entre sí e inocuos (no tocan la base de PostgreSQL).
    """

    def setUp(self):
        self.app = create_app("testing")
        self.contexto = self.app.app_context()
        self.contexto.push()
        db.create_all()
        crear_usuario_service().crear_roles_iniciales()
        self.cliente_http = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.contexto.pop()

    def registrar(self, nombre: str = "Juan Perez", email: str = "juan@mail.com",
                  password: str = "clave123"):
        """Llama al endpoint de registro.

        :return: respuesta HTTP del cliente de pruebas de Flask.
        """
        return self.cliente_http.post(
            "/api/v1/usuarios",
            json={"nombre": nombre, "email": email, "password": password},
        )

    def iniciar_sesion(self, email: str = "juan@mail.com", password: str = "clave123"):
        """Llama al endpoint de login.

        :return: respuesta HTTP del cliente de pruebas de Flask.
        """
        return self.cliente_http.post(
            "/api/v1/auth/login", json={"email": email, "password": password}
        )

    def encabezado_con_token(self, email: str = "juan@mail.com",
                             password: str = "clave123") -> dict:
        """Inicia sesión y arma el encabezado Authorization para los endpoints protegidos.

        :return: diccionario de encabezados HTTP con el token Bearer.
        """
        token = self.iniciar_sesion(email, password).get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
