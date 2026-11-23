from datetime import date

from app import db
from app.models import Ocupacion
from app.repository.base import RepositorioLectura


class OcupacionRepository(RepositorioLectura):
    """Solo lectura (ISP): las ocupaciones se crean y se borran a través de su
    turno (composición), nunca por separado."""

    modelo = Ocupacion

    def listar_por_fecha(self, fecha: date) -> list[Ocupacion]:
        """:return: los casilleros tomados ese día por turnos no cancelados.

        Los turnos cancelados no dejan ocupaciones (ver TurnoRepository), así que
        no hace falta filtrar por deleted_at.
        """
        consulta = db.select(Ocupacion).filter_by(fecha=fecha)
        return list(db.session.scalars(consulta))
