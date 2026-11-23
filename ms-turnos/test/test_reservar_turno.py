from datetime import time

from caso_base import (
    AUTO_DEL_CLIENTE_1,
    AUTO_DEL_CLIENTE_2,
    DOMINGO,
    LUNES,
    SABADO,
    URL_TURNOS,
    CasoBase,
    ayer,
    proximo,
)

from app.models import Ocupacion, Turno
from app.repository import CasilleroOcupado, TurnoRepository


class ReservarTurnoComunTestCase(CasoBase):
    """Criterios de aceptación de HU-10 (Reservar turno común)."""

    def test_reserva_exitosa_devuelve_201_con_el_turno(self):
        fecha = proximo(LUNES)
        respuesta = self.reservar(fecha=fecha, hora="09:30")
        self.assertEqual(respuesta.status_code, 201)
        turno = respuesta.get_json()
        self.assertIn("id", turno)
        self.assertEqual(turno["fecha"], fecha.isoformat())
        self.assertEqual(turno["hora_inicio"], "09:30")
        self.assertEqual(turno["hora_fin"], "10:00")
        self.assertEqual(turno["vehiculo_id"], AUTO_DEL_CLIENTE_1)
        self.assertEqual(turno["patente"], "AB123CD")
        self.assertEqual(turno["tipo_vehiculo"], "auto")

    def test_queda_asociado_al_cliente_del_token(self):
        respuesta = self.reservar(usuario_id=2, vehiculo_id=AUTO_DEL_CLIENTE_2)
        self.assertEqual(respuesta.get_json()["usuario_id"], 2)

    def test_acepta_motos_autos_y_camionetas(self):
        for id, tipo, hora in ((31, "moto", "17:00"), (32, "auto", "17:30"),
                               (33, "camioneta", "18:00")):
            with self.subTest(tipo=tipo):
                self.ms_vehiculos.agregar(id, usuario_id=1, tipo=tipo)
                respuesta = self.reservar(vehiculo_id=id, fecha=proximo(SABADO), hora=hora)
                self.assertEqual(respuesta.status_code, 201)
                self.assertEqual(respuesta.get_json()["tipo_vehiculo"], tipo)

    def test_el_sabado_se_puede_reservar(self):
        self.assertEqual(self.reservar(fecha=proximo(SABADO)).status_code, 201)

    def test_el_domingo_devuelve_400(self):
        self.assertEqual(self.reservar(fecha=proximo(DOMINGO)).status_code, 400)

    def test_horario_fuera_de_la_grilla_devuelve_400(self):
        for hora in ("07:30", "08:15", "13:00", "14:00", "20:30"):
            with self.subTest(hora=hora):
                self.assertEqual(self.reservar(hora=hora).status_code, 400)

    def test_fecha_pasada_devuelve_400(self):
        self.assertEqual(self.reservar(fecha=ayer(), hora="10:00").status_code, 400)

    def test_vehiculo_de_otro_cliente_devuelve_404(self):
        respuesta = self.reservar(usuario_id=1, vehiculo_id=AUTO_DEL_CLIENTE_2)
        self.assertEqual(respuesta.status_code, 404)

    def test_vehiculo_inexistente_devuelve_404(self):
        self.assertEqual(self.reservar(vehiculo_id=999).status_code, 404)

    def test_si_ms_vehiculos_no_responde_devuelve_503(self):
        self.ms_vehiculos.caido = True
        self.assertEqual(self.reservar().status_code, 503)

    def test_asigna_automaticamente_el_box_1_y_luego_el_box_2(self):
        primero = self.reservar(usuario_id=1, vehiculo_id=AUTO_DEL_CLIENTE_1)
        segundo = self.reservar(usuario_id=2, vehiculo_id=AUTO_DEL_CLIENTE_2)
        self.assertEqual(primero.get_json()["box"], 1)
        self.assertEqual(segundo.get_json()["box"], 2)

    def test_con_los_2_boxes_ocupados_devuelve_409(self):
        self.reservar(usuario_id=1, vehiculo_id=AUTO_DEL_CLIENTE_1)
        self.reservar(usuario_id=2, vehiculo_id=AUTO_DEL_CLIENTE_2)
        self.ms_vehiculos.agregar(40, usuario_id=1, tipo="moto", patente="A123BCD")
        respuesta = self.reservar(usuario_id=1, vehiculo_id=40)
        self.assertEqual(respuesta.status_code, 409)

    def test_la_reserva_descuenta_un_box_en_la_disponibilidad(self):
        fecha = proximo(LUNES)
        self.reservar(fecha=fecha, hora="11:00")
        self.assertEqual(self.boxes_libres(fecha)["11:00"], 1)

    def test_campos_obligatorios(self):
        completo = {"vehiculo_id": AUTO_DEL_CLIENTE_1, "fecha": proximo(LUNES).isoformat(),
                    "hora": "08:00"}
        for campo in completo:
            with self.subTest(campo_faltante=campo):
                datos = {clave: valor for clave, valor in completo.items() if clave != campo}
                respuesta = self.cliente_http.post(URL_TURNOS, json=datos,
                                                   headers=self.encabezado_de())
                self.assertEqual(respuesta.status_code, 400)

    def test_formatos_invalidos_devuelven_400(self):
        for cambios in ({"fecha": "30/11/2026"}, {"hora": "8hs"}, {"vehiculo_id": "diez"}):
            with self.subTest(**cambios):
                datos = {"vehiculo_id": AUTO_DEL_CLIENTE_1, "fecha": proximo(LUNES).isoformat(),
                         "hora": "08:00", **cambios}
                respuesta = self.cliente_http.post(URL_TURNOS, json=datos,
                                                   headers=self.encabezado_de())
                self.assertEqual(respuesta.status_code, 400)

    def test_no_se_puede_elegir_el_box(self):
        datos = {"vehiculo_id": AUTO_DEL_CLIENTE_1, "fecha": proximo(LUNES).isoformat(),
                 "hora": "08:00", "box": 2}
        respuesta = self.cliente_http.post(URL_TURNOS, json=datos, headers=self.encabezado_de())
        self.assertEqual(respuesta.status_code, 400)

    def test_sin_token_devuelve_401(self):
        respuesta = self.cliente_http.post(URL_TURNOS, json={})
        self.assertEqual(respuesta.status_code, 401)


class ReservasSimultaneasTestCase(CasoBase):
    """RNF-02: la base de datos es la última barrera ante dos reservas simultáneas."""

    def turno_en(self, box: int) -> Turno:
        fecha, hora = proximo(LUNES), time(8, 0)
        return Turno(fecha=fecha, hora_inicio=hora, hora_fin=time(8, 30), box=box, usuario_id=1,
                     vehiculo_id=AUTO_DEL_CLIENTE_1, patente="AB123CD", tipo_vehiculo="auto",
                     ocupaciones=[Ocupacion(fecha=fecha, hora=hora, box=box)])

    def test_dos_turnos_en_el_mismo_box_y_horario_lanzan_casillero_ocupado(self):
        repositorio = TurnoRepository()
        repositorio.guardar(self.turno_en(box=1))
        with self.assertRaises(CasilleroOcupado):
            repositorio.guardar(self.turno_en(box=1))

    def test_el_turno_rechazado_no_queda_guardado(self):
        repositorio = TurnoRepository()
        repositorio.guardar(self.turno_en(box=1))
        with self.assertRaises(CasilleroOcupado):
            repositorio.guardar(self.turno_en(box=1))
        self.assertEqual(len(repositorio.listar()), 1)

    def test_el_mismo_horario_en_otro_box_si_se_acepta(self):
        repositorio = TurnoRepository()
        repositorio.guardar(self.turno_en(box=1))
        repositorio.guardar(self.turno_en(box=2))
        self.assertEqual(len(repositorio.listar()), 2)
