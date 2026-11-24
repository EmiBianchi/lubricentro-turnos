import unittest
from datetime import time

from app.services.excepciones import (
    HorarioFueraDeGrilla,
    HorarioNoPermitidoParaCamion,
    TipoVehiculoNoAdmitido,
)
from app.services.grilla_horaria import Franja, GrillaHoraria
from app.services.reglas_reserva import FabricaReglas, ReglaTurnoCamion, ReglaTurnoComun


class ReglaTurnoComunTestCase(unittest.TestCase):
    """RN-05: motos, autos y camionetas ocupan un box durante 30 minutos."""

    def setUp(self):
        self.grilla = GrillaHoraria()
        self.regla = ReglaTurnoComun()

    def test_acepta_cualquier_horario_de_la_grilla(self):
        for hora in [h for franja in Franja for h in self.grilla.horarios_de_franja(franja)]:
            with self.subTest(hora=hora):
                self.regla.validar(hora, self.grilla)

    def test_rechaza_horarios_fuera_de_la_grilla(self):
        for hora in (time(7, 30), time(8, 15), time(13, 0), time(16, 0), time(20, 30)):
            with self.subTest(hora=hora):
                with self.assertRaises(HorarioFueraDeGrilla):
                    self.regla.validar(hora, self.grilla)

    def test_ocupa_solo_su_horario(self):
        self.assertEqual(self.regla.horarios_a_ocupar(time(9, 0), self.grilla), [time(9, 0)])


class ReglaTurnoCamionTestCase(unittest.TestCase):
    """RN-06 y RN-07: un camión solo empieza a las 08:00 o a las 16:30 y ocupa el
    box toda la franja."""

    def setUp(self):
        self.grilla = GrillaHoraria()
        self.regla = ReglaTurnoCamion()

    def test_acepta_el_inicio_de_cada_franja(self):
        for hora in (time(8, 0), time(16, 30)):
            with self.subTest(hora=hora):
                self.regla.validar(hora, self.grilla)

    def test_rechaza_cualquier_otro_horario(self):
        for hora in (time(8, 30), time(12, 30), time(17, 0), time(20, 0), time(14, 0)):
            with self.subTest(hora=hora):
                with self.assertRaises(HorarioNoPermitidoParaCamion):
                    self.regla.validar(hora, self.grilla)

    def test_a_la_manana_ocupa_de_0800_a_1230(self):
        horarios = self.regla.horarios_a_ocupar(time(8, 0), self.grilla)
        self.assertEqual(horarios, self.grilla.horarios_de_franja(Franja.MANANA))

    def test_a_la_tarde_ocupa_de_1630_a_2000(self):
        horarios = self.regla.horarios_a_ocupar(time(16, 30), self.grilla)
        self.assertEqual(horarios, self.grilla.horarios_de_franja(Franja.TARDE))


class FabricaReglasTestCase(unittest.TestCase):

    def test_motos_autos_y_camionetas_usan_la_regla_comun(self):
        for tipo in ("moto", "auto", "camioneta"):
            with self.subTest(tipo=tipo):
                self.assertIsInstance(FabricaReglas().crear(tipo), ReglaTurnoComun)

    def test_los_camiones_usan_la_regla_de_camion(self):
        self.assertIsInstance(FabricaReglas().crear("camion"), ReglaTurnoCamion)

    def test_tipo_desconocido_lanza_excepcion(self):
        with self.assertRaises(TipoVehiculoNoAdmitido):
            FabricaReglas().crear("bicicleta")
