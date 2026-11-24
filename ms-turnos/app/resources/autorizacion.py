from functools import wraps

from flask_jwt_extended import JWTManager, get_jwt, verify_jwt_in_request

# Nombre del rol tal como lo emite ms-usuarios en el claim "rol" del token.
ROL_ADMIN = "admin"


def rol_requerido(*roles_permitidos: str):
    """Decorador que restringe un endpoint a ciertos roles (HU-04 y HU-14).

    Copia del de ms-usuarios a propósito: cada microservicio se despliega por
    separado (RNF-05). El rol se lee del token, sin consultar a ms-usuarios. Sin
    token o con token inválido responde 401; con un token válido de otro rol, 403.

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
    criterio "requiere token válido" lo trata igual que la falta de token. Se
    repite lo de ms-usuarios a propósito: cada microservicio se despliega por
    separado (RNF-05) y no comparte código con los demás.
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
