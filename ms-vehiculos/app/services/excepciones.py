class ErrorDeNegocio(Exception):
    """Base de las reglas de negocio violadas. Los servicios no conocen HTTP:
    la capa resources traduce cada subclase a su código de respuesta."""


class PatenteYaRegistrada(ErrorDeNegocio):

    def __init__(self, patente: str):
        super().__init__(f"La patente {patente} ya está registrada.")
