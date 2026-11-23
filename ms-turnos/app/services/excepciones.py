class ErrorDeNegocio(Exception):
    """Base de las reglas de negocio violadas. Los servicios no conocen HTTP:
    la capa resources traduce cada subclase a su código de respuesta."""


class FechaPasada(ErrorDeNegocio):

    def __init__(self):
        super().__init__("La fecha u horario indicado ya pasó.")
