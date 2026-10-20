"""Cómo juega cada uno: eficiencia, apertura, suerte y su acierto más milagroso.

Slice: `indicadores-de-juego` (openspec/slices/estadisticas/indicadores-de-juego.md).

**Todo sale de la cuadrícula y de la respuesta del día.** Con los colores de cada fila se estima cuántas
soluciones seguían siendo posibles antes de cada intento —las *candidatas*—. Acertar con una candidata es saber la
palabra; acertar con treinta es suerte. No se conocen las palabras probadas, solo sus colores: las candidatas se
estiman sorteando palabras de la lista que den esos colores contra la respuesta.

**No hay medidor de trampas** (decisión del dueño). Con una cuarentena de jugadores, cada mes alguien tiene una
racha que por puro azar solo ocurre un 1–2 % de las veces; un número junto a un nombre no puede decir por qué.

**Puro** (§10): la lista de soluciones entra por parámetro y solo se lee **hasta la última jornada jugada**, con
`palabra.palabra_de`, que es el guardarraíl del repositorio. Lo que sale no lleva ninguna palabra.
"""

from __future__ import annotations

import random
import re
import statistics
import unicodedata
from collections import Counter, defaultdict

from palabra import palabra_de
from seasons import resultados_de_temporada

#: Partidas con cuadrícula que hacen falta en la temporada para enseñar indicadores. Las mismas que el álbum:
#: con menos, una sola partida con suerte lo decide todo.
MINIMO_DE_PARTIDAS = 5

#: La media de un solucionador que conoce la lista de soluciones y elige siempre el intento que más informa
#: (máxima entropía). Medida sobre las 1.701 soluciones distintas de La Palabra del Día, sin tildes: 3,407. Es
#: la referencia de «jugar perfecto»; la estrategia óptima demostrada para el Wordle en inglés da 3,421.
MEDIA_DEL_SOLUCIONADOR = 3.41

#: Cuántas veces se sortean las palabras probadas para estimar las candidatas. Se toma la mediana.
SORTEOS = 15

#: El patrón de una fila acertada.
ACIERTO = "GGGGG"

#: Una fila legible: cinco colores.
FILA = re.compile(r"[GY.]{5}")

#: Lo que vale un fallo en la media, como en el marcador.
NOTA_DEL_FALLO = 7


def normaliza(palabra: str) -> str:
    """Minúsculas y sin tildes, como se juega. **La Ñ se conserva**: es una letra propia del juego."""
    sin_enie = str(palabra).lower().replace("ñ", "\0")
    plana = "".join(c for c in unicodedata.normalize("NFD", sin_enie) if unicodedata.category(c) != "Mn")
    return plana.replace("\0", "ñ")


def colores(intento: str, respuesta: str) -> str:
    """Los colores de un intento: `G` en su sitio, `Y` en otro sitio, `.` no está. Con letras repetidas, como el
    juego: primero las verdes, y cada amarilla gasta una letra de la respuesta que no fuera ya verde."""
    fila = ["."] * 5
    sobrantes: Counter = Counter()
    for i in range(5):
        if intento[i] == respuesta[i]:
            fila[i] = "G"
        else:
            sobrantes[respuesta[i]] += 1
    for i in range(5):
        if fila[i] == "." and sobrantes[intento[i]] > 0:
            fila[i] = "Y"
            sobrantes[intento[i]] -= 1
    return "".join(fila)


def candidatas_antes(filas: list[str], respuesta: str, universo: list[str], semilla) -> list[int] | None:
    """Las soluciones aún posibles antes de cada intento. La primera es el universo entero.

    Para las siguientes se sortea, en cada fila, una palabra del universo que dé esos colores contra la respuesta,
    y se cuentan las soluciones compatibles con todo lo visto; se repite `SORTEOS` veces y se toma la mediana. El
    sorteo usa `random.Random(semilla)` y el universo ordenado: con la misma semilla, el mismo resultado en
    cualquier proceso. Devuelve `None` si alguna fila no la produce ninguna palabra: la partida no se puede leer.
    """
    universo = sorted(universo)
    respuesta = normaliza(respuesta)
    # **Toda fila se valida, también la última**: cinco colores, ningún acierto antes del final, y que alguna
    # palabra pueda producirla contra la respuesta. Una fila ilegible descarta la partida entera.
    if not filas or any(not FILA.fullmatch(fila) for fila in filas) or ACIERTO in filas[:-1]:
        return None
    producibles = {}
    for fila in filas:
        if fila not in producibles:
            producibles[fila] = [w for w in universo if colores(w, respuesta) == fila]
        if not producibles[fila]:
            return None
    # Antes del intento k cuentan las filas anteriores: la última fila no informa a ningún intento.
    previas = list(filas[:-1])
    opciones = [producibles[fila] for fila in previas]
    if not previas:
        return [len(universo)]

    azar = random.Random(semilla)
    por_intento: list[list[int]] = [[] for _ in previas]
    for _ in range(SORTEOS):
        vivas = universo
        for i, (fila, quien) in enumerate(zip(previas, opciones)):
            intento = azar.choice(quien)
            vivas = [w for w in vivas if colores(intento, w) == fila]
            por_intento[i].append(len(vivas))
    return [len(universo)] + [round(statistics.median(tamanos)) for tamanos in por_intento]


def suerte_de_partida(filas: list[str], candidatas: list[int]) -> float:
    """Lo que acertó menos lo que le tocaba: por cada intento, 1 si acierta (0 si no) menos 1/candidatas.

    Acertar con una sola candidata suma cero —1 − 1—: es saber la palabra, no suerte.
    """
    return sum((1 if fila == ACIERTO else 0) - 1 / max(1, n) for fila, n in zip(filas, candidatas))


def apertura_de(partidas: list[dict]) -> list[float | None]:
    """La mediana de candidatas tras el primer y tras el segundo intento. Una partida resuelta antes no cuenta."""
    tras = []
    for k in (1, 2):
        valores = [p["candidatas"][k] for p in partidas if len(p["candidatas"]) > k]
        tras.append(_redondea(statistics.median(valores)) if valores else None)
    return tras


def milagro_de(partidas: list[dict]) -> dict | None:
    """La partida resuelta con más candidatas en el intento que acertó; a igualdad, la jornada más antigua."""
    resueltas = [p for p in partidas if p["resuelta"]]
    if not resueltas:
        return None
    mejor = min(resueltas, key=lambda p: (-p["candidatas"][-1], p["jornada"]))
    return {"jornada": mejor["jornada"], "intentos": mejor["intentos"], "candidatas": mejor["candidatas"][-1]}


def _redondea(valor: float, decimales: int = 1) -> float:
    redondo = round(float(valor), decimales)
    return int(redondo) if redondo == int(redondo) else redondo


def _nota(fila: dict) -> int:
    score = fila.get("score")
    return score if isinstance(score, int) and 1 <= score <= 6 else NOTA_DEL_FALLO


def indicadores(resultados: list[dict], temporada: str, soluciones: list[dict], hasta: int) -> dict:
    """Los indicadores de la temporada, por jugador y del grupo.

    `soluciones` son las entradas de la lista del juego (`{id, solution}`) y `hasta` la última jornada de la tabla:
    no se lee ninguna solución posterior. El universo de candidatas son las soluciones ya jugadas, sin tildes.
    """
    respuestas: dict[int, str] = {}
    for entrada in soluciones:
        # La lista viene de fuera y puede cambiar de forma: lo que no sea una entrada de cinco letras se ignora.
        jornada = entrada.get("id") if isinstance(entrada, dict) else None
        if isinstance(jornada, int) and jornada <= hasta:
            palabra = palabra_de([entrada], jornada, hasta)
            if isinstance(palabra, str) and len(normaliza(palabra)) == 5:
                respuestas[jornada] = normaliza(palabra)
    universo = sorted(set(respuestas.values()))

    cuentan = resultados_de_temporada(resultados, temporada)
    por_jugador: dict[str, list[dict]] = defaultdict(list)
    notas: dict[str, list[int]] = defaultdict(list)
    for fila in cuentan:
        jugador = fila["slack_user_id"]
        notas[jugador].append(_nota(fila))
        respuesta = respuestas.get(fila.get("wordle_id"))
        if not fila.get("pattern") or not respuesta:
            continue
        filas = str(fila["pattern"]).split("/")
        candidatas = candidatas_antes(filas, respuesta, universo, semilla=f"jornada-{fila['wordle_id']}")
        if candidatas is None:
            continue
        por_jugador[jugador].append({
            "jornada": fila["wordle_id"],
            "intentos": len(filas),
            "resuelta": filas[-1] == ACIERTO,
            "candidatas": candidatas,
            "suerte": suerte_de_partida(filas, candidatas),
        })

    todas = [p for partidas in por_jugador.values() for p in partidas]
    todas_las_notas = [n for lista_ in notas.values() for n in lista_]
    grupo = {
        "media": round(statistics.mean(todas_las_notas), 2) if todas_las_notas else None,
        "apertura": apertura_de(todas),
        "suerte_por_partida": round(statistics.mean(p["suerte"] for p in todas), 3) if todas else None,
        "partidas": len(todas),
    }

    jugadores = {}
    for jugador in notas:
        partidas = por_jugador.get(jugador, [])
        if len(partidas) < MINIMO_DE_PARTIDAS:
            jugadores[jugador] = {"partidas": len(partidas), "faltan": MINIMO_DE_PARTIDAS - len(partidas)}
            continue
        suerte = sum(p["suerte"] for p in partidas)
        jugadores[jugador] = {
            "partidas": len(partidas),
            "media": round(statistics.mean(notas[jugador]), 2),
            "apertura": apertura_de(partidas),
            "suerte": round(suerte, 2),
            "suerte_por_partida": round(suerte / len(partidas), 3),
            "milagro": milagro_de(partidas),
        }

    return {
        "minimo": MINIMO_DE_PARTIDAS,
        "referencia": MEDIA_DEL_SOLUCIONADOR,
        "grupo": grupo,
        "jugadores": jugadores,
    }
