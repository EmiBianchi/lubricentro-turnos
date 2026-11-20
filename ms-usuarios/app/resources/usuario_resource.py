from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.mapping import UsuarioSchema
from app.models import ROL_ADMIN
from app.resources.autorizacion import rol_requerido
from app.services.fabrica import crear_usuario_service

usuario_bp = Blueprint("usuarios", __name__)
usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)


@usuario_bp.route("", methods=["POST"])
def registrar():
    """POST /api/v1/usuarios — registro público de clientes (HU-01)."""
    # silent=True: un cuerpo vacío o que no es JSON llega como {} y marshmallow
    # responde 400 indicando los campos obligatorios, en vez de un error genérico.
    datos = usuario_schema.load(request.get_json(silent=True) or {})
    usuario = crear_usuario_service().registrar(**datos)
    return usuario_schema.dump(usuario), 201


@usuario_bp.route("", methods=["GET"])
@rol_requerido(ROL_ADMIN)
def listar():
    """GET /api/v1/usuarios — listado de usuarios, solo administrador (HU-04)."""
    return usuarios_schema.dump(crear_usuario_service().listar()), 200


@usuario_bp.route("/perfil", methods=["GET"])
@jwt_required()
def ver_perfil():
    """GET /api/v1/usuarios/perfil — datos del dueño del token (HU-03)."""
    # El id sale del token y no de la URL: un cliente no puede pedir el perfil de otro.
    usuario = crear_usuario_service().obtener(int(get_jwt_identity()))
    return usuario_schema.dump(usuario), 200
