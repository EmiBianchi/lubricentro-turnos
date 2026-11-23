from datetime import time

from caso_base import DOMINGO, LUNES, SABADO, URL_DISPONIBILIDAD, CasoBase, ayer, proximo

HORARIOS_DE_UN_DIA_HABIL = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30",
    "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30", "20:00",
]


class DisponibilidadTestCase(CasoBase):
    """Criterios de aceptación de HU-09 (Consultar disponibilidad)."""

    def test_dia_habil_devuelve_200_con_la_fecha_consultada(self):
        fecha = proximo(LUNES)
        respuesta = self.consultar_disponibilidad(fecha)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json()["fecha"], fecha.isoformat())

    def test_dia_habil_devuelve_los_horarios_de_ambas_franjas_cada_30_minutos(self):
        horarios = self.boxes_libres(proximo(LUNES))
        self.assertEqual(list(horarios), HORARIOS_DE_UN_DIA_HABIL)

    def test_el_sabado_tambien_devuelve_horarios(self):
        horarios = self.boxes_libres(proximo(SABADO))
        self.assertEqual(list(horarios), HORARIOS_DE_UN_DIA_HABIL)

    def test_sin_turnos_todos_los_horarios_tienen_2_boxes_libres(self):
        horarios = self.boxes_libres(proximo(LUNES))
        self.assertTrue(all(libres == 2 for libres in horarios.values()))

    def test_un_turno_deja_1_box_libre_solo_en_su_horario(self):
        fecha = proximo(LUNES)
        self.ocupar(fecha, [time(10, 0)], box=1)
        horarios = self.boxes_libres(fecha)
        self.assertEqual(horarios["10:00"], 1)
        self.assertEqual(horarios["09:30"], 2)
        self.assertEqual(horarios["10:30"], 2)

    def test_dos_turnos_en_el_mismo_horario_dejan_0_boxes_libres(self):
        fecha = proximo(LUNES)
        self.ocupar(fecha, [time(17, 0)], box=1)
        self.ocupar(fecha, [time(17, 0)], box=2)
        self.assertEqual(self.boxes_libres(fecha)["17:00"], 0)

    def test_los_turnos_de_otro_dia_no_afectan(self):
        self.ocupar(proximo(SABADO), [time(10, 0)], box=1)
        self.assertEqual(self.boxes_libres(proximo(LUNES))["10:00"], 2)

    def test_un_domingo_no_devuelve_horarios(self):
        respuesta = self.consultar_disponibilidad(proximo(DOMINGO))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json()["horarios"], [])

    def test_una_fecha_pasada_devuelve_400(self):
        respuesta = self.consultar_disponibilidad(ayer())
        self.assertEqual(respuesta.status_code, 400)

    def test_sin_fecha_devuelve_400(self):
        respuesta = self.cliente_http.get(URL_DISPONIBILIDAD, headers=self.encabezado_de())
        self.assertEqual(respuesta.status_code, 400)

    def test_fecha_con_formato_invalido_devuelve_400(self):
        for fecha in ("30/11/2026", "mañana", "2026-13-40"):
            with self.subTest(fecha=fecha):
                self.assertEqual(self.consultar_disponibilidad(fecha).status_code, 400)

    def test_sin_token_devuelve_401(self):
        respuesta = self.cliente_http.get(URL_DISPONIBILIDAD,
                                          query_string={"fecha": proximo(LUNES).isoformat()})
        self.assertEqual(respuesta.status_code, 401)
