from datetime import datetime, timedelta, timezone

# Argentina no aplica horario de verano: un desfase fijo evita depender del paquete
# tzdata, que Windows no trae y que ZoneInfo necesita para "America/Argentina/...".
HORA_ARGENTINA = timezone(timedelta(hours=-3))


class Reloj:
    """Fuente de "ahora" inyectada en TurnoService (DIP): los tests la reemplazan
    por un reloj fijo para probar fechas y horarios pasados (RN-08)."""

    def ahora(self) -> datetime:
        """:return: fecha y hora actuales del lubricentro, sin zona horaria.

        Sin zona porque los turnos guardan fecha y hora locales: así se comparan
        directamente, sin importar la zona del servidor o del contenedor Docker.
        """
        return datetime.now(HORA_ARGENTINA).replace(tzinfo=None)
