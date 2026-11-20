from flask_jwt_extended import JWTManager


def registrar_manejadores_jwt(jwt: JWTManager) -> None:
    """Unifica las respuestas de autenticación en 401.

    Por defecto Flask-JWT-Extended responde 422 ante un token mal formado; el
    criterio "requiere token válido" lo trata igual que la falta de token.
    """

    @jwt.unauthorized_loader
    def sin_token(motivo: str):
        return {"error": "Se requiere un token de acceso."}, 401

    @jwt.invalid_token_loader
    def token_invalido(motivo: str):
        return {"error": "Token inválido."}, 401

    @jwt.expired_token_loader
    def token_vencido(encabezado: dict, datos: dict):
        return {"error": "El token venció. Iniciá sesión nuevamente."}, 401
