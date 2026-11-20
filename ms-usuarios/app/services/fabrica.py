"""Armado de servicios con sus dependencias concretas (patrón Factory).

Es el único lugar que elige las implementaciones reales; los servicios solo
conocen las abstracciones que reciben por constructor (DIP).
"""
from app.repository import RolRepository, UsuarioRepository
from app.services.auth_service import AuthService
from app.services.security import EncriptadorWerkzeug
from app.services.usuario_service import UsuarioService


def crear_usuario_service() -> UsuarioService:
    return UsuarioService(UsuarioRepository(), RolRepository(), EncriptadorWerkzeug())


def crear_auth_service() -> AuthService:
    return AuthService(UsuarioRepository(), EncriptadorWerkzeug())
