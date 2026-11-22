from app import db
from app.models import Vehiculo
from app.repository.base import RepositorioEscritura, RepositorioLectura


class VehiculoRepository(RepositorioLectura, RepositorioEscritura):
    modelo = Vehiculo

    def buscar_por_patente(self, patente: str) -> Vehiculo | None:
        """:return: el vehículo activo con esa patente, o None si no existe.

        Ignora los dados de baja: su patente queda libre para registrarse de nuevo.
        """
        consulta = db.select(Vehiculo).filter_by(patente=patente, deleted_at=None)
        return db.session.scalars(consulta).first()
