from flask import Blueprint, request

from app.mapping import UsuarioSchema
from app.services.fabrica import crear_usuario_service

usuario_bp = Blueprint("usuarios", __name__)
usuario_schema = UsuarioSchema()


@usuario_bp.route("", methods=["POST"])
def registrar():
    """POST /api/v1/usuarios — registro público de clientes (HU-01)."""
    # silent=True: un cuerpo vacío o que no es JSON llega como {} y marshmallow
    # responde 400 indicando los campos obligatorios, en vez de un error genérico.
    datos = usuario_schema.load(request.get_json(silent=True) or {})
    usuario = crear_usuario_service().registrar(**datos)
    return usuario_schema.dump(usuario), 201
