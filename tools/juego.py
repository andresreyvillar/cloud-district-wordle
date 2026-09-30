"""La clasificación del SuperWordleBros en la temporada.

Slice: `clasificacion-del-juego` (openspec/slices/ranking/clasificacion-del-juego.md).

Cada día el grupo juega el nivel congelado de la jornada anterior y deja su mejor marca (`game_times`). Los
tiempos de niveles distintos **no se pueden sumar** —cada nivel tiene otro largo, según cuántos jugaron ese
día—, así que el mes se puntúa **por puesto en cada nivel**, decisión del dueño: 10, 8, 6, 5, 4, 3 y 2, y del
octavo en adelante 1, en el orden del ranking del nivel: más estrellas primero y, con las mismas, menos
tiempo. Premia ganar y también jugar a menudo.

Función pura (§10): resultados, niveles y marcas entran por parámetro. Lo que lee de la base de datos lo lee
el borde (`materialize_seasons.py`, `post_ranking.py`).
"""

from __future__ import annotations

from collections import defaultdict

from seasons import dias_de_temporada, temporada_de

#: Los puntos de los siete primeros puestos de cada nivel.
ESCALA = (10, 8, 6, 5, 4, 3, 2)

#: Los puntos del octavo en adelante. Uno, y no cero: terminar el nivel ya es jugar, y la escala premia jugar.
PUNTOS_DESDE_EL_OCTAVO = 1


def _centesimas(segundos) -> int:
    """El tiempo como se guarda y se compara: en centésimas. 30,001 y 30,004 son el mismo tiempo."""
    return round(float(segundos) * 100)


def puntos_del_puesto(puesto: int) -> int:
    return ESCALA[puesto - 1] if puesto <= len(ESCALA) else PUNTOS_DESDE_EL_OCTAVO


def _orden(marca: dict) -> tuple[int, int]:
    """Cómo se ordena un nivel: **más estrellas primero** y, con las mismas, menos tiempo. Las estrellas pesan
    más que el tiempo (decisión del dueño): 13 estrellas en 0:13 van por delante de 9 en 0:12."""
    return (-int(marca.get("estrellas") or 0), _centesimas(marca["segundos"]))


def puestos_de_nivel(marcas_del_nivel: list[dict]) -> dict[str, tuple[int, int]]:
    """`jugador -> (puesto, puntos)` en un nivel. Las mismas estrellas y el mismo tiempo en centésimas comparten
    puesto y puntos (1, 1, 3)."""
    ordenadas = sorted(marcas_del_nivel, key=lambda m: (*_orden(m), str(m["jugador"])))
    resultado: dict[str, tuple[int, int]] = {}
    puesto, anterior = 0, None
    for vistos, marca in enumerate(ordenadas, start=1):
        tiempo = _orden(marca)
        if tiempo != anterior:
            puesto, anterior = vistos, tiempo
        resultado[marca["jugador"]] = (puesto, puntos_del_puesto(puesto))
    return resultado


def _nombres(resultados: list[dict]) -> dict[str, str]:
    """El nombre de cada jugador en su fila **más reciente**: es como le conoce hoy el grupo."""
    ultima: dict[str, dict] = {}
    for fila in resultados:
        jugador = fila.get("slack_user_id")
        if not jugador:
            continue
        previa = ultima.get(jugador)
        if previa is None or (fila["wordle_id"], str(fila["date"])) > (previa["wordle_id"], str(previa["date"])):
            ultima[jugador] = fila
    return {jugador: fila.get("player_name") or jugador for jugador, fila in ultima.items()}


def niveles_que_puntuan(resultados: list[dict], niveles: list[dict], temporada: str) -> list[int]:
    """Las jornadas congeladas que dan puntos en la temporada, ordenadas.

    **Solo las de días que cuentan**: laborables con cinco jugadores, como en la clasificación general. Si no,
    un sábado con tres jugadores repartiría 10 puntos con un nivel de tres tramos. Y cada nivel cuenta en el
    mes de **su jornada**, no en el de la partida: el del día 30 se juega el 1 y es del mes que se cierra.
    """
    validas = set(dias_de_temporada(resultados, temporada))
    return sorted(
        nivel["jornada"]
        for nivel in niveles
        if nivel["jornada"] in validas and temporada_de(nivel["fecha"]) == temporada
    )


def clasificacion_del_juego(
    resultados: list[dict], niveles: list[dict], marcas: list[dict], temporada: str
) -> dict:
    """La clasificación del juego de una temporada: `{ escala, niveles, clasificacion }`.

    El mes suma los puntos de cada jugador. A igualdad de puntos **se comparte puesto**, como en el resto de
    clasificaciones; las victorias y el nombre solo deciden en qué orden se listan.
    """
    cuentan = niveles_que_puntuan(resultados, niveles, temporada)
    por_nivel: dict[int, list[dict]] = defaultdict(list)
    for marca in marcas:
        if marca["jornada"] in cuentan:
            por_nivel[marca["jornada"]].append(marca)

    puntos: dict[str, int] = defaultdict(int)
    jugados: dict[str, int] = defaultdict(int)
    victorias: dict[str, int] = defaultdict(int)
    for jornada in cuentan:
        for jugador, (puesto, de_puesto) in puestos_de_nivel(por_nivel[jornada]).items():
            puntos[jugador] += de_puesto
            jugados[jugador] += 1
            victorias[jugador] += puesto == 1

    nombres = _nombres(resultados)
    filas = [
        {
            "jugador": jugador,
            "nombre": nombres.get(jugador, jugador),
            "puntos": puntos[jugador],
            "niveles": jugados[jugador],
            "victorias": victorias[jugador],
        }
        for jugador in puntos
    ]
    filas.sort(key=lambda f: (-f["puntos"], -f["victorias"], f["nombre"].lower(), f["jugador"]))

    posicion, anterior = 0, None
    for vistos, fila in enumerate(filas, start=1):
        if fila["puntos"] != anterior:
            posicion, anterior = vistos, fila["puntos"]
        fila["posicion"] = posicion

    return {
        "escala": [*ESCALA, PUNTOS_DESDE_EL_OCTAVO],
        "niveles": len(cuentan),
        "clasificacion": [
            {clave: fila[clave] for clave in ("posicion", "jugador", "nombre", "puntos", "niveles", "victorias")}
            for fila in filas
        ],
    }
