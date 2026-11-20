from app.models import ROL_ADMIN, ROL_CLIENTE, Rol, Usuario
from app.services.excepciones import EmailYaRegistrado, UsuarioNoEncontrado
from app.services.security import Encriptador

ROLES_INICIALES = (ROL_CLIENTE, ROL_ADMIN)


class UsuarioService:
    """Casos de uso de usuarios.

    Recibe repositorios y encriptador por constructor (DIP): en ejecución se
    inyectan los reales (ver fabrica.py) y en los tests, dobles en memoria.
    """

    def __init__(self, usuario_repo, rol_repo, encriptador: Encriptador):
        self._usuario_repo = usuario_repo
        self._rol_repo = rol_repo
        self._encriptador = encriptador

    def registrar(self, nombre: str, email: str, password: str) -> Usuario:
        """Registra un cliente nuevo.

        :param nombre: nombre visible del cliente.
        :param email: email único, usado para iniciar sesión.
        :param password: contraseña en texto plano; se guarda solo su hash.
        :return: el usuario creado.
        :raises EmailYaRegistrado: si ya existe un usuario con ese email.
        """
        if self._usuario_repo.buscar_por_email(email) is not None:
            raise EmailYaRegistrado(email)
        # El registro público asigna siempre "cliente": ningún dato del pedido
        # puede elegir el rol (HU-01 y HU-04).
        return self._crear(nombre, email, password, ROL_CLIENTE)

    def listar(self) -> list[Usuario]:
        """:return: todos los usuarios. Función exclusiva del administrador (HU-04)."""
        return self._usuario_repo.listar()

    def obtener(self, id: int) -> Usuario:
        """:return: el usuario con ese id.
        :raises UsuarioNoEncontrado: si no existe (por ejemplo, token de un usuario borrado).
        """
        usuario = self._usuario_repo.buscar_por_id(id)
        if usuario is None:
            raise UsuarioNoEncontrado(id)
        return usuario

    def crear_roles_iniciales(self) -> None:
        """Crea los roles que falten. Es idempotente: puede ejecutarse en cada arranque."""
        for nombre in ROLES_INICIALES:
            if self._rol_repo.buscar_por_nombre(nombre) is None:
                self._rol_repo.guardar(Rol(nombre=nombre))

    def crear_admin_inicial(self, nombre: str, email: str, password: str) -> None:
        """Crea el administrador si todavía no existe.

        Es el único camino para obtener el rol admin: se invoca al arrancar el
        sistema con datos del .env, nunca desde un endpoint público (HU-04).
        """
        if self._usuario_repo.buscar_por_email(email) is None:
            self._crear(nombre, email, password, ROL_ADMIN)

    def _crear(self, nombre: str, email: str, password: str, nombre_rol: str) -> Usuario:
        # Alta común a clientes y admin (DRY): solo cambia el rol asignado.
        usuario = Usuario(
            nombre=nombre,
            email=email,
            password=self._encriptador.generar_hash(password),
            rol=self._rol_repo.buscar_por_nombre(nombre_rol),
        )
        return self._usuario_repo.guardar(usuario)
