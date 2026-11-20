from flask import Blueprint, request

from app.mapping import LoginSchema
from app.services.fabrica import crear_auth_service

auth_bp = Blueprint("auth", __name__)
login_schema = LoginSchema()


@auth_bp.route("/login", methods=["POST"])
def iniciar_sesion():
    """POST /api/v1/auth/login — devuelve un token JWT (HU-02)."""
    datos = login_schema.load(request.get_json(silent=True) or {})
    token = crear_auth_service().iniciar_sesion(datos["email"], datos["password"])
    return {"access_token": token}, 200
