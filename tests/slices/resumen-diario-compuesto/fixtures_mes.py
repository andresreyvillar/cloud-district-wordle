"""Un mes sintético para los podios y el momento del mes, de `resumen-diario-compuesto`.

Septiembre de 2026, con cinco jugadores que juegan todos los laborables: así cada día cuenta para la
temporada (laborable y con cinco jugadores). Los nombres son sintéticos: el repositorio es público.
"""

from __future__ import annotations

import datetime

TEMPORADA = "2026-09"

LORO = ".G.../.G..G/.GY../GGGGG"
GEOMETRICO = "..G../..G../GGGGG"
FLOR = "Y..../..Y../GGGGG"

#: Nota y dibujo de cada uno, todos los días.
JUGADORES = {
    "Ana": (3, LORO),
    "Bea": (3, GEOMETRICO),
    "Cris": (4, FLOR),
    "Dani": (5, FLOR),
    "Eva": (5, FLOR),
}

#: La jornada de un día: un número por día natural, como los del Wordle.
PRIMERA_JORNADA = 1700


def jornada_de(fecha: str) -> int:
    return PRIMERA_JORNADA + (datetime.date.fromisoformat(fecha) - datetime.date(2026, 9, 1)).days


def laborables(hasta: str) -> list[str]:
    """Los laborables de septiembre de 2026 hasta `hasta`, incluido."""
    dia, fin, fechas = datetime.date(2026, 9, 1), datetime.date.fromisoformat(hasta), []
    while dia <= fin:
        if dia.weekday() < 5:
            fechas.append(dia.isoformat())
        dia += datetime.timedelta(days=1)
    return fechas


def fila(nombre: str, fecha: str, score: int, patron: str) -> dict:
    return {
        "slack_user_id": f"U_{nombre}",
        "player_name": nombre,
        "wordle_id": jornada_de(fecha),
        "score": score,
        "date": fecha,
        "pattern": patron,
    }


def mes(hasta: str, notas: dict[str, int] | None = None, cambios: dict[tuple[str, str], int] | None = None):
    """Los resultados de septiembre hasta `hasta`. `cambios[(nombre, fecha)]` sustituye una nota."""
    filas = []
    for fecha in laborables(hasta):
        for nombre, (score, patron) in JUGADORES.items():
            nota = (notas or {}).get(nombre, score)
            nota = (cambios or {}).get((nombre, fecha), nota)
            filas.append(fila(nombre, fecha, nota, patron))
    return filas


def nivel(fecha: str) -> dict:
    return {"jornada": jornada_de(fecha), "fecha": fecha}


def marca(fecha: str, nombre: str, segundos: float) -> dict:
    return {"jornada": jornada_de(fecha), "jugador": f"U_{nombre}", "segundos": segundos, "estrellas": 1}
