class ErrorDeNegocio(Exception):
    """Base de las reglas de negocio violadas. Los servicios no conocen HTTP:
    la capa resources traduce cada subclase a su código de respuesta."""


class EmailYaRegistrado(ErrorDeNegocio):

    def __init__(self, email: str):
        super().__init__(f"El email {email} ya está registrado.")


class CredencialesInvalidas(ErrorDeNegocio):

    def __init__(self):
        # Mismo mensaje para email inexistente y contraseña incorrecta: no se
        # revela a un atacante qué emails están registrados.
        super().__init__("Email o contraseña incorrectos.")


class UsuarioNoEncontrado(ErrorDeNegocio):

    def __init__(self, id: int):
        super().__init__(f"No existe el usuario {id}.")
