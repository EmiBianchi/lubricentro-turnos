import unittest
from datetime import datetime, timezone

from flask_jwt_extended import create_access_token

from app import create_app, db
from app.models import Vehiculo

URL_VEHICULOS = "/api/v1/vehiculos"

VEHICULO_VALIDO = {
    "patente": "AB123CD",
    "tipo": "auto",
    "marca": "Ford",
    "modelo": "Fiesta",
    "anio": 2018,
}


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

    def registrar_vehiculo(self, usuario_id: int = 1, **cambios):
        """Llama al endpoint de registro con un vehículo válido, modificado por "cambios".

        :return: respuesta HTTP del cliente de pruebas de Flask.
        """
        return self.cliente_http.post(
            URL_VEHICULOS, json={**VEHICULO_VALIDO, **cambios},
            headers=self.encabezado_de(usuario_id),
        )

    def listar_vehiculos(self, usuario_id: int = 1):
        """Llama al endpoint de listado con el token del cliente indicado.

        :return: respuesta HTTP del cliente de pruebas de Flask.
        """
        return self.cliente_http.get(URL_VEHICULOS, headers=self.encabezado_de(usuario_id))

    def marcar_como_eliminado(self, vehiculo_id: int) -> None:
        """Completa deleted_at directamente en la base, sin pasar por la API.

        Permite probar que los listados ignoran los vehículos dados de baja sin
        depender del endpoint de baja (HU-08).
        """
        vehiculo = db.session.get(Vehiculo, vehiculo_id)
        vehiculo.deleted_at = datetime.now(timezone.utc)
        db.session.commit()
