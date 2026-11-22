from caso_base import URL_VEHICULOS, VEHICULO_VALIDO, CasoBase

from app import db
from app.models import Vehiculo


class BajaVehiculoTestCase(CasoBase):
    """Criterios de aceptación de HU-08 (Dar de baja vehículo)."""

    def setUp(self):
        super().setUp()
        self.vehiculo_id = self.registrar_vehiculo(usuario_id=1).get_json()["id"]

    def dar_de_baja(self, usuario_id: int = 1, vehiculo_id: int | None = None):
        return self.cliente_http.delete(
            f"{URL_VEHICULOS}/{vehiculo_id or self.vehiculo_id}",
            headers=self.encabezado_de(usuario_id),
        )

    def test_el_dueno_da_de_baja_su_vehiculo(self):
        respuesta = self.dar_de_baja(usuario_id=1)
        self.assertEqual(respuesta.status_code, 204)

    def test_es_baja_logica_se_completa_deleted_at(self):
        self.dar_de_baja(usuario_id=1)
        vehiculo = db.session.get(Vehiculo, self.vehiculo_id)
        self.assertIsNotNone(vehiculo, "El registro no debe borrarse físicamente.")
        self.assertIsNotNone(vehiculo.deleted_at)

    def test_deja_de_aparecer_en_el_listado(self):
        self.dar_de_baja(usuario_id=1)
        self.assertEqual(self.listar_vehiculos(usuario_id=1).get_json(), [])

    def test_otro_cliente_recibe_403(self):
        respuesta = self.dar_de_baja(usuario_id=2)
        self.assertEqual(respuesta.status_code, 403)

    def test_otro_cliente_no_logra_la_baja(self):
        self.dar_de_baja(usuario_id=2)
        self.assertEqual(len(self.listar_vehiculos(usuario_id=1).get_json()), 1)

    def test_vehiculo_inexistente_devuelve_404(self):
        respuesta = self.dar_de_baja(usuario_id=1, vehiculo_id=999)
        self.assertEqual(respuesta.status_code, 404)

    def test_dar_de_baja_dos_veces_devuelve_404(self):
        self.dar_de_baja(usuario_id=1)
        respuesta = self.dar_de_baja(usuario_id=1)
        self.assertEqual(respuesta.status_code, 404)

    def test_sin_token_devuelve_401(self):
        respuesta = self.cliente_http.delete(f"{URL_VEHICULOS}/{self.vehiculo_id}")
        self.assertEqual(respuesta.status_code, 401)

    def test_no_se_puede_modificar_un_vehiculo_dado_de_baja(self):
        self.dar_de_baja(usuario_id=1)
        respuesta = self.cliente_http.put(
            f"{URL_VEHICULOS}/{self.vehiculo_id}", json=VEHICULO_VALIDO,
            headers=self.encabezado_de(1),
        )
        self.assertEqual(respuesta.status_code, 404)

    def test_la_patente_de_un_vehiculo_dado_de_baja_se_puede_volver_a_registrar(self):
        self.dar_de_baja(usuario_id=1)
        respuesta = self.registrar_vehiculo(usuario_id=2)
        self.assertEqual(respuesta.status_code, 201)
