from app.models import Vehiculo
from app.services.excepciones import PatenteYaRegistrada


class VehiculoService:
    """Casos de uso de vehículos.

    Recibe el repositorio por constructor (DIP): en ejecución se inyecta el real
    (ver fabrica.py) y en los tests, un doble en memoria.
    """

    def __init__(self, vehiculo_repo):
        self._vehiculo_repo = vehiculo_repo

    def registrar(self, usuario_id: int, datos: dict) -> Vehiculo:
        """Registra un vehículo a nombre del cliente.

        :param usuario_id: id del cliente, tomado del token.
        :param datos: patente, tipo, marca, modelo y anio ya validados por el schema.
        :return: el vehículo creado.
        :raises PatenteYaRegistrada: si otro vehículo activo tiene esa patente.
        """
        self._validar_patente_libre(datos["patente"])
        return self._vehiculo_repo.guardar(Vehiculo(usuario_id=usuario_id, **datos))

    def listar_de_usuario(self, usuario_id: int) -> list[Vehiculo]:
        """:return: los vehículos activos del cliente; no incluye los dados de baja."""
        return self._vehiculo_repo.listar_por_usuario(usuario_id)

    def _validar_patente_libre(self, patente: str) -> None:
        if self._vehiculo_repo.buscar_por_patente(patente) is not None:
            raise PatenteYaRegistrada(patente)
