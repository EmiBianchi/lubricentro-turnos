import unittest

from app.models import ROL_CLIENTE
from app.services.excepciones import EmailYaRegistrado
from app.services.security import Encriptador
from app.services.usuario_service import ROLES_INICIALES, UsuarioService


class RepositorioUsuariosFalso:
    """Doble de prueba en memoria: permite probar UsuarioService sin base de datos (DIP)."""

    def __init__(self):
        self.usuarios = []

    def buscar_por_email(self, email):
        return next((u for u in self.usuarios if u.email == email), None)

    def guardar(self, usuario):
        self.usuarios.append(usuario)
        return usuario


class RepositorioRolesFalso:

    def __init__(self):
        self.roles = {}

    def buscar_por_nombre(self, nombre):
        return self.roles.get(nombre)

    def guardar(self, rol):
        self.roles[rol.nombre] = rol
        return rol


class EncriptadorFalso(Encriptador):

    def generar_hash(self, password):
        return f"hash-{password}"

    def verificar(self, password, hash_guardado):
        return hash_guardado == f"hash-{password}"


class UsuarioServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.usuario_repo = RepositorioUsuariosFalso()
        self.rol_repo = RepositorioRolesFalso()
        self.servicio = UsuarioService(self.usuario_repo, self.rol_repo, EncriptadorFalso())
        self.servicio.crear_roles_iniciales()

    def test_registrar_asigna_rol_cliente(self):
        usuario = self.servicio.registrar("Juan Perez", "juan@mail.com", "clave123")
        self.assertEqual(usuario.rol.nombre, ROL_CLIENTE)

    def test_registrar_guarda_password_cifrada(self):
        usuario = self.servicio.registrar("Juan Perez", "juan@mail.com", "clave123")
        self.assertEqual(usuario.password, "hash-clave123")

    def test_registrar_email_repetido_lanza_excepcion(self):
        self.servicio.registrar("Juan Perez", "juan@mail.com", "clave123")
        with self.assertRaises(EmailYaRegistrado):
            self.servicio.registrar("Otro Nombre", "juan@mail.com", "otraclave")

    def test_crear_roles_iniciales_no_duplica(self):
        self.servicio.crear_roles_iniciales()
        self.assertEqual(len(self.rol_repo.roles), len(ROLES_INICIALES))
