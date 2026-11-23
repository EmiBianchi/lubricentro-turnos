from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Turno
from app.repository.base import RepositorioBorrado, RepositorioEscritura, RepositorioLectura


class CasilleroOcupado(Exception):
    """La base rechazó el turno porque otra reserva ya tomó alguno de sus casilleros."""


class TurnoRepository(RepositorioLectura, RepositorioEscritura, RepositorioBorrado):
    modelo = Turno

    def guardar(self, turno: Turno) -> Turno:
        """Guarda el turno junto con sus ocupaciones en una sola transacción.

        :return: el turno con su id asignado.
        :raises CasilleroOcupado: si la restricción única (fecha, hora, box) de
            ocupaciones lo rechaza: otra reserva simultánea ganó el casillero.
        """
        try:
            return super().guardar(turno)
        except IntegrityError as error:
            # Tras un error, SQLAlchemy no acepta más operaciones en la sesión hasta
            # deshacer la transacción; además descarta el turno rechazado.
            db.session.rollback()
            raise CasilleroOcupado() from error
