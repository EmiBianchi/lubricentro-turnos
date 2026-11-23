import unittest
from datetime import date, datetime, time

from app.models import Ocupacion
from app.services.excepciones import FechaPasada
from app.services.grilla_horaria import GrillaHoraria
from app.services.turno_service import TurnoService

LUNES = date(2026, 11, 23)
DOMINGO = date(2026, 11, 29)


class RelojFijo:
    """Doble del reloj: fija "ahora" para probar fechas y horarios pasados sin
    depender del momento en que se ejecuta el test."""

    def __init__(self, momento: datetime):
        self.momento = momento

    def ahora(self) -> datetime:
        return self.momento


class RepositorioOcupacionesFalso:
    """Doble de prueba en memoria: permite probar TurnoService sin base de datos (DIP)."""

    def __init__(self):
        self.ocupaciones = []

    def listar_por_fecha(self, fecha):
        return [ocupacion for ocupacion in self.ocupaciones if ocupacion.fecha == fecha]


class TurnoServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.ocupaciones = RepositorioOcupacionesFalso()
        # "Ahora" es el lunes 23/11/2026 a las 10:00.
        self.reloj = RelojFijo(datetime(2026, 11, 23, 10, 0))
        self.servicio = TurnoService(self.ocupaciones, GrillaHoraria(), self.reloj)

    def libres_por_hora(self, fecha: date) -> dict:
        return {h["hora"]: h["boxes_libres"] for h in self.servicio.consultar_disponibilidad(fecha)}

    def test_disponibilidad_descuenta_las_ocupaciones_del_horario(self):
        fecha = date(2026, 11, 24)
        self.ocupaciones.ocupaciones.append(Ocupacion(fecha=fecha, hora=time(9, 0), box=1))
        libres = self.libres_por_hora(fecha)
        self.assertEqual(libres[time(9, 0)], 1)
        self.assertEqual(libres[time(8, 0)], 2)

    def test_disponibilidad_de_una_fecha_pasada_lanza_excepcion(self):
        with self.assertRaises(FechaPasada):
            self.servicio.consultar_disponibilidad(date(2026, 11, 22))

    def test_disponibilidad_de_hoy_omite_los_horarios_que_ya_pasaron(self):
        libres = self.libres_por_hora(LUNES)
        self.assertNotIn(time(10, 0), libres)
        self.assertEqual(min(libres), time(10, 30))

    def test_disponibilidad_del_domingo_es_vacia(self):
        self.assertEqual(self.servicio.consultar_disponibilidad(DOMINGO), [])
