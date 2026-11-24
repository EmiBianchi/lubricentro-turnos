from datetime import time

from caso_base import (
    AUTO_DEL_CLIENTE_1,
    AUTO_DEL_CLIENTE_2,
    CAMION_DEL_CLIENTE_1,
    CAMION_DEL_CLIENTE_2,
    LUNES,
    CasoBase,
    proximo,
)

HORARIOS_MANANA = ["08:00", "08:30", "09:00", "09:30", "10:00",
                   "10:30", "11:00", "11:30", "12:00", "12:30"]
HORARIOS_TARDE = ["16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00"]


class ReservarTurnoCamionTestCase(CasoBase):
    """Criterios de aceptación de HU-11 (Reservar turno de camión)."""

    def setUp(self):
        super().setUp()
        self.fecha = proximo(LUNES)

    def reservar_camion(self, hora: str, usuario_id: int = 1,
                        vehiculo_id: int = CAMION_DEL_CLIENTE_1):
        return self.reservar(usuario_id=usuario_id, vehiculo_id=vehiculo_id,
                             fecha=self.fecha, hora=hora)

    def test_a_las_0800_se_acepta_y_ocupa_hasta_las_1300(self):
        respuesta = self.reservar_camion("08:00")
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.get_json()["hora_inicio"], "08:00")
        self.assertEqual(respuesta.get_json()["hora_fin"], "13:00")
        self.assertEqual(respuesta.get_json()["tipo_vehiculo"], "camion")

    def test_a_las_1630_se_acepta_y_ocupa_hasta_las_2030(self):
        respuesta = self.reservar_camion("16:30")
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.get_json()["hora_fin"], "20:30")

    def test_en_cualquier_otro_horario_devuelve_400(self):
        for hora in ("08:30", "12:30", "17:00", "20:00", "14:00"):
            with self.subTest(hora=hora):
                self.assertEqual(self.reservar_camion(hora).status_code, 400)

    def test_mientras_dura_su_box_no_aparece_libre_en_la_disponibilidad(self):
        self.reservar_camion("08:00")
        libres = self.boxes_libres(self.fecha)
        for hora in HORARIOS_MANANA:
            with self.subTest(hora=hora):
                self.assertEqual(libres[hora], 1)
        for hora in HORARIOS_TARDE:
            with self.subTest(hora=hora):
                self.assertEqual(libres[hora], 2)

    def test_si_el_box_1_tiene_un_turno_en_la_franja_usa_el_box_2(self):
        self.ocupar(self.fecha, [time(12, 30)], box=1)
        respuesta = self.reservar_camion("08:00")
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.get_json()["box"], 2)

    def test_si_ningun_box_tiene_la_franja_libre_devuelve_409(self):
        self.ocupar(self.fecha, [time(11, 0)], box=1)
        self.ocupar(self.fecha, [time(9, 0)], box=2)
        self.assertEqual(self.reservar_camion("08:00").status_code, 409)

    def test_un_turno_en_la_otra_franja_no_impide_al_camion(self):
        self.ocupar(self.fecha, [time(17, 0)], box=1)
        self.ocupar(self.fecha, [time(17, 0)], box=2)
        self.assertEqual(self.reservar_camion("08:00").status_code, 201)

    def test_dos_camiones_ocupan_ambos_boxes_y_un_tercero_recibe_409(self):
        self.assertEqual(self.reservar_camion("08:00").status_code, 201)
        segundo = self.reservar_camion("08:00", usuario_id=2, vehiculo_id=CAMION_DEL_CLIENTE_2)
        self.assertEqual(segundo.get_json()["box"], 2)
        self.ms_vehiculos.agregar(80, usuario_id=1, tipo="camion", patente="AF345IJ")
        self.assertEqual(self.reservar_camion("08:00", vehiculo_id=80).status_code, 409)

    def test_con_un_camion_en_cada_box_un_auto_no_consigue_turno_en_la_franja(self):
        self.reservar_camion("08:00")
        self.reservar_camion("08:00", usuario_id=2, vehiculo_id=CAMION_DEL_CLIENTE_2)
        respuesta = self.reservar(vehiculo_id=AUTO_DEL_CLIENTE_1, fecha=self.fecha, hora="11:30")
        self.assertEqual(respuesta.status_code, 409)

    def test_con_un_camion_un_auto_usa_el_otro_box(self):
        self.reservar_camion("08:00")
        respuesta = self.reservar(usuario_id=2, vehiculo_id=AUTO_DEL_CLIENTE_2,
                                  fecha=self.fecha, hora="10:00")
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.get_json()["box"], 2)
