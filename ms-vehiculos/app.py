import os

from app import create_app

app = create_app()


if __name__ == "__main__":
    # 0.0.0.0: acepta conexiones de otras máquinas y contenedores, no solo de localhost.
    app.run(host="0.0.0.0", port=int(os.getenv("PUERTO", "5002")))
