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

    def listar_por_usuario(self, usuario_id: int) -> list[Vehiculo]:
        """:return: los vehículos activos del usuario, del más antiguo al más nuevo.

        El filtro por deleted_at se hace en la consulta y no en el servicio: así
        nunca se traen a memoria vehículos que no se van a mostrar.
        """
        consulta = (db.select(Vehiculo)
                    .filter_by(usuario_id=usuario_id, deleted_at=None)
                    .order_by(Vehiculo.id))
        return list(db.session.scalars(consulta))
