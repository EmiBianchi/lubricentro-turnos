from datetime import date, datetime, time, timedelta
from enum import Enum

DOMINGO = 6


class Franja(Enum):
    MANANA = "manana"
    TARDE = "tarde"


class GrillaHoraria:
    """Horario de atención del lubricentro (RN-01 a RN-04).

    Único lugar donde se definen días, franjas, duración y cantidad de boxes:
    disponibilidad, reservas y reglas por tipo de vehículo la consultan en vez de
    repetir los horarios (DRY). Cambiar el horario de atención es tocar solo aquí.
    """

    cantidad_boxes = 2
    duracion_minutos = 30
    # (inicio del primer turno, cierre). El cierre es el fin del último turno,
    # no un turno: 13:00 y 20:30 no se pueden reservar.
    _FRANJAS = {
        Franja.MANANA: (time(8, 0), time(13, 0)),
        Franja.TARDE: (time(16, 30), time(20, 30)),
    }

    def es_dia_habil(self, fecha: date) -> bool:
        """RN-01: se atiende de lunes a sábado."""
        return fecha.weekday() != DOMINGO

    def horarios_de_franja(self, franja: Franja) -> list[time]:
        """:return: inicio de cada turno de la franja, cada duracion_minutos."""
        inicio, cierre = self._FRANJAS[franja]
        horarios = []
        hora = inicio
        while hora < cierre:
            horarios.append(hora)
            hora = self.hora_fin(hora)
        return horarios

    def horarios_del_dia(self, fecha: date) -> list[time]:
        """:return: los horarios de ambas franjas, o una lista vacía si no es día hábil."""
        if not self.es_dia_habil(fecha):
            return []
        return [hora for franja in Franja for hora in self.horarios_de_franja(franja)]

    def franja_de(self, hora: time) -> Franja | None:
        """:return: la franja a la que pertenece el horario, o None si no es un
        horario de la grilla (p. ej. 08:15, 13:00 o 14:00)."""
        return next((franja for franja in Franja if hora in self.horarios_de_franja(franja)), None)

    def hora_fin(self, hora: time) -> time:
        """:return: la hora en que termina un turno que empieza a esa hora."""
        # time no admite sumas: se pasa por datetime con una fecha cualquiera.
        return (datetime.combine(date.min, hora) + timedelta(minutes=self.duracion_minutos)).time()
