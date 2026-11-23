import unittest
from datetime import date, datetime, time, timedelta

from flask_jwt_extended import create_access_token

from app import create_app, db
from app.models import Ocupacion, Turno

URL_TURNOS = "/api/v1/turnos"
URL_DISPONIBILIDAD = f"{URL_TURNOS}/disponibilidad"

LUNES, SABADO, DOMINGO = 0, 5, 6


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
