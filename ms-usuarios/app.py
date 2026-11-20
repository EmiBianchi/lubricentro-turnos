import os

from app import create_app
from app.services.fabrica import crear_usuario_service

app = create_app()


def inicializar_datos() -> None:
    """Carga los datos que el sistema necesita para funcionar (roles).

    Se ejecuta al arrancar con "python app.py" y no al importar el módulo:
    así los comandos "flask db ..." no intentan usar tablas que todavía no existen.
    """
    with app.app_context():
        crear_usuario_service().crear_roles_iniciales()


if __name__ == "__main__":
    inicializar_datos()
    # 0.0.0.0: acepta conexiones de otras máquinas y contenedores, no solo de localhost.
    app.run(host="0.0.0.0", port=int(os.getenv("PUERTO", "5001")))
