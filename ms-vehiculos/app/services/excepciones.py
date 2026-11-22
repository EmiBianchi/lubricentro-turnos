class ErrorDeNegocio(Exception):
    """Base de las reglas de negocio violadas. Los servicios no conocen HTTP:
    la capa resources traduce cada subclase a su código de respuesta."""


class PatenteYaRegistrada(ErrorDeNegocio):

    def __init__(self, patente: str):
        super().__init__(f"La patente {patente} ya está registrada.")


class VehiculoNoEncontrado(ErrorDeNegocio):

    def __init__(self, id: int):
        super().__init__(f"No existe el vehículo {id}.")


class VehiculoAjeno(ErrorDeNegocio):

    def __init__(self):
        # 403 y no 404: el vehículo existe pero pertenece a otro cliente (HU-07).
        super().__init__("El vehículo pertenece a otro cliente.")
