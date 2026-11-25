# Sistema de Turnos para Lubricentro

Proyecto de la materia **Desarrollo de Software**.

Sistema de gestión de turnos para un lubricentro con 2 boxes, desarrollado
con arquitectura de **microservicios**, metodología **TDD** y principios
**SOLID, DRY, KISS y YAGNI**.

## Microservicios

| Servicio      | Responsabilidad                              | Puerto | Base de datos  |
|---------------|----------------------------------------------|--------|----------------|
| ms-usuarios   | Registro, login (JWT) y roles                | 5001   | `usuarios_db`  |
| ms-vehiculos  | Vehículos de cada cliente                    | 5002   | `vehiculos_db` |
| ms-turnos     | Disponibilidad, reserva y cancelación        | 5003   | `turnos_db`    |

- Cada microservicio tiene su propia base de datos dentro de un único servidor PostgreSQL.
- ms-usuarios emite el token JWT; ms-vehiculos y ms-turnos lo verifican con la misma clave, sin consultar a ms-usuarios.
- Al reservar, ms-turnos le consulta por HTTP a ms-vehiculos si el vehículo pertenece al cliente y de qué tipo es.

## Reglas de negocio

- Atención de lunes a sábado.
- Turnos de 30 minutos: mañana de 8:00 a 12:30 (último turno) y tarde de 16:30 a 20:00 (último turno).
- 2 boxes disponibles; el sistema asigna el box automáticamente.
- Los camiones solo reservan a las 8:00 o 16:30 y ocupan un box toda la franja.
- Los turnos cancelados y los vehículos dados de baja no se borran (baja lógica).

## Tecnologías

Python 3.12, Flask, SQLAlchemy, Flask-Migrate, Marshmallow, Flask-JWT-Extended, PostgreSQL 16, Docker.

## Estructura del repositorio

```
lubricentro-turnos/
├── docker-compose.yml        # Sistema completo: base + 3 microservicios
├── .env.example              # Variables para docker-compose.yml
├── docker/postgres/          # Solo la base de datos (desarrollo local)
├── docs/                     # Requerimientos, historias y diagramas PlantUML
├── scripts/                  # Verificación de la integración
├── ms-usuarios/              # Cada microservicio: app/, test/, migrations/,
├── ms-vehiculos/             #   Dockerfile, requirements.txt y .env.example
└── ms-turnos/
```

## Requisitos previos

| Herramienta    | Para qué                                     | Cómo verificar           |
|----------------|----------------------------------------------|--------------------------|
| Git            | Clonar el repositorio                        | `git --version`          |
| Docker Desktop | Levantar la base y los microservicios        | `docker compose version` |
| Python 3.10 o superior | Ejecutar los tests y el script de verificación | `python --version` |
| VS Code (opcional) | Editor; extensiones Python, Docker y PlantUML | —                   |

Docker Desktop tiene que estar **abierto** (ícono de la ballena sin errores) antes de usar cualquier comando `docker`.
Los puertos 5001, 5002, 5003 y 5433 de la computadora deben estar libres.

## Cómo levantar el sistema (Docker)

Los comandos son para la terminal **CMD** de Windows y se ejecutan en la carpeta raíz del repositorio.

1. Clonar el repositorio y entrar a la carpeta:

   ```cmd
   git clone https://github.com/EmiBianchi/lubricentro-turnos.git
   cd lubricentro-turnos
   ```

2. Crear el archivo de configuración a partir del ejemplo:

   ```cmd
   copy .env.example .env
   ```

   Abrir `.env` y completar `JWT_SECRET_KEY` y `ADMIN_PASSWORD`. Para generar una clave segura:

   ```cmd
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   Si ya se usó `docker/postgres`, `POSTGRES_USER` y `POSTGRES_PASSWORD` deben ser los mismos de `docker/postgres/.env`.

3. Si la base de desarrollo (`docker/postgres`) está encendida, apagarla: usan el mismo contenedor y no pueden estar las dos a la vez.

   ```cmd
   cd docker\postgres
   docker compose down
   cd ..\..
   ```

4. Construir las imágenes y levantar todo en segundo plano:

   ```cmd
   docker compose up -d --build
   ```

   La primera vez tarda unos minutos (descarga Python y PostgreSQL e instala las librerías).
   Cada microservicio aplica sus migraciones al arrancar, y ms-usuarios crea los roles y el administrador del `.env`.

5. Comprobar que los 4 contenedores estén en estado `running` (la base, además, `healthy`):

   ```cmd
   docker compose ps
   ```

6. Verificar que los microservicios se comuniquen entre sí:

   ```cmd
   python scripts\verificar_integracion.py
   ```

   Registra un cliente, inicia sesión, carga un vehículo y reserva un turno. La reserva solo funciona si ms-turnos
   consigue los datos del vehículo desde ms-vehiculos. Al final cancela el turno y da de baja el vehículo de prueba.
   Debe terminar con: `Integración verificada: ms-turnos se comunica correctamente con ms-vehiculos.`

### Comandos útiles

| Acción                                   | Comando                                  |
|------------------------------------------|------------------------------------------|
| Ver los registros (logs) de un servicio  | `docker compose logs -f ms-turnos`       |
| Detener todo (conserva los datos)        | `docker compose down`                    |
| Volver a levantar tras cambiar el código | `docker compose up -d --build`           |
| Detener un solo servicio                 | `docker compose stop ms-vehiculos`       |

Los datos quedan en `docker/postgres/data` y sobreviven a `docker compose down`. Para empezar con la base vacía,
detener todo y borrar esa carpeta.

### Desarrollo local sin Docker para los microservicios

Para programar con recarga automática se puede levantar solo la base con `docker/postgres` y ejecutar cada
microservicio con `python app.py` (cada uno con su propio `.env`, copiado de su `.env.example`).
Ver el apartado de tests para crear el entorno virtual.

## Cómo ejecutar los tests

Los tests usan SQLite en memoria y simulan a ms-vehiculos: **no necesitan Docker** ni el sistema levantado.

1. Crear y activar el entorno virtual (una sola vez, en la raíz del repositorio; se comparte entre los tres microservicios):

   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r ms-usuarios\requirements.txt -r ms-vehiculos\requirements.txt -r ms-turnos\requirements.txt
   ```

   En cada terminal nueva basta con `venv\Scripts\activate` (aparece `(venv)` al inicio de la línea).

2. Ejecutar los tests de cada microservicio desde su carpeta:

   ```cmd
   cd ms-usuarios
   python -m unittest discover -s test -v
   cd ..\ms-vehiculos
   python -m unittest discover -s test -v
   cd ..\ms-turnos
   python -m unittest discover -s test -v
   cd ..
   ```

   Cada ejecución debe terminar con `OK`.

También se pueden ejecutar dentro de los contenedores, con el sistema levantado:

```cmd
docker compose exec ms-turnos python -m unittest discover -s test
```

## Endpoints disponibles

Todas las rutas empiezan con `http://localhost:<puerto>/api/v1`. Los cuerpos son JSON.
Las rutas protegidas requieren el encabezado `Authorization: Bearer <token>`, con el token que devuelve el login.

| Acceso  | Significado                                                       |
|---------|-------------------------------------------------------------------|
| Público | No requiere token                                                 |
| Token   | Cualquier usuario con token válido; sin token o vencido → 401     |
| Admin   | Solo rol admin; con token de cliente → 403                        |

### ms-usuarios — puerto 5001

| Método | Ruta                | Acceso  | Descripción                               | Cuerpo / parámetros                   | Respuesta OK |
|--------|---------------------|---------|-------------------------------------------|---------------------------------------|--------------|
| POST   | `/usuarios`         | Público | Registrar cliente (HU-01)                 | `{"nombre", "email", "password"}`     | 201          |
| POST   | `/auth/login`       | Público | Iniciar sesión; devuelve el token (HU-02) | `{"email", "password"}`               | 200 `{"access_token"}` |
| GET    | `/usuarios/perfil`  | Token   | Datos del dueño del token (HU-03)         | —                                     | 200          |
| GET    | `/usuarios`         | Admin   | Listar todos los usuarios (HU-04)         | —                                     | 200          |

### ms-vehiculos — puerto 5002

| Método | Ruta               | Acceso | Descripción                              | Cuerpo / parámetros                                  | Respuesta OK |
|--------|--------------------|--------|------------------------------------------|------------------------------------------------------|--------------|
| POST   | `/vehiculos`       | Token  | Registrar vehículo propio (HU-05)        | `{"patente", "tipo", "marca", "modelo", "anio"}`     | 201          |
| GET    | `/vehiculos`       | Token  | Listar mis vehículos activos (HU-06)     | —                                                    | 200          |
| PUT    | `/vehiculos/<id>`  | Token  | Modificar vehículo propio (HU-07)        | mismo cuerpo que el alta                             | 200          |
| DELETE | `/vehiculos/<id>`  | Token  | Baja lógica de vehículo propio (HU-08)   | —                                                    | 204          |

`tipo`: `moto`, `auto`, `camioneta` o `camion`. `patente`: 6 o 7 letras y números (ej. `AB123CD`).

### ms-turnos — puerto 5003

| Método | Ruta                                   | Acceso | Descripción                                   | Cuerpo / parámetros                          | Respuesta OK |
|--------|----------------------------------------|--------|-----------------------------------------------|----------------------------------------------|--------------|
| GET    | `/turnos/disponibilidad?fecha=AAAA-MM-DD` | Token | Boxes libres de cada horario (HU-09)       | `fecha` en la URL                            | 200          |
| POST   | `/turnos`                              | Token  | Reservar turno común o de camión (HU-10, HU-11) | `{"vehiculo_id", "fecha": "AAAA-MM-DD", "hora": "HH:MM"}` | 201 |
| GET    | `/turnos`                              | Token  | Ver mis turnos (HU-12)                        | —                                            | 200          |
| DELETE | `/turnos/<id>`                         | Token  | Cancelar turno propio y futuro (HU-13)        | —                                            | 204          |
| GET    | `/turnos/agenda?fecha=AAAA-MM-DD`      | Admin  | Agenda del día (HU-14)                        | `fecha` en la URL                            | 200          |

Errores de la reserva: 400 (domingo, fecha pasada u horario inválido), 404 (el vehículo no es del cliente),
409 (sin boxes libres) y 503 (ms-vehiculos no responde).

## Documentación

| Archivo | Contenido |
|---------|-----------|
| [docs/requerimientos.md](docs/requerimientos.md) | Requerimientos funcionales, no funcionales y reglas de negocio |
| [docs/historias-de-usuario.md](docs/historias-de-usuario.md) | Historias de usuario, tareas técnicas y plan de sprints |
| `docs/clases_ms_*.puml` | Diagramas de clases de cada microservicio |
| [docs/secuencia_reserva_turno_comun.puml](docs/secuencia_reserva_turno_comun.puml) | Secuencia de la reserva de turno común entre microservicios |
| [docs/secuencia_reserva_turno_camion.puml](docs/secuencia_reserva_turno_camion.puml) | Secuencia de la reserva de turno de camión |

Los diagramas `.puml` se ven en VS Code con la extensión PlantUML (`Alt + D`).

## Trabajo futuro

- Recomendación de filtros (aire, aceite, combustible y habitáculo) según el vehículo.
