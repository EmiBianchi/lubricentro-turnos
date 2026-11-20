from app import db
from app.models import Rol
from app.repository.base import RepositorioEscritura, RepositorioLectura


class RolRepository(RepositorioLectura, RepositorioEscritura):
    modelo = Rol

    def buscar_por_nombre(self, nombre: str) -> Rol | None:
        """:return: el rol con ese nombre, o None si no existe."""
        return db.session.scalars(db.select(Rol).filter_by(nombre=nombre)).first()
