import unittest
from datetime import time

from app.services.excepciones import HorarioFueraDeGrilla, TipoVehiculoNoAdmitido
from app.services.grilla_horaria import Franja, GrillaHoraria
from app.services.reglas_reserva import FabricaReglas, ReglaTurnoComun


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


class FabricaReglasTestCase(unittest.TestCase):

    def test_motos_autos_y_camionetas_usan_la_regla_comun(self):
        for tipo in ("moto", "auto", "camioneta"):
            with self.subTest(tipo=tipo):
                self.assertIsInstance(FabricaReglas().crear(tipo), ReglaTurnoComun)

    def test_tipo_desconocido_lanza_excepcion(self):
        with self.assertRaises(TipoVehiculoNoAdmitido):
            FabricaReglas().crear("bicicleta")
