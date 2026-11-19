# Sistema de Turnos para Lubricentro

Proyecto de la materia **Desarrollo de Software**.

Sistema de gestión de turnos para un lubricentro con 2 boxes, desarrollado
con arquitectura de **microservicios**, metodología **TDD** y principios
**SOLID, DRY, KISS y YAGNI**.

## Microservicios

| Servicio      | Responsabilidad                              | Puerto |
|---------------|----------------------------------------------|--------|
| ms-usuarios   | Registro, login (JWT) y roles                | 5001   |
| ms-vehiculos  | Vehículos de cada cliente                    | 5002   |
| ms-turnos     | Disponibilidad, reserva y cancelación        | 5003   |

## Reglas de negocio

- Atención de lunes a sábado.
- Turnos de 30 minutos: mañana de 8:00 a 12:30 (último turno) y tarde de 16:30 a 20:00 (último turno).
- 2 boxes disponibles.
- Los camiones solo reservan a las 8:00 o 16:30 y ocupan un box toda la franja.

## Tecnologías

Python, Flask, SQLAlchemy, Marshmallow, PostgreSQL, Docker.

## Trabajo futuro

- Recomendación de filtros (aire, aceite, combustible y habitáculo) según el vehículo.
