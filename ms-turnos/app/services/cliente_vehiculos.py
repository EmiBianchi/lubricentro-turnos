from abc import ABC, abstractmethod

import requests

from app.services.excepciones import ServicioVehiculosNoDisponible


class ClienteVehiculos(ABC):
    """Acceso a los vehículos de ms-vehiculos. TurnoService depende de esta
    abstracción (DIP): en los tests se reemplaza sin levantar ms-vehiculos."""

    @abstractmethod
    def obtener_vehiculo(self, vehiculo_id: int, token: str) -> dict | None:
        """Busca un vehículo activo del cliente dueño del token.

        :param token: JWT del cliente, sin el prefijo "Bearer".
        :return: el vehículo (id, patente, tipo, ...) o None si el cliente no lo tiene.
        :raises ServicioVehiculosNoDisponible: si ms-vehiculos no responde correctamente.
        """


class ClienteVehiculosHTTP(ClienteVehiculos):
    """Consulta a ms-vehiculos por HTTP y JSON (RNF-09)."""

    # Sin límite, un ms-vehiculos colgado dejaría la reserva esperando para siempre.
    TIEMPO_ESPERA_SEGUNDOS = 5

    def __init__(self, url_base: str):
        self._url_base = url_base.rstrip("/")

    def obtener_vehiculo(self, vehiculo_id: int, token: str) -> dict | None:
        # Se reenvía el token del cliente y se busca en SU listado: ms-vehiculos solo
        # devuelve vehículos activos del dueño del token, así que propiedad y baja
        # lógica se validan donde viven esos datos (RNF-01) y sin agregarle endpoints.
        try:
            respuesta = requests.get(
                f"{self._url_base}/api/v1/vehiculos",
                headers={"Authorization": f"Bearer {token}"},
                timeout=self.TIEMPO_ESPERA_SEGUNDOS,
            )
            respuesta.raise_for_status()
        except requests.RequestException as error:
            raise ServicioVehiculosNoDisponible() from error
        return next((vehiculo for vehiculo in respuesta.json() if vehiculo["id"] == vehiculo_id),
                    None)
