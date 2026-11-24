# Imagen de ms-usuarios. Cada microservicio tiene su propio Dockerfile porque se
# construye y despliega por separado (RNF-05); por eso no se comparte con los otros.

# slim: Debian mínimo con Python. 3.12 porque el código usa "str | None" (3.10+).
FROM python:3.12-slim

# Sin archivos .pyc dentro del contenedor y con los print/logs visibles al
# instante en "docker compose logs" (sin buffer).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# requirements.txt se copia antes que el código: Docker reutiliza esta capa en
# cache y solo reinstala librerías cuando cambia este archivo, no con cada cambio de código.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

# Primero se aplican las migraciones pendientes (crea o actualiza las tablas) y
# después arranca la API. "exec" reemplaza al shell por Python: el contenedor
# queda con un único proceso, que es el que recibe la señal de "docker compose stop".
CMD ["sh", "-c", "flask db upgrade && exec python app.py"]
