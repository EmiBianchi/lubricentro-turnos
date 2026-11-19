# Historias de Usuario

Formato: *Como [rol] necesito [funcionalidad] con la finalidad de [resultado].*
Cada historia y cada tarea técnica se carga como un issue en GitHub.

**Esfuerzo:** Bajo / Medio / Alto · **Estado:** Todo / In progress / Done

## Plan de sprints

| Sprint   | Objetivo                                              | Inicio     | Fin        |
|----------|-------------------------------------------------------|------------|------------|
| Sprint 0 | Preparación: tablero, diagrama de clases y base datos | 19/11/2026 | 20/11/2026 |
| Sprint 1 | Microservicio ms-usuarios                             | 20/11/2026 | 20/11/2026 |
| Sprint 2 | Microservicio ms-vehiculos                            | 21/11/2026 | 21/11/2026 |
| Sprint 3 | Microservicio ms-turnos                               | 22/11/2026 | 22/11/2026 |
| Sprint 4 | Integración y documentación                           | 23/11/2026 | 23/11/2026 |
| Sprint 5 | Ajustes según devolución y entrega                    | 24/11/2026 | 25/11/2026 |

## Historias de usuario

| ID | Nombre | Enunciado | Criterios de aceptación | Prioridad | Esfuerzo | Sprint | Estado |
|----|--------|-----------|-------------------------|-----------|----------|--------|--------|
| HU-01 | Registrar cuenta | Como cliente necesito registrarme con mi nombre, email y contraseña con la finalidad de poder reservar turnos. | • Nombre, email y contraseña son obligatorios.<br>• El email no puede estar registrado previamente.<br>• La contraseña se guarda cifrada.<br>• La respuesta no incluye la contraseña.<br>• El usuario creado tiene rol "cliente". | Alta | Medio | 1 | Todo |
| HU-02 | Iniciar sesión | Como cliente necesito iniciar sesión con mi email y contraseña con la finalidad de acceder a mis datos y turnos. | • Con credenciales correctas devuelve un token JWT.<br>• Con email o contraseña incorrectos devuelve error 401.<br>• El token tiene fecha de expiración. | Alta | Medio | 1 | Todo |
| HU-03 | Ver mi perfil | Como cliente necesito ver mis datos con la finalidad de verificar que estén correctos. | • Requiere token válido.<br>• Devuelve nombre, email y rol, sin contraseña.<br>• Sin token devuelve error 401. | Media | Bajo | 1 | Todo |
| HU-04 | Control por roles | Como administrador necesito que ciertas funciones sean exclusivas de mi rol con la finalidad de proteger la información del lubricentro. | • Existen los roles "cliente" y "admin".<br>• Un cliente que accede a una función de admin recibe error 403.<br>• El usuario admin se crea al iniciar el sistema, no por registro público. | Alta | Medio | 1 | Todo |
| HU-05 | Registrar vehículo | Como cliente necesito cargar mi vehículo con la finalidad de indicar cuál será atendido en el turno. | • Requiere token válido.<br>• Patente, tipo, marca, modelo y año son obligatorios.<br>• Tipo válido: moto, auto, camioneta o camion.<br>• La patente no puede repetirse.<br>• El vehículo queda asociado al cliente del token. | Alta | Medio | 2 | Todo |
| HU-06 | Listar mis vehículos | Como cliente necesito ver mis vehículos con la finalidad de elegir cuál llevar al turno. | • Devuelve solo los vehículos del cliente del token.<br>• No muestra vehículos dados de baja. | Alta | Bajo | 2 | Todo |
| HU-07 | Modificar vehículo | Como cliente necesito modificar los datos de mi vehículo con la finalidad de corregir errores de carga. | • Solo el dueño puede modificarlo (si no, error 403).<br>• Se aplican las mismas validaciones que al registrar. | Media | Bajo | 2 | Todo |
| HU-08 | Dar de baja vehículo | Como cliente necesito eliminar un vehículo con la finalidad de no verlo más si ya no lo tengo. | • Solo el dueño puede darlo de baja.<br>• Es una baja lógica (soft delete): se completa deleted_at.<br>• El vehículo deja de aparecer en el listado. | Media | Bajo | 2 | Todo |
| HU-09 | Consultar disponibilidad | Como cliente necesito ver los horarios libres de un día con la finalidad de elegir cuándo llevar mi vehículo. | • Para lunes a sábado devuelve los horarios de 08:00 a 12:30 y de 16:30 a 20:00 cada 30 minutos.<br>• Cada horario indica cuántos boxes quedan libres (0, 1 o 2).<br>• Un domingo no devuelve horarios.<br>• Una fecha pasada devuelve error 400. | Alta | Medio | 3 | Todo |
| HU-10 | Reservar turno común | Como cliente necesito reservar un turno para mi moto, auto o camioneta con la finalidad de asegurar que me atiendan. | • Solo de lunes a sábado y en un horario de la grilla.<br>• No se permite fecha u horario pasado.<br>• El vehículo debe pertenecer al cliente (se consulta a ms-vehiculos).<br>• Si hay un box libre, se asigna automáticamente.<br>• Si los 2 boxes están ocupados, devuelve error 409.<br>• Dos reservas simultáneas no pueden quedar en el mismo box y horario. | Alta | Alto | 3 | Todo |
| HU-11 | Reservar turno de camión | Como cliente necesito reservar un turno para mi camión con la finalidad de que lo atiendan en un box completo. | • Solo se acepta a las 08:00 o a las 16:30.<br>• Ocupa el box toda la franja (mañana: hasta 13:00; tarde: hasta 20:30).<br>• Solo se acepta si el box no tiene ningún turno en esa franja.<br>• Mientras dure, ese box no aparece libre en la disponibilidad. | Alta | Alto | 3 | Todo |
| HU-12 | Ver mis turnos | Como cliente necesito ver mis turnos reservados con la finalidad de recordar cuándo tengo que ir. | • Devuelve solo los turnos del cliente del token.<br>• Muestra fecha, hora, box y vehículo.<br>• No muestra turnos cancelados. | Alta | Bajo | 3 | Todo |
| HU-13 | Cancelar turno | Como cliente necesito cancelar un turno con la finalidad de liberar el horario si no puedo asistir. | • Solo el dueño puede cancelarlo.<br>• Solo se pueden cancelar turnos futuros.<br>• Es una baja lógica (soft delete).<br>• El horario vuelve a aparecer disponible. | Alta | Medio | 3 | Todo |
| HU-14 | Agenda del día | Como administrador necesito ver todos los turnos de un día con la finalidad de organizar el trabajo en los boxes. | • Solo accesible con rol admin.<br>• Lista los turnos ordenados por hora y box.<br>• Muestra la patente y el tipo de cada vehículo.<br>• No incluye turnos cancelados. | Media | Medio | 3 | Todo |

## Tareas técnicas

| ID | Nombre | Descripción | Prioridad | Esfuerzo | Sprint | Estado |
|----|--------|-------------|-----------|----------|--------|--------|
| TT-01 | Estructura inicial del repositorio | Crear repositorio, .gitignore y README. | Alta | Bajo | 0 | Done |
| TT-02 | Requerimientos e historias de usuario | Documentar análisis de requerimientos e historias. | Alta | Medio | 0 | Done |
| TT-03 | Configurar tablero de GitHub | Crear proyecto, etiquetas, milestones e issues. | Alta | Bajo | 0 | Todo |
| TT-04 | Diagrama de clases | Diagramar las clases de los 3 microservicios en PlantUML. | Alta | Alto | 0 | Todo |
| TT-05 | Base de datos en Docker | Levantar PostgreSQL con docker-compose y crear una base por microservicio. | Alta | Medio | 0 | Todo |
| TT-06 | Integración con docker-compose | Levantar los 3 microservicios y la base con un solo comando. | Alta | Alto | 4 | Todo |
| TT-07 | Diagramas de secuencia | Diagramar en PlantUML el flujo de reserva de turno entre microservicios. | Media | Medio | 4 | Todo |
| TT-08 | Documentación final | Completar el README con instrucciones de instalación, ejecución y pruebas. | Alta | Medio | 4 | Todo |
| TT-09 | Ajustes según devolución | Aplicar las correcciones indicadas por el profesor en la revisión de avances. | Alta | Medio | 5 | Todo |
