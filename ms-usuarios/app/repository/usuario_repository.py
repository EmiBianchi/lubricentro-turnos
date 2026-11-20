from app import db
from app.models import Usuario
from app.repository.base import RepositorioEscritura, RepositorioLectura


class UsuarioRepository(RepositorioLectura, RepositorioEscritura):
    modelo = Usuario

    def buscar_por_email(self, email: str) -> Usuario | None:
        """:return: el usuario con ese email, o None si no existe."""
        return db.session.scalars(db.select(Usuario).filter_by(email=email)).first()
