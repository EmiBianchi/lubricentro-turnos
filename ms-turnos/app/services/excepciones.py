from datetime import time


class ErrorDeNegocio(Exception):
    """Base de las reglas de negocio violadas. Los servicios no conocen HTTP:
    la capa resources traduce cada subclase a su código de respuesta."""


class FechaPasada(ErrorDeNegocio):

    def __init__(self):
        super().__init__("La fecha u horario indicado ya pasó.")


class DiaNoHabil(ErrorDeNegocio):

    def __init__(self):
        super().__init__("El lubricentro atiende de lunes a sábado.")


class HorarioFueraDeGrilla(ErrorDeNegocio):

    def __init__(self, hora: time):
        super().__init__(f"{hora:%H:%M} no es un horario de turno. Consultá la "
                         "disponibilidad del día para ver los horarios válidos.")


class HorarioNoPermitidoParaCamion(ErrorDeNegocio):

    def __init__(self, horarios_permitidos: list[time]):
        # Los horarios llegan desde la grilla para no repetirlos en el mensaje (DRY).
        permitidos = " o ".join(f"{hora:%H:%M}" for hora in horarios_permitidos)
        super().__init__(f"Los camiones solo pueden reservar a las {permitidos}.")


class VehiculoNoEncontrado(ErrorDeNegocio):

    def __init__(self, vehiculo_id: int):
        # 404 y no 403: ms-vehiculos solo informa los vehículos del cliente, así que
        # no se distingue (ni se revela) si el id existe a nombre de otra persona.
        super().__init__(f"No tenés registrado el vehículo {vehiculo_id}.")


class TipoVehiculoNoAdmitido(ErrorDeNegocio):

    def __init__(self, tipo: str):
        super().__init__(f"No hay una regla de reserva para el tipo de vehículo {tipo}.")


class SinBoxDisponible(ErrorDeNegocio):

    def __init__(self):
        super().__init__("No hay boxes libres en ese horario.")


class ServicioVehiculosNoDisponible(ErrorDeNegocio):

    def __init__(self):
        super().__init__("No se pudo consultar el vehículo. Intentá nuevamente en unos minutos.")
