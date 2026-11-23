from datetime import timedelta

from caso_base import (
    AUTO_DEL_CLIENTE_1,
    AUTO_DEL_CLIENTE_2,
    CAMION_DEL_CLIENTE_1,
    LUNES,
    SABADO,
    URL_TURNOS,
    CasoBase,
    proximo,
)


class VerMisTurnosTestCase(CasoBase):
    """Criterios de aceptación de HU-12 (Ver mis turnos)."""

    def test_devuelve_200_con_los_turnos_del_cliente(self):
        self.reservar(usuario_id=1, hora="09:00")
        respuesta = self.listar_mis_turnos(usuario_id=1)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.get_json()), 1)

    def test_sin_turnos_devuelve_lista_vacia(self):
        self.assertEqual(self.listar_mis_turnos().get_json(), [])

    def test_devuelve_solo_los_turnos_del_cliente_del_token(self):
        self.reservar(usuario_id=1, vehiculo_id=AUTO_DEL_CLIENTE_1, hora="09:00")
        self.reservar(usuario_id=2, vehiculo_id=AUTO_DEL_CLIENTE_2, hora="09:00")
        turnos = self.listar_mis_turnos(usuario_id=2).get_json()
        self.assertEqual(len(turnos), 1)
        self.assertEqual(turnos[0]["usuario_id"], 2)

    def test_muestra_fecha_hora_box_y_vehiculo(self):
        fecha = proximo(LUNES)
        self.reservar(fecha=fecha, hora="10:30")
        turno = self.listar_mis_turnos().get_json()[0]
        self.assertEqual(turno["fecha"], fecha.isoformat())
        self.assertEqual(turno["hora_inicio"], "10:30")
        self.assertEqual(turno["hora_fin"], "11:00")
        self.assertEqual(turno["box"], 1)
        self.assertEqual(turno["vehiculo_id"], AUTO_DEL_CLIENTE_1)
        self.assertEqual(turno["patente"], "AB123CD")
        self.assertEqual(turno["tipo_vehiculo"], "auto")

    def test_no_muestra_turnos_cancelados(self):
        turno_id = self.reservar(hora="09:00").get_json()["id"]
        self.reservar(hora="10:00")
        self.marcar_como_cancelado(turno_id)
        turnos = self.listar_mis_turnos().get_json()
        self.assertEqual([turno["hora_inicio"] for turno in turnos], ["10:00"])

    def test_ordena_por_fecha_y_hora(self):
        lunes = proximo(LUNES)
        sabado = proximo(SABADO)
        posterior, anterior = sorted([lunes, sabado], reverse=True)
        self.reservar(fecha=posterior, hora="09:00")
        self.reservar(fecha=anterior, hora="17:00")
        self.reservar(fecha=anterior, hora="08:00", vehiculo_id=CAMION_DEL_CLIENTE_1)
        turnos = self.listar_mis_turnos().get_json()
        self.assertEqual([(t["fecha"], t["hora_inicio"]) for t in turnos], [
            (anterior.isoformat(), "08:00"),
            (anterior.isoformat(), "17:00"),
            (posterior.isoformat(), "09:00"),
        ])

    def test_incluye_turnos_de_distintas_semanas(self):
        fecha = proximo(LUNES)
        self.reservar(fecha=fecha)
        self.reservar(fecha=fecha + timedelta(days=7))
        self.assertEqual(len(self.listar_mis_turnos().get_json()), 2)

    def test_sin_token_devuelve_401(self):
        self.assertEqual(self.cliente_http.get(URL_TURNOS).status_code, 401)
