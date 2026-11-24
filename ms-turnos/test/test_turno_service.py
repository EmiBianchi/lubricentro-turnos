import unittest
from datetime import date, datetime, time

from app.models import Ocupacion
from app.repository import CasilleroOcupado
from app.services.excepciones import (
    DiaNoHabil,
    FechaPasada,
    HorarioFueraDeGrilla,
    SinBoxDisponible,
    VehiculoNoEncontrado,
)
from app.services.grilla_horaria import GrillaHoraria
from app.services.reglas_reserva import FabricaReglas
from app.services.turno_service import TurnoService

LUNES = date(2026, 11, 23)
MARTES = date(2026, 11, 24)
DOMINGO = date(2026, 11, 29)
AUTO = 10
CAMION = 30
TOKEN = "token-del-cliente"


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


class RepositorioTurnosFalso:
    """Guarda en memoria y registra las ocupaciones del turno en el repositorio de
    ocupaciones, como hace la base real por la composición Turno-Ocupacion."""

    def __init__(self, ocupaciones: RepositorioOcupacionesFalso):
        self.turnos = []
        self._ocupaciones = ocupaciones
        self.simular_reserva_simultanea = False

    def guardar(self, turno):
        if self.simular_reserva_simultanea:
            raise CasilleroOcupado()
        if turno not in self.turnos:
            turno.id = len(self.turnos) + 1
            turno.deleted_at = None
            self.turnos.append(turno)
            self._ocupaciones.ocupaciones.extend(turno.ocupaciones)
        return turno

    def listar_por_usuario(self, usuario_id):
        return [t for t in self.turnos if t.usuario_id == usuario_id and t.deleted_at is None]


class ClienteVehiculosFalso:
    """Reemplaza la consulta HTTP a ms-vehiculos (DIP): devuelve el vehículo solo
    si está en el diccionario, como si ms-vehiculos lo hubiera encontrado."""

    def __init__(self, vehiculos: dict):
        self.vehiculos = vehiculos
        self.tokens_recibidos = []

    def obtener_vehiculo(self, vehiculo_id, token):
        self.tokens_recibidos.append(token)
        return self.vehiculos.get(vehiculo_id)


class TurnoServiceTestCase(unittest.TestCase):

    def setUp(self):
        self.ocupaciones = RepositorioOcupacionesFalso()
        self.turnos = RepositorioTurnosFalso(self.ocupaciones)
        self.vehiculos = ClienteVehiculosFalso(
            {AUTO: {"id": AUTO, "tipo": "auto", "patente": "AB123CD"},
             CAMION: {"id": CAMION, "tipo": "camion", "patente": "AD789EF"}})
        # "Ahora" es el lunes 23/11/2026 a las 10:00.
        self.reloj = RelojFijo(datetime(2026, 11, 23, 10, 0))
        self.servicio = TurnoService(self.turnos, self.ocupaciones, self.vehiculos,
                                     GrillaHoraria(), FabricaReglas(), self.reloj)

    def libres_por_hora(self, fecha: date) -> dict:
        return {h["hora"]: h["boxes_libres"] for h in self.servicio.consultar_disponibilidad(fecha)}

    def reservar(self, fecha=MARTES, hora=time(8, 0), vehiculo_id=AUTO, usuario_id=1):
        return self.servicio.reservar(usuario_id, vehiculo_id, fecha, hora, TOKEN)

    # HU-09 — Consultar disponibilidad

    def test_disponibilidad_descuenta_las_ocupaciones_del_horario(self):
        self.ocupaciones.ocupaciones.append(Ocupacion(fecha=MARTES, hora=time(9, 0), box=1))
        libres = self.libres_por_hora(MARTES)
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

    # HU-10 — Reservar turno común

    def test_reservar_asigna_el_primer_box_libre(self):
        self.assertEqual(self.reservar().box, 1)
        self.assertEqual(self.reservar().box, 2)

    def test_reservar_completa_hora_fin_patente_y_tipo(self):
        turno = self.reservar(hora=time(12, 30))
        self.assertEqual(turno.hora_fin, time(13, 0))
        self.assertEqual(turno.patente, "AB123CD")
        self.assertEqual(turno.tipo_vehiculo, "auto")

    def test_reservar_un_turno_comun_ocupa_un_solo_casillero(self):
        turno = self.reservar()
        self.assertEqual(len(turno.ocupaciones), 1)

    def test_reservar_reenvia_el_token_a_ms_vehiculos(self):
        self.reservar()
        self.assertEqual(self.vehiculos.tokens_recibidos, [TOKEN])

    def test_reservar_con_los_dos_boxes_ocupados_lanza_excepcion(self):
        self.reservar()
        self.reservar()
        with self.assertRaises(SinBoxDisponible):
            self.reservar()

    def test_reservar_un_domingo_lanza_excepcion(self):
        with self.assertRaises(DiaNoHabil):
            self.reservar(fecha=DOMINGO)

    def test_reservar_un_horario_de_hoy_que_ya_paso_lanza_excepcion(self):
        with self.assertRaises(FechaPasada):
            self.reservar(fecha=LUNES, hora=time(9, 30))

    def test_reservar_hoy_un_horario_futuro_es_valido(self):
        self.assertEqual(self.reservar(fecha=LUNES, hora=time(10, 30)).box, 1)

    def test_reservar_fuera_de_la_grilla_lanza_excepcion(self):
        with self.assertRaises(HorarioFueraDeGrilla):
            self.reservar(hora=time(14, 0))

    def test_reservar_un_vehiculo_que_no_es_del_cliente_lanza_excepcion(self):
        with self.assertRaises(VehiculoNoEncontrado):
            self.reservar(vehiculo_id=999)

    def test_reserva_simultanea_rechazada_por_la_base_lanza_sin_box_disponible(self):
        self.turnos.simular_reserva_simultanea = True
        with self.assertRaises(SinBoxDisponible):
            self.reservar()

    # HU-11 — Reservar turno de camión

    def test_camion_de_la_manana_termina_a_las_1300_y_ocupa_10_casilleros(self):
        turno = self.reservar(vehiculo_id=CAMION, hora=time(8, 0))
        self.assertEqual(turno.hora_fin, time(13, 0))
        self.assertEqual(len(turno.ocupaciones), 10)
        self.assertTrue(all(ocupacion.box == turno.box for ocupacion in turno.ocupaciones))

    def test_camion_de_la_tarde_termina_a_las_2030(self):
        turno = self.reservar(vehiculo_id=CAMION, hora=time(16, 30))
        self.assertEqual(turno.hora_fin, time(20, 30))

    def test_camion_usa_el_box_que_tiene_toda_la_franja_libre(self):
        self.ocupaciones.ocupaciones.append(Ocupacion(fecha=MARTES, hora=time(12, 0), box=1))
        self.assertEqual(self.reservar(vehiculo_id=CAMION, hora=time(8, 0)).box, 2)

    def test_camion_sin_un_box_con_la_franja_completa_libre_lanza_excepcion(self):
        self.ocupaciones.ocupaciones.append(Ocupacion(fecha=MARTES, hora=time(12, 0), box=1))
        self.ocupaciones.ocupaciones.append(Ocupacion(fecha=MARTES, hora=time(9, 30), box=2))
        with self.assertRaises(SinBoxDisponible):
            self.reservar(vehiculo_id=CAMION, hora=time(8, 0))

    def test_camion_deja_el_box_sin_lugar_en_la_disponibilidad(self):
        self.reservar(vehiculo_id=CAMION, hora=time(8, 0))
        libres = self.libres_por_hora(MARTES)
        self.assertTrue(all(libres[hora] == 1 for hora in libres if hora < time(13, 0)))
        self.assertTrue(all(libres[hora] == 2 for hora in libres if hora > time(13, 0)))

    # HU-12 — Ver mis turnos

    def test_listar_de_usuario_devuelve_solo_sus_turnos(self):
        self.reservar(usuario_id=1)
        self.reservar(usuario_id=2)
        turnos = self.servicio.listar_de_usuario(2)
        self.assertEqual([turno.usuario_id for turno in turnos], [2])
