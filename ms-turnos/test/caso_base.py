import unittest
from datetime import date, datetime, time, timedelta
from unittest.mock import patch

from flask_jwt_extended import create_access_token, decode_token

from app import create_app, db
from app.models import Ocupacion, Turno
from app.services.excepciones import ServicioVehiculosNoDisponible

URL_TURNOS = "/api/v1/turnos"
URL_DISPONIBILIDAD = f"{URL_TURNOS}/disponibilidad"

LUNES, SABADO, DOMINGO = 0, 5, 6

# Vehículos que ms-vehiculos (simulado) tiene registrados en cada test.
AUTO_DEL_CLIENTE_1 = 10
AUTO_DEL_CLIENTE_2 = 20


def proximo(dia_semana: int) -> date:
    """Próxima fecha que cae en ese día de la semana, entre mañana y 7 días.

    Las fechas se calculan desde hoy y no se escriben fijas: así los tests siguen
    siendo "futuros" sin importar el día en que se ejecuten.

    :param dia_semana: 0 = lunes ... 6 = domingo (igual que date.weekday()).
    """
    hoy = date.today()
    return hoy + timedelta(days=(dia_semana - hoy.weekday() - 1) % 7 + 1)


def ayer() -> date:
    return date.today() - timedelta(days=1)


class ClienteVehiculosFalso:
    """Reemplaza a ms-vehiculos en los tests: no hace falta levantarlo (DIP).

    Identifica al cliente decodificando el token, igual que ms-vehiculos, y solo
    devuelve vehículos de ese cliente: así se prueba de verdad la regla de dueño.
    """

    def __init__(self):
        self.vehiculos = []
        self.caido = False

    def agregar(self, id: int, usuario_id: int, tipo: str = "auto", patente: str = "AB123CD"):
        self.vehiculos.append({"id": id, "usuario_id": usuario_id, "tipo": tipo, "patente": patente})

    def obtener_vehiculo(self, vehiculo_id: int, token: str) -> dict | None:
        if self.caido:
            raise ServicioVehiculosNoDisponible()
        usuario_id = int(decode_token(token)["sub"])
        return next((v for v in self.vehiculos
                     if v["id"] == vehiculo_id and v["usuario_id"] == usuario_id), None)


class CasoBase(unittest.TestCase):
    """Base de los tests que necesitan la aplicación y la base de datos.

    Usa la configuración "testing" (SQLite en memoria): cada test parte de tablas
    vacías y al terminar se destruye todo, sin tocar la base de PostgreSQL.
    """

    def setUp(self):
        self.app = create_app("testing")
        self.contexto = self.app.app_context()
        self.contexto.push()
        db.create_all()
        self.cliente_http = self.app.test_client()

        self.ms_vehiculos = ClienteVehiculosFalso()
        self.ms_vehiculos.agregar(AUTO_DEL_CLIENTE_1, usuario_id=1, patente="AB123CD")
        self.ms_vehiculos.agregar(AUTO_DEL_CLIENTE_2, usuario_id=2, patente="AC456DE")
        # La fábrica arma el cliente HTTP real; se reemplaza solo durante el test.
        parche = patch("app.services.fabrica.ClienteVehiculosHTTP", return_value=self.ms_vehiculos)
        parche.start()
        self.addCleanup(parche.stop)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.contexto.pop()

    def encabezado_de(self, usuario_id: int = 1, rol: str = "cliente") -> dict:
        """Arma el encabezado Authorization con un token como el que emite ms-usuarios.

        El token se firma con la clave de testing en lugar de pedirlo a ms-usuarios:
        así los tests de este microservicio no dependen de que el otro esté levantado.

        :return: diccionario de encabezados HTTP con el token Bearer.
        """
        token = create_access_token(identity=str(usuario_id), additional_claims={"rol": rol})
        return {"Authorization": f"Bearer {token}"}

    def consultar_disponibilidad(self, fecha: date | str):
        """Llama al endpoint de disponibilidad con el token de un cliente.

        :return: respuesta HTTP del cliente de pruebas de Flask.
        """
        fecha = fecha.isoformat() if isinstance(fecha, date) else fecha
        return self.cliente_http.get(URL_DISPONIBILIDAD, query_string={"fecha": fecha},
                                     headers=self.encabezado_de())

    def boxes_libres(self, fecha: date) -> dict[str, int]:
        """:return: {"08:00": boxes libres, ...} según el endpoint de disponibilidad."""
        horarios = self.consultar_disponibilidad(fecha).get_json()["horarios"]
        return {horario["hora"]: horario["boxes_libres"] for horario in horarios}

    def reservar(self, usuario_id: int = 1, vehiculo_id: int = AUTO_DEL_CLIENTE_1,
                 fecha: date | None = None, hora: str = "08:00"):
        """Llama al endpoint de reserva; por defecto, el próximo lunes a las 08:00.

        :return: respuesta HTTP del cliente de pruebas de Flask.
        """
        fecha = fecha or proximo(LUNES)
        return self.cliente_http.post(
            URL_TURNOS, json={"vehiculo_id": vehiculo_id, "fecha": fecha.isoformat(), "hora": hora},
            headers=self.encabezado_de(usuario_id),
        )

    def ocupar(self, fecha: date, horarios: list[time], box: int, usuario_id: int = 1) -> Turno:
        """Guarda un turno directamente en la base, sin pasar por la API.

        Permite preparar boxes ocupados para probar la disponibilidad sin depender
        del endpoint de reserva (HU-10).

        :param horarios: casilleros que ocupa el turno (uno para un turno común).
        :return: el turno guardado.
        """
        fin = (datetime.combine(fecha, horarios[-1]) + timedelta(minutes=30)).time()
        turno = Turno(
            fecha=fecha, hora_inicio=horarios[0], hora_fin=fin, box=box,
            usuario_id=usuario_id, vehiculo_id=1, patente="AB123CD", tipo_vehiculo="auto",
            ocupaciones=[Ocupacion(fecha=fecha, hora=hora, box=box) for hora in horarios],
        )
        db.session.add(turno)
        db.session.commit()
        return turno
