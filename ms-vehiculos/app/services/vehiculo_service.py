from app.models import Vehiculo
from app.services.excepciones import PatenteYaRegistrada, VehiculoAjeno, VehiculoNoEncontrado


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

    def obtener_de_usuario(self, id: int, usuario_id: int) -> Vehiculo:
        """Busca un vehículo activo y verifica que pertenezca al cliente.

        Punto único de control de propiedad: modificar y dar de baja lo reutilizan
        en lugar de repetir la verificación (DRY).

        :return: el vehículo.
        :raises VehiculoNoEncontrado: si no existe o ya fue dado de baja.
        :raises VehiculoAjeno: si pertenece a otro cliente.
        """
        vehiculo = self._vehiculo_repo.buscar_por_id(id)
        if vehiculo is None or vehiculo.deleted_at is not None:
            raise VehiculoNoEncontrado(id)
        if vehiculo.usuario_id != usuario_id:
            raise VehiculoAjeno()
        return vehiculo

    def modificar(self, id: int, usuario_id: int, datos: dict) -> Vehiculo:
        """Reemplaza los datos de un vehículo del cliente.

        :param datos: validados con el mismo schema que el registro (HU-07).
        :return: el vehículo modificado.
        :raises VehiculoNoEncontrado, VehiculoAjeno: ver obtener_de_usuario.
        :raises PatenteYaRegistrada: si la nueva patente es de otro vehículo activo.
        """
        vehiculo = self.obtener_de_usuario(id, usuario_id)
        self._validar_patente_libre(datos["patente"], id_propio=vehiculo.id)
        # Solo llegan los campos del schema: usuario_id es dump_only, así que el
        # dueño no puede cambiarse desde el pedido.
        for campo, valor in datos.items():
            setattr(vehiculo, campo, valor)
        return self._vehiculo_repo.guardar(vehiculo)

    def dar_de_baja(self, id: int, usuario_id: int) -> None:
        """Baja lógica de un vehículo del cliente (HU-08).

        :raises VehiculoNoEncontrado, VehiculoAjeno: ver obtener_de_usuario.
        """
        vehiculo = self.obtener_de_usuario(id, usuario_id)
        self._vehiculo_repo.eliminar(vehiculo)

    def _validar_patente_libre(self, patente: str, id_propio: int | None = None) -> None:
        # id_propio: al modificar, la patente actual del mismo vehículo no es un duplicado.
        existente = self._vehiculo_repo.buscar_por_patente(patente)
        if existente is not None and existente.id != id_propio:
            raise PatenteYaRegistrada(patente)
