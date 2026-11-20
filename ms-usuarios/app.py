import os

from app import create_app
from app.services.fabrica import crear_usuario_service

app = create_app()


def inicializar_datos() -> None:
    """Carga los datos que el sistema necesita para funcionar: roles y administrador.

    Se ejecuta al arrancar con "python app.py" y no al importar el módulo:
    así los comandos "flask db ..." no intentan usar tablas que todavía no existen.
    El admin se crea aquí y no por registro público (HU-04); sus datos salen del
    .env para no dejar credenciales en el código (RNF-07).
    """
    with app.app_context():
        servicio = crear_usuario_service()
        servicio.crear_roles_iniciales()

        email_admin = os.getenv("ADMIN_EMAIL")
        password_admin = os.getenv("ADMIN_PASSWORD")
        if email_admin and password_admin:
            servicio.crear_admin_inicial(
                os.getenv("ADMIN_NOMBRE", "Administrador"), email_admin, password_admin
            )
        else:
            app.logger.warning("ADMIN_EMAIL o ADMIN_PASSWORD no están en el .env: "
                               "no se creó el administrador.")


if __name__ == "__main__":
    inicializar_datos()
    # 0.0.0.0: acepta conexiones de otras máquinas y contenedores, no solo de localhost.
    app.run(host="0.0.0.0", port=int(os.getenv("PUERTO", "5001")))
