from datetime import time

from caso_base import (
    AUTO_DEL_CLIENTE_2,
    CAMION_DEL_CLIENTE_1,
    LUNES,
    URL_TURNOS,
    CasoBase,
    ayer,
    proximo,
)

from app import db
from app.models import Ocupacion, Turno


class CancelarTurnoTestCase(CasoBase):
    """Criterios de aceptación de HU-13 (Cancelar turno)."""

    def setUp(self):
        super().setUp()
        self.fecha = proximo(LUNES)
        self.turno_id = self.reservar(usuario_id=1, fecha=self.fecha, hora="10:00").get_json()["id"]

    def cancelar(self, usuario_id: int = 1, turno_id: int | None = None):
        return self.cliente_http.delete(f"{URL_TURNOS}/{turno_id or self.turno_id}",
                                        headers=self.encabezado_de(usuario_id))

    def test_el_dueno_cancela_su_turno(self):
        self.assertEqual(self.cancelar(usuario_id=1).status_code, 204)

    def test_es_baja_logica_se_completa_deleted_at(self):
        self.cancelar()
        turno = db.session.get(Turno, self.turno_id)
        self.assertIsNotNone(turno, "El turno no debe borrarse físicamente.")
        self.assertIsNotNone(turno.deleted_at)

    def test_el_turno_cancelado_conserva_fecha_hora_y_box(self):
        self.cancelar()
        turno = db.session.get(Turno, self.turno_id)
        self.assertEqual(turno.fecha, self.fecha)
        self.assertEqual(turno.hora_inicio, time(10, 0))
        self.assertEqual(turno.box, 1)

    def test_el_horario_vuelve_a_aparecer_disponible(self):
        self.assertEqual(self.boxes_libres(self.fecha)["10:00"], 1)
        self.cancelar()
        self.assertEqual(self.boxes_libres(self.fecha)["10:00"], 2)

    def test_el_horario_liberado_se_puede_volver_a_reservar(self):
        self.cancelar()
        respuesta = self.reservar(usuario_id=2, vehiculo_id=AUTO_DEL_CLIENTE_2,
                                  fecha=self.fecha, hora="10:00")
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.get_json()["box"], 1)

    def test_se_borran_las_ocupaciones_del_turno(self):
        self.cancelar()
        ocupaciones = db.session.scalars(db.select(Ocupacion).filter_by(turno_id=self.turno_id))
        self.assertEqual(list(ocupaciones), [])

    def test_cancelar_un_camion_libera_toda_la_franja(self):
        camion_id = self.reservar(vehiculo_id=CAMION_DEL_CLIENTE_1, fecha=self.fecha,
                                  hora="16:30").get_json()["id"]
        self.cancelar(turno_id=camion_id)
        libres = self.boxes_libres(self.fecha)
        self.assertTrue(all(libres[hora] == 2 for hora in libres if hora >= "16:30"))

    def test_deja_de_aparecer_en_mis_turnos(self):
        self.cancelar()
        self.assertEqual(self.listar_mis_turnos().get_json(), [])

    def test_otro_cliente_recibe_403(self):
        self.assertEqual(self.cancelar(usuario_id=2).status_code, 403)

    def test_otro_cliente_no_logra_cancelarlo(self):
        self.cancelar(usuario_id=2)
        self.assertIsNone(db.session.get(Turno, self.turno_id).deleted_at)

    def test_turno_inexistente_devuelve_404(self):
        self.assertEqual(self.cancelar(turno_id=999).status_code, 404)

    def test_cancelar_dos_veces_devuelve_404(self):
        self.cancelar()
        self.assertEqual(self.cancelar().status_code, 404)

    def test_un_turno_pasado_no_se_puede_cancelar(self):
        pasado = self.ocupar(ayer(), [time(10, 0)], box=1, usuario_id=1)
        respuesta = self.cancelar(turno_id=pasado.id)
        self.assertEqual(respuesta.status_code, 400)
        self.assertIsNone(db.session.get(Turno, pasado.id).deleted_at)

    def test_sin_token_devuelve_401(self):
        respuesta = self.cliente_http.delete(f"{URL_TURNOS}/{self.turno_id}")
        self.assertEqual(respuesta.status_code, 401)
