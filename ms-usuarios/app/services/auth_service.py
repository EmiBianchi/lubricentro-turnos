from flask_jwt_extended import create_access_token

from app.services.excepciones import CredencialesInvalidas
from app.services.security import Encriptador


class AuthService:
    """Autenticación de usuarios. Separado de UsuarioService (SRP): emitir tokens
    es una responsabilidad distinta de administrar los datos del usuario."""

    def __init__(self, usuario_repo, encriptador: Encriptador):
        self._usuario_repo = usuario_repo
        self._encriptador = encriptador

    def iniciar_sesion(self, email: str, password: str) -> str:
        """Valida las credenciales y emite un token JWT con vencimiento.

        :param email: email registrado.
        :param password: contraseña en texto plano.
        :return: token JWT firmado.
        :raises CredencialesInvalidas: si el email no existe o la contraseña no coincide.
        """
        usuario = self._usuario_repo.buscar_por_email(email)
        if usuario is None or not self._encriptador.verificar(password, usuario.password):
            raise CredencialesInvalidas()

        # "sub" debe ser texto (estándar JWT). El rol viaja en el token para que
        # cualquier microservicio autorice sin consultar la base de ms-usuarios.
        return create_access_token(
            identity=str(usuario.id), additional_claims={"rol": usuario.rol.nombre}
        )
