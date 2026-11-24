from collections import Counter
from datetime import date, datetime, time

from app.models import Ocupacion, Turno
from app.repository import CasilleroOcupado
from app.services.cliente_vehiculos import ClienteVehiculos
from app.services.excepciones import (
    DiaNoHabil,
    FechaPasada,
    SinBoxDisponible,
    TurnoAjeno,
    TurnoNoCancelable,
    TurnoNoEncontrado,
    VehiculoNoEncontrado,
)
from app.services.grilla_horaria import GrillaHoraria
from app.services.reglas_reserva import FabricaReglas
from app.services.reloj import Reloj


class TurnoService:
    """Casos de uso de turnos.

    Recibe sus dependencias por constructor (DIP): en ejecución se inyectan las
    reales (ver fabrica.py) y en los tests, dobles en memoria y un reloj fijo.
    """

    def __init__(self, turno_repo, ocupacion_repo, cliente_vehiculos: ClienteVehiculos,
                 grilla: GrillaHoraria, fabrica_reglas: FabricaReglas, reloj: Reloj):
        self._turno_repo = turno_repo
        self._ocupacion_repo = ocupacion_repo
        self._cliente_vehiculos = cliente_vehiculos
        self._grilla = grilla
        self._fabrica_reglas = fabrica_reglas
        self._reloj = reloj

    def consultar_disponibilidad(self, fecha: date) -> list[dict]:
        """Boxes libres de cada horario del día (HU-09).

        :param fecha: día a consultar.
        :return: [{"hora": time, "boxes_libres": int}, ...] en orden; vacía si es domingo.
        :raises FechaPasada: si la fecha es anterior a hoy.
        """
        ahora = self._reloj.ahora()
        if fecha < ahora.date():
            raise FechaPasada()
        # Hoy se omiten los horarios que ya empezaron: no se podrían reservar (RN-08).
        horarios = [hora for hora in self._grilla.horarios_del_dia(fecha)
                    if datetime.combine(fecha, hora) > ahora]
        ocupados = Counter(ocupacion.hora for ocupacion in self._ocupacion_repo.listar_por_fecha(fecha))
        return [{"hora": hora, "boxes_libres": self._grilla.cantidad_boxes - ocupados[hora]}
                for hora in horarios]

    def reservar(self, usuario_id: int, vehiculo_id: int, fecha: date, hora: time,
                 token: str) -> Turno:
        """Reserva un turno y le asigna automáticamente un box libre (HU-10, RN-10).

        :param usuario_id: id del cliente, tomado del token.
        :param token: JWT del cliente, reenviado a ms-vehiculos.
        :return: el turno creado.
        :raises DiaNoHabil: si la fecha es domingo.
        :raises FechaPasada: si la fecha y hora ya pasaron.
        :raises VehiculoNoEncontrado: si el vehículo no es un vehículo activo del cliente.
        :raises ErrorDeNegocio: si la regla del tipo de vehículo rechaza el horario.
        :raises SinBoxDisponible: si ningún box tiene libres todos los horarios necesarios.
        """
        # Primero las validaciones locales: no se consulta a ms-vehiculos por un
        # pedido que igual se va a rechazar.
        if not self._grilla.es_dia_habil(fecha):
            raise DiaNoHabil()
        if datetime.combine(fecha, hora) <= self._reloj.ahora():
            raise FechaPasada()

        vehiculo = self._cliente_vehiculos.obtener_vehiculo(vehiculo_id, token)
        if vehiculo is None:
            raise VehiculoNoEncontrado(vehiculo_id)

        regla = self._fabrica_reglas.crear(vehiculo["tipo"])
        regla.validar(hora, self._grilla)
        horarios = regla.horarios_a_ocupar(hora, self._grilla)
        box = self._box_libre(fecha, horarios)

        turno = Turno(
            fecha=fecha, hora_inicio=hora, hora_fin=self._grilla.hora_fin(horarios[-1]), box=box,
            usuario_id=usuario_id, vehiculo_id=vehiculo_id,
            patente=vehiculo["patente"], tipo_vehiculo=vehiculo["tipo"],
            ocupaciones=[Ocupacion(fecha=fecha, hora=horario, box=box) for horario in horarios],
        )
        try:
            return self._turno_repo.guardar(turno)
        except CasilleroOcupado:
            # Otra reserva tomó el casillero entre la búsqueda del box y el guardado:
            # la restricción única de la base decide cuál queda (RNF-02).
            raise SinBoxDisponible() from None

    def listar_de_usuario(self, usuario_id: int) -> list[Turno]:
        """:return: los turnos del cliente (HU-12); no incluye los cancelados."""
        return self._turno_repo.listar_por_usuario(usuario_id)

    def cancelar(self, turno_id: int, usuario_id: int) -> None:
        """Baja lógica de un turno futuro del cliente; el horario vuelve a quedar libre (HU-13).

        :raises TurnoNoEncontrado: si no existe o ya fue cancelado.
        :raises TurnoAjeno: si pertenece a otro cliente.
        :raises TurnoNoCancelable: si el turno ya empezó o pasó.
        """
        turno = self._turno_repo.buscar_por_id(turno_id)
        if turno is None or turno.deleted_at is not None:
            raise TurnoNoEncontrado(turno_id)
        if turno.usuario_id != usuario_id:
            raise TurnoAjeno()
        # Cancelar un turno pasado no liberaría nada y borraría el registro de
        # que el vehículo fue atendido.
        if datetime.combine(turno.fecha, turno.hora_inicio) <= self._reloj.ahora():
            raise TurnoNoCancelable()
        self._turno_repo.eliminar(turno)

    def _box_libre(self, fecha: date, horarios: list[time]) -> int:
        # El box debe estar libre en TODOS los horarios: un camión necesita la
        # franja completa en el mismo box (RN-07); un turno común, uno solo.
        ocupados = {(ocupacion.hora, ocupacion.box)
                    for ocupacion in self._ocupacion_repo.listar_por_fecha(fecha)}
        for box in range(1, self._grilla.cantidad_boxes + 1):
            if all((horario, box) not in ocupados for horario in horarios):
                return box
        raise SinBoxDisponible()
