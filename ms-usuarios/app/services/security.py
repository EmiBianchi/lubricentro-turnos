from abc import ABC, abstractmethod

from werkzeug.security import check_password_hash, generate_password_hash


class Encriptador(ABC):
    """Contrato para cifrar contraseñas.

    Los servicios dependen de esta abstracción (DIP). Si el algoritmo queda
    comprometido se agrega otra subclase sin tocar los servicios (OCP), y
    cualquier subclase reemplaza a otra sin cambios en quien la usa (LSP).
    """

    @abstractmethod
    def generar_hash(self, password: str) -> str:
        """:return: hash irreversible de la contraseña."""

    @abstractmethod
    def verificar(self, password: str, hash_guardado: str) -> bool:
        """:return: True si la contraseña corresponde al hash guardado."""


class EncriptadorWerkzeug(Encriptador):

    def generar_hash(self, password: str) -> str:
        return generate_password_hash(password)

    def verificar(self, password: str, hash_guardado: str) -> bool:
        return check_password_hash(hash_guardado, password)
