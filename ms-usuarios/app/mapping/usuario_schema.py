from marshmallow import fields, validate

from app import ma


class UsuarioSchema(ma.Schema):
    """Convierte Usuario <-> JSON y valida los datos de entrada del registro."""

    id = fields.Integer(dump_only=True)
    nombre = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    # load_only: se recibe al registrar pero nunca se incluye en una respuesta (RNF-03).
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=1))
    # dump_only: si el pedido trae "rol", marshmallow lo rechaza como campo
    # desconocido (400); así nadie puede auto-asignarse el rol admin.
    rol = fields.String(attribute="rol.nombre", dump_only=True)
