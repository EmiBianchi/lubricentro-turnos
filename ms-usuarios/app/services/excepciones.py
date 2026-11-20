class ErrorDeNegocio(Exception):
    """Base de las reglas de negocio violadas. Los servicios no conocen HTTP:
    la capa resources traduce cada subclase a su código de respuesta."""


class EmailYaRegistrado(ErrorDeNegocio):

    def __init__(self, email: str):
        super().__init__(f"El email {email} ya está registrado.")
