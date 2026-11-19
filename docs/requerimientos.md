# Análisis de Requerimientos

## 1. Descripción del problema

El lubricentro asigna turnos de forma manual. Se necesita un sistema donde los
clientes registren sus vehículos y reserven turnos según la disponibilidad real
de los 2 boxes, respetando el horario de atención y la regla especial de camiones.

## 2. Actores

| Actor         | Descripción                                                   |
|---------------|---------------------------------------------------------------|
| Cliente       | Se registra, carga sus vehículos, reserva y cancela turnos.   |
| Administrador | Personal del lubricentro. Consulta la agenda diaria.          |

## 3. Reglas de negocio

| ID    | Regla                                                                                          |
|-------|------------------------------------------------------------------------------------------------|
| RN-01 | Se atiende de lunes a sábado. Los domingos no hay turnos.                                      |
| RN-02 | Franja mañana: turnos de 30 min desde 08:00 hasta 12:30 (último turno). Cierre 13:00.          |
| RN-03 | Franja tarde: turnos de 30 min desde 16:30 hasta 20:00 (último turno). Cierre 20:30.           |
| RN-04 | Hay 2 boxes. En un mismo horario puede haber como máximo 2 turnos.                             |
| RN-05 | Motos, autos y camionetas ocupan un box durante 30 minutos.                                    |
| RN-06 | Un camión solo puede reservar a las 08:00 o a las 16:30 y ocupa un box durante toda la franja. |
| RN-07 | Un camión solo se acepta si el box está libre durante toda la franja.                          |
| RN-08 | No se pueden reservar turnos en fechas u horarios pasados.                                     |
| RN-09 | Un turno cancelado no se borra: se marca como eliminado (soft delete) y libera el horario.     |
| RN-10 | El box lo asigna el sistema automáticamente; el cliente no lo elige.                           |

## 4. Requerimientos funcionales

| ID    | Requerimiento                                         | Microservicio |
|-------|-------------------------------------------------------|---------------|
| RF-01 | Registrar un cliente.                                 | ms-usuarios   |
| RF-02 | Iniciar sesión y obtener un token de acceso.          | ms-usuarios   |
| RF-03 | Consultar los datos del propio perfil.                | ms-usuarios   |
| RF-04 | Restringir funciones según el rol (cliente / admin).  | ms-usuarios   |
| RF-05 | Registrar un vehículo del cliente.                    | ms-vehiculos  |
| RF-06 | Listar los vehículos del cliente.                     | ms-vehiculos  |
| RF-07 | Modificar un vehículo.                                | ms-vehiculos  |
| RF-08 | Dar de baja un vehículo.                              | ms-vehiculos  |
| RF-09 | Consultar los horarios disponibles de un día.         | ms-turnos     |
| RF-10 | Reservar un turno para un vehículo.                   | ms-turnos     |
| RF-11 | Listar los turnos del cliente.                        | ms-turnos     |
| RF-12 | Cancelar un turno.                                    | ms-turnos     |
| RF-13 | Consultar la agenda de un día (administrador).        | ms-turnos     |

## 5. Requerimientos no funcionales

| ID     | Requerimiento                                                                                      |
|--------|----------------------------------------------------------------------------------------------------|
| RNF-01 | Persistencia: los datos se guardan en PostgreSQL; cada microservicio usa su propia base de datos.  |
| RNF-02 | Concurrencia: dos reservas simultáneas no pueden ocupar el mismo box en el mismo horario.          |
| RNF-03 | Seguridad: las contraseñas se guardan cifradas y nunca se devuelven en las respuestas.             |
| RNF-04 | Seguridad: las operaciones requieren un token JWT válido, salvo registro e inicio de sesión.       |
| RNF-05 | Modularidad: cada microservicio tiene una única responsabilidad y se despliega por separado.       |
| RNF-06 | Portabilidad: todo el sistema se levanta con Docker, sin instalar PostgreSQL localmente.           |
| RNF-07 | Configuración: usuarios, contraseñas y claves se leen de archivos .env, nunca del código.          |
| RNF-08 | Mantenibilidad: el desarrollo sigue TDD y el código aplica SOLID, DRY, KISS y YAGNI.               |
| RNF-09 | Comunicación: los microservicios intercambian datos en formato JSON sobre HTTP.                    |

## 6. Fuera de alcance (trabajo futuro)

- Recomendación de filtros (aire, aceite, combustible y habitáculo) según el vehículo.
- Interfaz gráfica (frontend). Las pruebas se realizan con Thunder Client / Postman.
- Notificaciones, pagos, precios de servicios y gestión de stock.
