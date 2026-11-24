from datetime import timedelta

from caso_base import (
    AUTO_DEL_CLIENTE_1,
    AUTO_DEL_CLIENTE_2,
    CAMION_DEL_CLIENTE_2,
    LUNES,
    URL_TURNOS,
    CasoBase,
    ayer,
    proximo,
)

URL_AGENDA = f"{URL_TURNOS}/agenda"
ADMIN = 99


class AgendaDelDiaTestCase(CasoBase):
    """Criterios de aceptación de HU-14 (Agenda del día)."""

    def setUp(self):
        super().setUp()
        self.fecha = proximo(LUNES)

    def agenda(self, fecha=None, usuario_id: int = ADMIN, rol: str = "admin"):
        fecha = fecha or self.fecha
        fecha = fecha.isoformat() if hasattr(fecha, "isoformat") else fecha
        return self.cliente_http.get(URL_AGENDA, query_string={"fecha": fecha},
                                     headers=self.encabezado_de(usuario_id, rol))

    def test_el_admin_obtiene_200(self):
        self.assertEqual(self.agenda().status_code, 200)

    def test_un_cliente_recibe_403(self):
        self.assertEqual(self.agenda(usuario_id=1, rol="cliente").status_code, 403)

    def test_sin_token_devuelve_401(self):
        respuesta = self.cliente_http.get(URL_AGENDA, query_string={"fecha": self.fecha.isoformat()})
        self.assertEqual(respuesta.status_code, 401)

    def test_incluye_los_turnos_de_todos_los_clientes(self):
        self.reservar(usuario_id=1, vehiculo_id=AUTO_DEL_CLIENTE_1, fecha=self.fecha, hora="09:00")
        self.reservar(usuario_id=2, vehiculo_id=AUTO_DEL_CLIENTE_2, fecha=self.fecha, hora="11:00")
        usuarios = {turno["usuario_id"] for turno in self.agenda().get_json()}
        self.assertEqual(usuarios, {1, 2})

    def test_ordena_por_hora_y_box(self):
        # Se reservan desordenados a propósito; el camión de las 08:00 queda en el
        # box 1 porque a esa altura la mañana está libre.
        self.reservar(usuario_id=1, vehiculo_id=AUTO_DEL_CLIENTE_1, fecha=self.fecha, hora="17:00")
        self.reservar(usuario_id=2, vehiculo_id=CAMION_DEL_CLIENTE_2, fecha=self.fecha, hora="08:00")
        self.reservar(usuario_id=1, vehiculo_id=AUTO_DEL_CLIENTE_1, fecha=self.fecha, hora="09:00")
        self.reservar(usuario_id=2, vehiculo_id=AUTO_DEL_CLIENTE_2, fecha=self.fecha, hora="17:00")
        orden = [(turno["hora_inicio"], turno["box"]) for turno in self.agenda().get_json()]
        self.assertEqual(orden, [("08:00", 1), ("09:00", 2), ("17:00", 1), ("17:00", 2)])

    def test_muestra_patente_y_tipo_de_cada_vehiculo(self):
        self.reservar(usuario_id=2, vehiculo_id=CAMION_DEL_CLIENTE_2, fecha=self.fecha, hora="16:30")
        turno = self.agenda().get_json()[0]
        self.assertEqual(turno["patente"], "AE012GH")
        self.assertEqual(turno["tipo_vehiculo"], "camion")
        self.assertEqual(turno["hora_fin"], "20:30")

    def test_no_incluye_turnos_cancelados(self):
        turno_id = self.reservar(fecha=self.fecha, hora="09:00").get_json()["id"]
        self.reservar(fecha=self.fecha, hora="10:00")
        self.marcar_como_cancelado(turno_id)
        horas = [turno["hora_inicio"] for turno in self.agenda().get_json()]
        self.assertEqual(horas, ["10:00"])

    def test_solo_incluye_los_turnos_de_ese_dia(self):
        self.reservar(fecha=self.fecha, hora="09:00")
        self.reservar(fecha=self.fecha + timedelta(days=1), hora="09:00")
        self.assertEqual(len(self.agenda().get_json()), 1)

    def test_dia_sin_turnos_devuelve_lista_vacia(self):
        self.assertEqual(self.agenda().get_json(), [])

    def test_se_puede_consultar_un_dia_pasado(self):
        self.assertEqual(self.agenda(fecha=ayer()).status_code, 200)

    def test_sin_fecha_devuelve_400(self):
        respuesta = self.cliente_http.get(URL_AGENDA, headers=self.encabezado_de(ADMIN, "admin"))
        self.assertEqual(respuesta.status_code, 400)

    def test_fecha_con_formato_invalido_devuelve_400(self):
        self.assertEqual(self.agenda(fecha="30/11/2026").status_code, 400)
