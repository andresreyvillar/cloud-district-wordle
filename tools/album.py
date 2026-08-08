"""El álbum de figuras de una temporada: qué dibujó cada jugador y en qué proporción.

Slice: `clasificacion-de-figuras` (openspec/slices/ranking/clasificacion-de-figuras.md).

Es el **segundo ranking**, independiente del de puntuación por decisión explícita del brief
([ranking-de-figuras](../docs/context/briefs/ranking-de-figuras.md)). Este módulo no clasifica nada: aplica
`figures.figura` a los patrones que la temporada ya considera suyos y cuenta.

**La categoría no se almacena.** Se deriva del patrón crudo en cada materialización, así que recalibrar un
umbral reclasifica el histórico solo, sin migración. El precio declarado es que cambia el álbum de todo el
mundo a la vez.

Funciones puras: sin reloj y sin red (§10 del protocolo).
"""

from __future__ import annotations

from collections import Counter

from figures import ABSTRACTO, FIGURAS, VOCABULARIO, figura
from seasons import resultados_de_temporada

#: Partidas clasificadas que hacen falta para tener puesto en el ranking de belleza.
#:
#: Medido sobre la temporada 0, no elegido por redondo: con 3 la gana alguien con un **100% de tres
#: partidas**; con 5, 8 y 10 el líder es el mismo (83% de 86). Es el umbral más bajo que mata la anomalía.
#:
#: Coincide con el `MINIMO_PARA_CLASIFICAR` de la tabla de puntuación, que venía del legacy. Se declara
#: aquí y no se importa de allí porque responde a otra pregunta: aquel mide días jugados de una temporada
#: sin imputación, este mide partidas con dibujo. Que hoy valgan lo mismo es una coincidencia, y atarlos
#: haría que mover uno moviera el otro sin querer.
MINIMO_PARA_EL_ALBUM = 5

#: Decimales de la tasa. Cuatro llegan para ordenar sin que el ruido del coma flotante decida un empate
#: que a la vista es idéntico, y para que el JSON de la instantánea no lleve dieciséis dígitos.
PRECISION = 4

#: Las cuatro categorías, en el orden en que se muestran: primero las que puntúan.
CATEGORIAS: tuple[str, ...] = FIGURAS + (ABSTRACTO,)


def categorias() -> list[dict]:
    """El catálogo que viaja en la instantánea: clave, emoji y si puntúa, **en orden**.

    Va como lista y no como diccionario porque **JSONB no conserva el orden de las claves**: Postgres las
    devuelve ordenadas por longitud y luego alfabéticamente, así que un diccionario llegaría a la web con
    `abstracto` antes que `geometrico`. Comprobado contra la instantánea real, no supuesto.

    Y viaja con el álbum en lugar de vivir en la web porque un mapa de categoría a emoji escrito en
    JavaScript sería una segunda verdad, que se queda atrás en cuanto se añada o renombre una categoría.
    """
    return [
        {"clave": categoria, "emoji": VOCABULARIO[categoria], "puntua": categoria in FIGURAS}
        for categoria in CATEGORIAS
    ]


def album(resultados: list[dict], temporada: str) -> dict:
    """El álbum de una temporada: reparto, cobertura y una fila por jugador con algo que clasificar.

    Se calcula sobre `resultados_de_temporada`, así que **hereda la definición de qué jornada cuenta** en
    lugar de tener la suya. Dos definiciones de lo mismo ya divergieron dos veces en este repositorio.
    """
    cuentan = resultados_de_temporada(resultados, temporada)

    reparto: Counter[str] = Counter()
    recuentos: dict[str, Counter[str]] = {}
    nombre_de: dict[str, str] = {}
    sin_patron = 0

    for fila in cuentan:
        patron = fila.get("pattern")
        if not patron:
            # Sin dibujo no hay veredicto. Contarlo como abstracto castigaría a quien jugó cuando el
            # pipeline todavía descartaba la cuadrícula: un fallo del sistema cobrado al jugador.
            sin_patron += 1
            continue
        jugador = fila["slack_user_id"]
        categoria = figura(patron)
        reparto[categoria] += 1
        recuentos.setdefault(jugador, Counter())[categoria] += 1
        nombre_de[jugador] = fila.get("player_name") or jugador

    return {
        "minimo": MINIMO_PARA_EL_ALBUM,
        "clasificadas": sum(reparto.values()),
        "sin_patron": sin_patron,
        "reparto": {categoria: reparto[categoria] for categoria in CATEGORIAS},
        "categorias": categorias(),
        "jugadores": _ranking(recuentos, nombre_de),
        "ultima_jornada": _ultima_jornada(resultados, temporada),
    }


def _ultima_jornada(resultados: list[dict], temporada: str) -> dict:
    """La jornada más reciente de la temporada, con la figura de cada quien publicó cuadrícula.

    **Se calcula sobre todos los resultados de la temporada, cuenten o no sus días.** El álbum de arriba solo
    cuenta lo que puntúa; esto responde otra pregunta —qué se ha dibujado hoy— y una jornada abierta todavía
    no alcanza la muestra mínima a media mañana. Sus dibujos existen igual.

    Se publica **una sola jornada**. Publicar el histórico añadiría miles de entradas que nadie lee: la vista
    de hoy mira hoy.
    """
    from seasons import temporada_de

    de_la_temporada = [fila for fila in resultados if temporada_de(fila["date"]) == temporada]
    if not de_la_temporada:
        return {"jornada": None, "figuras": {}}

    jornada = max(fila["wordle_id"] for fila in de_la_temporada)
    return {
        "jornada": jornada,
        "figuras": {
            fila["slack_user_id"]: figura(fila["pattern"])
            for fila in de_la_temporada
            if fila["wordle_id"] == jornada and fila.get("pattern")
        },
    }


def _ranking(recuentos: dict[str, Counter[str]], nombre_de: dict[str, str]) -> list[dict]:
    """Las filas del álbum, ordenadas.

    Orden: tasa descendente; a igualdad **más figuras delante**, porque sostener una proporción durante más
    partidas dice más que alcanzarla en cinco; y a igualdad de figuras, por nombre, para que el resultado no
    dependa del orden en que la base de datos devolvió las filas.
    """
    filas: list[dict] = []
    for jugador, cuenta in recuentos.items():
        partidas = sum(cuenta.values())
        figuras = sum(cuenta[categoria] for categoria in FIGURAS)
        filas.append(
            {
                "jugador": jugador,
                "nombre": nombre_de[jugador],
                "partidas": partidas,
                "figuras": figuras,
                "tasa": round(figuras / partidas, PRECISION),
                "recuento": {categoria: cuenta[categoria] for categoria in CATEGORIAS},
                "clasificado": partidas >= MINIMO_PARA_EL_ALBUM,
            }
        )

    filas.sort(
        key=lambda fila: (
            not fila["clasificado"],  # quien no clasifica, al final
            -fila["tasa"],
            -fila["figuras"],
            fila["nombre"].lower(),
        )
    )
    posicion = 0
    for fila in filas:
        if fila["clasificado"]:
            posicion += 1
            fila["posicion"] = posicion
        else:
            fila["posicion"] = None
    return filas
