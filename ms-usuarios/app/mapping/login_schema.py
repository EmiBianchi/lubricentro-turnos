from marshmallow import fields

from app import ma


class LoginSchema(ma.Schema):
    """Valida el pedido de inicio de sesión."""

    # String y no Email: un email con formato inválido tampoco está registrado,
    # así que responde 401 como cualquier credencial incorrecta.
    email = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
