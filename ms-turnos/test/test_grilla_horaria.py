import unittest
from datetime import date, time

from app.services.grilla_horaria import Franja, GrillaHoraria

LUNES = date(2026, 11, 23)
SABADO = date(2026, 11, 28)
DOMINGO = date(2026, 11, 29)


class GrillaHorariaTestCase(unittest.TestCase):
    """Reglas RN-01 a RN-04 sin base de datos ni HTTP."""

    def setUp(self):
        self.grilla = GrillaHoraria()

    def test_hay_2_boxes_y_turnos_de_30_minutos(self):
        self.assertEqual(self.grilla.cantidad_boxes, 2)
        self.assertEqual(self.grilla.duracion_minutos, 30)

    def test_franja_manana_va_de_0800_a_1230(self):
        horarios = self.grilla.horarios_de_franja(Franja.MANANA)
        self.assertEqual(horarios[0], time(8, 0))
        self.assertEqual(horarios[-1], time(12, 30))
        self.assertEqual(len(horarios), 10)

    def test_franja_tarde_va_de_1630_a_2000(self):
        horarios = self.grilla.horarios_de_franja(Franja.TARDE)
        self.assertEqual(horarios[0], time(16, 30))
        self.assertEqual(horarios[-1], time(20, 0))
        self.assertEqual(len(horarios), 8)

    def test_lunes_a_sabado_son_habiles_y_domingo_no(self):
        self.assertTrue(self.grilla.es_dia_habil(LUNES))
        self.assertTrue(self.grilla.es_dia_habil(SABADO))
        self.assertFalse(self.grilla.es_dia_habil(DOMINGO))

    def test_horarios_del_dia_habil_suma_ambas_franjas(self):
        self.assertEqual(len(self.grilla.horarios_del_dia(LUNES)), 18)

    def test_horarios_del_domingo_es_vacio(self):
        self.assertEqual(self.grilla.horarios_del_dia(DOMINGO), [])

    def test_hora_fin_suma_la_duracion_de_un_turno(self):
        self.assertEqual(self.grilla.hora_fin(time(12, 30)), time(13, 0))
        self.assertEqual(self.grilla.hora_fin(time(20, 0)), time(20, 30))
