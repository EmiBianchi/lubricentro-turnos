"""Verifica que los tres microservicios levantados con docker compose trabajen juntos.

Recorre el flujo real de un cliente: registro y login (ms-usuarios), alta de un
vehículo (ms-vehiculos) y reserva de un turno (ms-turnos). La reserva es la prueba
de integración: ms-turnos solo puede completarla si le consulta el vehículo a
ms-vehiculos por la red de Docker.

Uso (con el sistema levantado):  python scripts/verificar_integracion.py

Solo usa la biblioteca estándar de Python: se ejecuta sin activar ningún entorno
virtual. Al terminar cancela el turno y da de baja el vehículo de prueba para no
dejar ocupado un box.
"""
import json
import random
import string
import sys
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

USUARIOS = "http://localhost:5001/api/v1"
VEHICULOS = "http://localhost:5002/api/v1"
TURNOS = "http://localhost:5003/api/v1"

DOMINGO = 6
# Un id que nunca va a pertenecer al cliente de prueba recién creado.
VEHICULO_INEXISTENTE = 999999


def llamar(metodo: str, url: str, cuerpo: dict | None = None,
           token: str | None = None) -> tuple[int, dict | list | None]:
    """Hace un pedido HTTP con JSON.

    :return: (código de estado, cuerpo de la respuesta convertido de JSON o None).
    """
    encabezados = {"Content-Type": "application/json"}
    if token:
        encabezados["Authorization"] = f"Bearer {token}"
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    pedido = Request(url, data=datos, headers=encabezados, method=metodo)
    try:
        with urlopen(pedido, timeout=10) as respuesta:
            return respuesta.status, _leer_json(respuesta.read())
    except HTTPError as error:
        # 4xx y 5xx no son fallas del script: son respuestas a comparar con lo esperado.
        return error.code, _leer_json(error.read())


def _leer_json(contenido: bytes):
    return json.loads(contenido) if contenido else None


def paso(descripcion: str, esperado: int, metodo: str, url: str,
         cuerpo: dict | None = None, token: str | None = None):
    """Ejecuta un pedido y corta el script si el código no es el esperado.

    :return: el cuerpo de la respuesta.
    """
    codigo, respuesta = llamar(metodo, url, cuerpo, token)
    if codigo != esperado:
        print(f"[ERROR] {descripcion}: se esperaba {esperado} y llegó {codigo}.")
        print(f"        Respuesta: {respuesta}")
        if codigo == 503:
            print("        ms-turnos no pudo comunicarse con ms-vehiculos. "
                  "Revisar: docker compose logs ms-turnos")
        sys.exit(1)
    print(f"[OK] {descripcion} ({codigo})")
    return respuesta


def proximo_horario_libre(token: str) -> tuple[str, str]:
    """Busca, desde mañana, el primer día hábil con algún box libre.

    :return: (fecha AAAA-MM-DD, hora HH:MM).
    """
    fecha = date.today()
    for _ in range(14):
        fecha += timedelta(days=1)
        if fecha.weekday() == DOMINGO:
            continue
        disponibilidad = paso(f"Consultar disponibilidad del {fecha}", 200, "GET",
                              f"{TURNOS}/turnos/disponibilidad?fecha={fecha}", token=token)
        libres = [h for h in disponibilidad["horarios"] if h["boxes_libres"] > 0]
        if libres:
            return fecha.isoformat(), libres[0]["hora"]
    print("[ERROR] No hay horarios libres en las próximas dos semanas.")
    sys.exit(1)


def main() -> None:
    # Sufijo aleatorio: el email y la patente son únicos, así el script se puede
    # ejecutar varias veces sin chocar con datos de una ejecución anterior.
    sufijo = "".join(random.choices(string.digits, k=6))
    letras = "".join(random.choices(string.ascii_uppercase, k=4))
    email = f"integracion{sufijo}@prueba.com"
    password = "clave-de-prueba"
    patente = f"{letras[:2]}{sufijo[:3]}{letras[2:]}"

    print("Verificando la integración de los microservicios...\n")
    try:
        paso("Registrar cliente en ms-usuarios", 201, "POST", f"{USUARIOS}/usuarios",
             {"nombre": "Cliente de prueba", "email": email, "password": password})
    except URLError:
        print("[ERROR] No se pudo conectar con ms-usuarios (localhost:5001).")
        print("        ¿Está levantado el sistema? Revisar con: docker compose ps")
        sys.exit(1)

    token = paso("Iniciar sesión en ms-usuarios", 200, "POST", f"{USUARIOS}/auth/login",
                 {"email": email, "password": password})["access_token"]

    vehiculo = paso("Registrar vehículo en ms-vehiculos (con el token de ms-usuarios)", 201,
                    "POST", f"{VEHICULOS}/vehiculos",
                    {"patente": patente, "tipo": "auto", "marca": "Fiat",
                     "modelo": "Cronos", "anio": 2022}, token)

    fecha, hora = proximo_horario_libre(token)

    turno = paso(f"Reservar turno en ms-turnos el {fecha} a las {hora}", 201, "POST",
                 f"{TURNOS}/turnos",
                 {"vehiculo_id": vehiculo["id"], "fecha": fecha, "hora": hora}, token)
    # La patente y el tipo no viajan en el pedido de reserva: si están en el turno es
    # porque ms-turnos se los pidió a ms-vehiculos.
    if (turno["patente"], turno["tipo_vehiculo"]) != (vehiculo["patente"], vehiculo["tipo"]):
        print(f"[ERROR] El turno no tiene los datos del vehículo: {turno}")
        sys.exit(1)
    print(f"[OK] ms-turnos obtuvo de ms-vehiculos la patente {turno['patente']} "
          f"y el tipo {turno['tipo_vehiculo']}; box asignado: {turno['box']}")

    paso("Reservar con un vehículo que no es del cliente (ms-vehiculos no lo devuelve)",
         404, "POST", f"{TURNOS}/turnos",
         {"vehiculo_id": VEHICULO_INEXISTENTE, "fecha": fecha, "hora": hora}, token)

    paso("Cancelar el turno de prueba", 204, "DELETE", f"{TURNOS}/turnos/{turno['id']}",
         token=token)
    paso("Dar de baja el vehículo de prueba", 204, "DELETE",
         f"{VEHICULOS}/vehiculos/{vehiculo['id']}", token=token)

    print("\nIntegración verificada: ms-turnos se comunica correctamente con ms-vehiculos.")


if __name__ == "__main__":
    main()
