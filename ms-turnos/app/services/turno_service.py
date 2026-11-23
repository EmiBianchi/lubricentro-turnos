from collections import Counter
from datetime import date, datetime

from app.services.excepciones import FechaPasada
from app.services.grilla_horaria import GrillaHoraria
from app.services.reloj import Reloj


class TurnoService:
    """Casos de uso de turnos.

    Recibe sus dependencias por constructor (DIP): en ejecución se inyectan las
    reales (ver fabrica.py) y en los tests, dobles en memoria y un reloj fijo.
    """

    def __init__(self, ocupacion_repo, grilla: GrillaHoraria, reloj: Reloj):
        self._ocupacion_repo = ocupacion_repo
        self._grilla = grilla
        self._reloj = reloj

    def consultar_disponibilidad(self, fecha: date) -> list[dict]:
        """Boxes libres de cada horario del día (HU-09).

        :param fecha: día a consultar.
        :return: [{"hora": time, "boxes_libres": int}, ...] en orden; vacía si es domingo.
        :raises FechaPasada: si la fecha es anterior a hoy.
        """
        ahora = self._reloj.ahora()
        if fecha < ahora.date():
            raise FechaPasada()
        # Hoy se omiten los horarios que ya empezaron: no se podrían reservar (RN-08).
        horarios = [hora for hora in self._grilla.horarios_del_dia(fecha)
                    if datetime.combine(fecha, hora) > ahora]
        ocupados = Counter(ocupacion.hora for ocupacion in self._ocupacion_repo.listar_por_fecha(fecha))
        return [{"hora": hora, "boxes_libres": self._grilla.cantidad_boxes - ocupados[hora]}
                for hora in horarios]
