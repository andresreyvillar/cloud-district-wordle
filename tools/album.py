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
from seasons import TEMPORADA_CERO, resultados_de_temporada

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

#: Lo que vale cada figura. **Decisión del dueño el 2026-08-09**: geométrico por encima de loro, y loro por
#: encima de flores.
#:
#: El orden sale de la rareza medida sobre la temporada 0 —geométrico 7,4%, loro 13,6%, flores 46,5%— así
#: que un geométrico es unas seis veces más raro que una flor. La escala se queda en **3/2/1 y no en 6/3/1**
#: a propósito: con 5/3/1 el podio es exactamente el mismo, así que la escala corta se explica igual de bien
#: y se recuerda mejor —«un geométrico vale tres flores»— sin cambiar a nadie de sitio.
#:
#: **Coste declarado.** Con todas las figuras valiendo 1, el podio de belleza no comparte a nadie con el de
#: puntuación, que es la razón por la que existe este segundo eje. Ponderando, Andrés R. —segundo en
#: puntuación— entra en el podio de belleza. Se acepta porque lo decide el dueño, no porque la medida lo
#: recomiende.
PUNTOS: dict[str, int] = {"geometrico": 3, "loro": 2, "flores": 1, ABSTRACTO: 0}


def categorias() -> list[dict]:
    """El catálogo que viaja en la instantánea: clave, emoji y si puntúa, **en orden**.

    Va como lista y no como diccionario porque **JSONB no conserva el orden de las claves**: Postgres las
    devuelve ordenadas por longitud y luego alfabéticamente, así que un diccionario llegaría a la web con
    `abstracto` antes que `geometrico`. Comprobado contra la instantánea real, no supuesto.

    Y viaja con el álbum en lugar de vivir en la web porque un mapa de categoría a emoji escrito en
    JavaScript sería una segunda verdad, que se queda atrás en cuanto se añada o renombre una categoría.
    """
    return [
        {
            "clave": categoria,
            "emoji": VOCABULARIO[categoria],
            "puntua": categoria in FIGURAS,
            "puntos": PUNTOS[categoria],
        }
        for categoria in CATEGORIAS
    ]


#: Jornadas que se usan de denominador, por temporada.
#:
#: **Faltar no puede mejorar la media**, que es la propiedad que el marcador protege con un escenario propio
#: (`faltar-nunca-mejora-la-media`) y que el álbum no tenía. Medido el 2026-08-12: dos jugadores con los
#: mismos 8 puntos, uno tras jugar las 8 jornadas con 3 abstractos y otro tras jugar 5 sin ninguno, salían a
#: 1,00 y 1,60. El segundo ganaba **por haber faltado tres días**: sus abstractos no existían porque no llegó
#: a jugarlos. Quien juega solo los días que le sale algo bonito tenía media perfecta.
#:
#: Con las jornadas de la temporada como denominador, los dos quedan a 1,00: hicieron lo mismo, y uno además
#: apareció todos los días.
#:
#: **La temporada 0 se queda con las partidas jugadas.** Son 181 jornadas de dieciocho meses en las que la
#: gente entró y salió del grupo; medir contra 181 no dice quién dibuja mejor, dice quién estaba desde el
#: principio. Es coherente con su propia regla: la temporada 0 se rige por lo que estaba en vigor cuando se
#: jugó. Decisión del dueño el 2026-08-12.
def _denominador(temporada: str, jornadas: int, partidas: int) -> int:
    return partidas if temporada == TEMPORADA_CERO else max(jornadas, partidas)


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
        "jornadas": len({fila["wordle_id"] for fila in cuentan}),
        "jugadores": _ranking(
            recuentos,
            nombre_de,
            _puntuacion_general(resultados, temporada),
            temporada,
            len({fila["wordle_id"] for fila in cuentan}),
        ),
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


#: Lo que se le supone a quien no aparece en la tabla de puntuación. Por encima del peor resultado posible,
#: así que ordena al final sin competir con nadie.
SIN_PUNTUACION = 99.0


def _puntuacion_general(resultados: list[dict], temporada: str) -> dict[str, float]:
    """La media de la tabla de puntuación de cada jugador, para deshacer empates en el álbum.

    Import local para no crear un ciclo: `standings` importa `badges` y `badges` importa este módulo.
    """
    from standings import clasificacion

    return {fila["jugador"]: fila["media_temporada"] for fila in clasificacion(resultados, temporada)}


def _ranking(
    recuentos: dict[str, Counter[str]],
    nombre_de: dict[str, str],
    puntuacion: dict[str, float],
    temporada: str = "",
    jornadas: int = 0,
) -> list[dict]:
    """Las filas del álbum, ordenadas.

    Orden: puntos por partida descendente; **a igualdad, mejor media en la tabla de puntuación**; luego más
    figuras; y por último el nombre, para que el resultado no dependa del orden de las filas.

    **El desempate por puntuación es decisión del dueño (2026-08-09)** y responde a un problema real: en una
    temporada de cinco jornadas jugadas por todo el mundo, la puntuación del álbum solo puede tomar seis
    valores, así que siete de ocho jugadores acababan empatados. Y no eran empates de redondeo — tenían
    **colecciones idénticas**, las mismas figuras en el mismo número—, así que ningún criterio sacado del
    propio álbum podía separarlos.

    Se descartó el otro candidato, premiar a quien publica antes: medido, `created_at` no captura el orden
    real de publicación. Solo el 34% de los resultados de una jornada tienen minuto distinto, porque el cron
    los escribe por lotes cada hora, y en ninguna jornada del histórico son todos distintos. Ordenar por ahí
    premiaría a quien cayó del lado bueno de una hora en punto.

    Precio declarado: acopla los dos ejes. El álbum existe para premiar a otra gente que el marcador, y
    ahora el marcador decide sus empates. Solo actúa cuando el criterio propio ya no distingue.
    """
    filas: list[dict] = []
    for jugador, cuenta in recuentos.items():
        partidas = sum(cuenta.values())
        denominador = _denominador(temporada, jornadas, partidas)
        figuras = sum(cuenta[categoria] for categoria in FIGURAS)
        puntos = sum(PUNTOS[categoria] * cuenta[categoria] for categoria in CATEGORIAS)
        filas.append(
            {
                "jugador": jugador,
                "nombre": nombre_de[jugador],
                "partidas": partidas,
                "figuras": figuras,
                "puntos": puntos,
                #: Las jornadas contra las que se mide. En una temporada mensual son las de la temporada,
                #: para que faltar no mejore la media; en la 0, las partidas jugadas.
                "denominador": denominador,
                # **Por jornada de la temporada, no por partida jugada ni en total.** El total corona a quien
                # más juega —un ranking de asistencia con otro nombre— y por partida jugada premiaba a quien
                # faltaba: sus abstractos no llegaban a existir. Ver `_denominador`.
                "media": round(puntos / denominador, PRECISION),
                "tasa": round(figuras / partidas, PRECISION),
                "recuento": {categoria: cuenta[categoria] for categoria in CATEGORIAS},
                "clasificado": partidas >= MINIMO_PARA_EL_ALBUM,
            }
        )

    def orden(fila):
        return (
            not fila["clasificado"],  # quien no clasifica, al final
            -fila["media"],
            puntuacion.get(fila["jugador"], SIN_PUNTUACION),  # mejor media de puntuación, delante
            -fila["figuras"],
            fila["nombre"].lower(),
        )

    filas.sort(key=orden)
    # Puesto compartido cuando la tasa es la misma, igual que en el marcador de puntuación
    # (slice `empates-comparten-puesto`): tres jugadores al 80% no han hecho uno mejor que otro, y el
    # desempate existe para que la lista sea determinista, no para separarlos.
    # Se comparte puesto solo cuando **ni el desempate** separa: mismo criterio propio, misma puntuación
    # general y mismas figuras. Comparar solo la media dejaba siete de ocho jugadores empatados en agosto.
    posicion = 0
    vistos = 0
    anterior = None
    for fila in filas:
        if not fila["clasificado"]:
            fila["posicion"] = None
            continue
        vistos += 1
        clave = orden(fila)[:-1]  # todo menos el nombre, que es solo para que el orden sea estable
        if clave != anterior:
            posicion = vistos
            anterior = clave
        fila["posicion"] = posicion
    return filas
