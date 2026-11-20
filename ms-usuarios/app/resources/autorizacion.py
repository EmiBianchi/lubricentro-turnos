from functools import wraps

from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request


def rol_requerido(*roles_permitidos: str):
    """Decorador que restringe un endpoint a ciertos roles (HU-04).

    Evita repetir "if rol != ..." en cada endpoint (DRY) y deja la regla visible
    en la firma del recurso. Sin token o con token inválido responde 401; con
    un token válido de otro rol, 403.

    :param roles_permitidos: nombres de rol que pueden acceder, p. ej. "admin".
    """
    def decorador(funcion):
        @wraps(funcion)
        def envoltura(*args, **kwargs):
            verify_jwt_in_request()
            if get_jwt().get("rol") not in roles_permitidos:
                return {"error": "No tiene permisos para esta operación."}, 403
            return funcion(*args, **kwargs)
        return envoltura
    return decorador


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
