from datetime import date

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

    def eliminar(self, turno: Turno) -> None:
        """Cancela el turno con baja lógica y libera sus casilleros (RN-09).

        Las ocupaciones sí se borran: no son historial sino el bloqueo de boxes, y
        si quedaran, la restricción única impediría volver a reservar el horario.
        El turno conserva fecha, hora y box. Todo se confirma en un mismo commit.
        """
        # clear() + delete-orphan: SQLAlchemy borra las ocupaciones al confirmar.
        turno.ocupaciones.clear()
        super().eliminar(turno)

    def listar_por_usuario(self, usuario_id: int) -> list[Turno]:
        """:return: los turnos no cancelados del cliente, del más próximo al más lejano.

        El filtro por deleted_at se hace en la consulta y no en el servicio: así
        nunca se traen a memoria turnos que no se van a mostrar.
        """
        consulta = (db.select(Turno)
                    .filter_by(usuario_id=usuario_id, deleted_at=None)
                    .order_by(Turno.fecha, Turno.hora_inicio))
        return list(db.session.scalars(consulta))

    def listar_por_fecha(self, fecha: date) -> list[Turno]:
        """:return: los turnos no cancelados del día, de todos los clientes,
        ordenados por hora de inicio y box (HU-14)."""
        consulta = (db.select(Turno)
                    .filter_by(fecha=fecha, deleted_at=None)
                    .order_by(Turno.hora_inicio, Turno.box))
        return list(db.session.scalars(consulta))
