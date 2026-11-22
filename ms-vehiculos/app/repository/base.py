from abc import ABC, abstractmethod

from app import db


class RepositorioLectura(ABC):
    """Operaciones de consulta comunes a cualquier modelo.

    Lectura y escritura están separadas (ISP): cada repositorio hereda solo las
    capacidades que necesita, en lugar de una interfaz CRUD completa.
    """

    @property
    @abstractmethod
    def modelo(self) -> type:
        """Clase del modelo que administra el repositorio."""

    def buscar_por_id(self, id: int):
        """:return: la entidad con ese id, o None si no existe."""
        return db.session.get(self.modelo, id)

    def listar(self) -> list:
        """:return: todas las entidades del modelo."""
        return list(db.session.scalars(db.select(self.modelo)))


class RepositorioEscritura(ABC):
    """Operaciones de alta y modificación comunes a cualquier modelo."""

    @property
    @abstractmethod
    def modelo(self) -> type:
        """Clase del modelo que administra el repositorio."""

    def guardar(self, entidad):
        """Inserta o actualiza la entidad y confirma la transacción.

        :return: la misma entidad, ya con su id asignado.
        """
        db.session.add(entidad)
        db.session.commit()
        return entidad
