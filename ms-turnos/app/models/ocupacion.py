from app import db


class Ocupacion(db.Model):
    """Casillero (fecha, hora, box) tomado por un turno.

    Un turno común genera una ocupación y un camión una por cada horario de su
    franja (RN-05 y RN-06). Contar ocupaciones por horario da los boxes libres
    sin calcular rangos de horas en cada consulta.
    """

    __tablename__ = "ocupaciones"

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    hora = db.Column(db.Time, nullable=False)
    box = db.Column(db.Integer, nullable=False)
    turno_id = db.Column(db.Integer, db.ForeignKey("turnos.id"), nullable=False)

    __table_args__ = (
        # Garantía de concurrencia (RNF-02): si dos reservas simultáneas eligen el
        # mismo casillero, la base rechaza la segunda aunque el servicio lo haya
        # visto libre. El índice que crea también acelera la búsqueda por fecha.
        db.UniqueConstraint("fecha", "hora", "box", name="uq_ocupaciones_casillero"),
    )
