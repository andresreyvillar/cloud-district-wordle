"""Medallas: catálogo y cálculo.

Slice: `medallas-en-el-resumen-diario` (openspec/slices/estadisticas/medallas-en-el-resumen-diario.md).

Funciones puras. La temporada y la jornada entran **por parámetro**: el cálculo no lee el reloj, y por
eso se puede verificar con fixtures fijos (§10 del protocolo).

Una medalla es una función de los resultados: no se almacena. Recalibrar un umbral recalcula el palmarés
histórico completo sin migrar nada — y por eso los umbrales viven en el catálogo, no repartidos por la
lógica.

Los umbrales están calibrados contra 123 pares jugador-mes del histórico; su rareza medida está en
docs/context/briefs/medallas.md. La propuesta original ("más de 10 figuras en un mes") era inalcanzable:
el máximo histórico de una figura en un mes es 6.
"""

from __future__ import annotations

import statistics
from collections import defaultdict
from dataclasses import dataclass

from calendario import solo_laborables

# El umbral de muestra vive en `seasons` porque es parte de qué es un día de temporada. Se importa en lugar
# de copiarse: el docstring de este módulo ya decía que quería ser el mismo criterio, y ahora lo es.
from seasons import MUESTRA_MINIMA_DEL_DIA  # noqa: F401  (se re-exporta: los tests lo leen de aquí)

FALLO = 7

UMBRAL_DIA_IMPOSIBLE = 5.5
UMBRAL_DIA_DIFICIL = 4.5
RESOLVER_RAPIDO = 4

MINIMO_SUPERVIVIENTE = 3
MINIMO_VERDUGO = 5
MINIMO_IMPECABLE = 10
MINIMO_FONDISTA = 15
MINIMO_DIAS_PARA_PLENO = 10


@dataclass(frozen=True)
class Medalla:
    clave: str
    nombre: str
    emoji: str
    nivel: str  # legendario | raro | comun
    alcance: str  # temporada | permanente


CATALOGO: tuple[Medalla, ...] = (
    Medalla("suertudo", "Suertud@", "🍀", "legendario", "permanente"),
    Medalla("dia-imposible", "El día imposible", "🗿", "legendario", "permanente"),
    Medalla("superviviente", "Superviviente", "🛡️", "legendario", "temporada"),
    Medalla("pleno", "Pleno", "📅", "raro", "temporada"),
    Medalla("verdugo", "Verdugo", "🎯", "comun", "temporada"),
    Medalla("impecable", "Impecable", "✨", "comun", "temporada"),
    Medalla("fondista", "Fondista", "💪", "comun", "temporada"),
)

POR_CLAVE = {m.clave: m for m in CATALOGO}
#: orden de presentación: primero lo que cuesta más conseguir
ORDEN_NIVEL = {"legendario": 0, "raro": 1, "comun": 2}


def _dificultad_por_dia(resultados: list[dict]) -> dict[int, float]:
    """Media del grupo en cada jornada, solo para las que tienen muestra suficiente."""
    por_dia: dict[int, list[int]] = defaultdict(list)
    for fila in resultados:
        por_dia[fila["wordle_id"]].append(fila["score"])
    return {
        wordle: statistics.mean(scores)
        for wordle, scores in por_dia.items()
        if len(scores) >= MUESTRA_MINIMA_DEL_DIA
    }


def _mejor_del_dia(resultados: list[dict]) -> dict[int, int]:
    mejor: dict[int, int] = {}
    for fila in resultados:
        wordle, score = fila["wordle_id"], fila["score"]
        if wordle not in mejor or score < mejor[wordle]:
            mejor[wordle] = score
    return mejor


def _de_la_temporada(resultados: list[dict], temporada: str) -> list[dict]:
    return [fila for fila in resultados if str(fila["date"]).startswith(temporada)]


def medallas_de_temporada(resultados: list[dict], temporada: str) -> dict[str, list[str]]:
    """Las medallas de temporada de cada jugador en esa temporada.

    `resultados` puede abarcar varias temporadas: la ventana la fija el parámetro, no el reloj.

    Solo cuentan los días laborables, y el filtro va **aquí** y no en cada recuento: así todo lo derivado
    queda limpio de una vez —la dificultad del día, el mejor del día, el número de partidas y, el que
    importa, el conjunto de días que forman la temporada del que depende `Pleno`.
    """
    del_mes = _de_la_temporada(solo_laborables(resultados), temporada)
    if not del_mes:
        return {}

    dificultad = _dificultad_por_dia(del_mes)
    mejor = _mejor_del_dia(del_mes)
    dias_de_la_temporada = {fila["wordle_id"] for fila in del_mes}

    por_jugador: dict[str, list[dict]] = defaultdict(list)
    for fila in del_mes:
        por_jugador[fila["player_name"]].append(fila)

    palmares: dict[str, list[str]] = {}
    for jugador, filas in por_jugador.items():
        ganadas: list[str] = []
        jugados = {fila["wordle_id"] for fila in filas}

        dias_duros_resueltos = sum(
            1
            for fila in filas
            if dificultad.get(fila["wordle_id"], 0) >= UMBRAL_DIA_DIFICIL
            and fila["score"] <= RESOLVER_RAPIDO
        )
        if dias_duros_resueltos >= MINIMO_SUPERVIVIENTE:
            ganadas.append("superviviente")

        if len(dias_de_la_temporada) >= MINIMO_DIAS_PARA_PLENO and jugados >= dias_de_la_temporada:
            ganadas.append("pleno")

        if sum(1 for fila in filas if fila["score"] == mejor[fila["wordle_id"]]) >= MINIMO_VERDUGO:
            ganadas.append("verdugo")

        if len(filas) >= MINIMO_IMPECABLE and all(fila["score"] < FALLO for fila in filas):
            ganadas.append("impecable")

        if len(filas) >= MINIMO_FONDISTA:
            ganadas.append("fondista")

        if ganadas:
            palmares[jugador] = sorted(ganadas, key=lambda c: (ORDEN_NIVEL[POR_CLAVE[c].nivel], c))
    return palmares


def medallas_permanentes(
    resultados: list[dict], jornada: int | None = None
) -> dict[str, list[str]]:
    """Las medallas permanentes de cada jugador.

    Con `jornada`, solo devuelve las conseguidas **en** esa jornada: es lo que permite anunciarlas el día
    que ocurren y no repetirlas después.

    Filtra por día laborable igual que el cálculo de temporada. Consecuencia buscada: en sábado o domingo
    no se gana nada, ni siquiera una gesta permanente.
    """
    resultados = solo_laborables(resultados)
    dificultad = _dificultad_por_dia(resultados)
    palmares: dict[str, list[str]] = defaultdict(list)

    for fila in resultados:
        if jornada is not None and fila["wordle_id"] != jornada:
            continue
        jugador = fila["player_name"]

        if fila["score"] == 1 and "suertudo" not in palmares[jugador]:
            palmares[jugador].append("suertudo")

        if (
            dificultad.get(fila["wordle_id"], 0) >= UMBRAL_DIA_IMPOSIBLE
            and fila["score"] <= RESOLVER_RAPIDO
            and "dia-imposible" not in palmares[jugador]
        ):
            palmares[jugador].append("dia-imposible")

    return {
        jugador: sorted(claves, key=lambda c: (ORDEN_NIVEL[POR_CLAVE[c].nivel], c))
        for jugador, claves in palmares.items()
        if claves
    }


def repeticiones(resultados: list[dict], temporadas: list[str]) -> dict[tuple[str, str], int]:
    """Cuántas veces ha ganado cada jugador cada medalla de temporada, en las temporadas dadas."""
    cuenta: dict[tuple[str, str], int] = defaultdict(int)
    for temporada in temporadas:
        for jugador, claves in medallas_de_temporada(resultados, temporada).items():
            for clave in claves:
                cuenta[(jugador, clave)] += 1
    return dict(cuenta)


def medallas_nuevas(resultados: list[dict], temporada: str, jornada: int) -> dict[str, list[str]]:
    """Las medallas que se han ganado **en** esa jornada, comparando el antes y el después.

    Se calcula, no se recuerda: el estado anterior se obtiene descartando la jornada. Así no hace falta
    guardar qué se anunció ya, y el resultado es reproducible con los mismos datos.
    """
    # Las dos ventanas se cortan en la jornada: comparar contra `resultados` completo metería las
    # jornadas POSTERIORES en el "ahora" y anunciaría medallas que aún no se han ganado.
    hasta_hoy = [fila for fila in resultados if fila["wordle_id"] <= jornada]
    hasta_ayer = [fila for fila in resultados if fila["wordle_id"] < jornada]
    antes = medallas_de_temporada(hasta_ayer, temporada)
    ahora = medallas_de_temporada(hasta_hoy, temporada)

    nuevas: dict[str, list[str]] = {}
    for jugador, claves in ahora.items():
        recien = [c for c in claves if c not in antes.get(jugador, [])]
        if recien:
            nuevas[jugador] = recien

    for jugador, claves in medallas_permanentes(resultados, jornada=jornada).items():
        nuevas.setdefault(jugador, []).extend(claves)

    return {
        jugador: sorted(claves, key=lambda c: (ORDEN_NIVEL[POR_CLAVE[c].nivel], c))
        for jugador, claves in nuevas.items()
    }


def texto_de_medallas(resultados: list[dict], temporada: str, jornada: int) -> str:
    """La sección de medallas del resumen diario, o cadena vacía si no hay novedades.

    Solo anuncia lo que se ha ganado en la jornada. El estado acumulado del mes es información de la
    ficha de jugador: en el mensaje diario produciría líneas de diez nombres repetidas veinte días
    seguidos, porque las tres medallas comunes las tiene casi todo el grupo.
    """
    nuevas = medallas_nuevas(resultados, temporada, jornada)
    if not nuevas:
        return ""

    temporadas = sorted({str(f["date"])[:7] for f in resultados if str(f["date"])[:7] <= temporada})
    veces = repeticiones(resultados, temporadas)

    por_medalla: dict[str, list[str]] = defaultdict(list)
    for jugador, claves in nuevas.items():
        for clave in claves:
            repetida = veces.get((jugador, clave), 1)
            por_medalla[clave].append(f"{jugador}{f' (×{repetida})' if repetida > 1 else ''}")

    lineas: list[str] = []
    for medalla in CATALOGO:  # el catálogo ya está en orden de rareza
        if medalla.clave in por_medalla:
            quienes = ", ".join(sorted(por_medalla[medalla.clave]))
            exclamacion = "¡" if medalla.nivel == "legendario" else ""
            cierre = "!" if medalla.nivel == "legendario" else ""
            lineas.append(f"{medalla.emoji} {exclamacion}{medalla.nombre}{cierre} — {quienes}")

    return "🏅 *Medallas de hoy*\n" + "\n".join(lineas)
