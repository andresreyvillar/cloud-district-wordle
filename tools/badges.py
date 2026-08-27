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
from figures import rasgos

# El umbral de muestra vive en `seasons` porque es parte de qué es un día de temporada. Se importa en lugar
# de copiarse: el docstring de este módulo ya decía que quería ser el mismo criterio, y ahora lo es.
from seasons import MUESTRA_MINIMA_DEL_DIA  # noqa: F401  (se re-exporta: los tests lo leen de aquí)
from seasons import temporada_de

FALLO = 7

UMBRAL_DIA_IMPOSIBLE = 5.5
UMBRAL_DIA_DIFICIL = 4.5
RESOLVER_RAPIDO = 4

MINIMO_SUPERVIVIENTE = 3
MINIMO_VERDUGO = 5
MINIMO_IMPECABLE = 10
MINIMO_FONDISTA = 15
MINIMO_DIAS_PARA_METRONOMO = 10

#: Umbrales de las medallas de figura, **remedidos el 2026-08-08 con el clasificador calibrado**.
#:
#: Los del brief se midieron con el clasificador que luego se desmintió, y el propio brief pedía rehacerlos
#: «junto a la calibración, no por separado». Con el bueno se habían descolocado del todo: Florista (5
#: flores) la lograba el 63% cuando era «raro, 8%», y Abstract@ (12) el 0,8% cuando era «común, 24%».
#:
#: Medido sobre 122 pares jugador-mes, con las jornadas que cuentan de verdad en cada temporada. Cada
#: umbral está justo por debajo del máximo que alguien ha llegado a hacer —loro 8, geométrico 4, flores 18,
#: abstracto 14— que es donde un logro es difícil sin ser imposible:
#:
#:     Ornitólog@  5 loros        3,3%  legendario
#:     Arquitect@  4 geométricos  1,6%  legendario
#:     Florista   11 flores      11,5%  raro
#:     Abstract@   7 abstractos  23,0%  común
#:
#: Excluir agosto de 2026 —el mes casi sin patrones— movía cada cifra menos de dos puntos, así que no se
#: excluye: un umbral que dependa de qué meses se miren no es un umbral.
MINIMO_ORNITOLOGO = 5
#: Filas de cuerpo que ha de tener un espejo para ser una gesta y no un accidente.
#:
#: **Tres, y el umbral es lo que hace el logro.** De los 19 espejos del histórico, siete tienen una sola fila
#: de cuerpo (`.GGG./GGGGG`) y son simétricos casi por casualidad. Medido sobre 1.706 cuadrículas:
#:
#:     cuerpo >= 1   19 (1,10%)  10 jugadores de 23
#:     cuerpo >= 2   12 (0,70%)   9 jugadores
#:     cuerpo >= 3    7 (0,41%)   7 jugadores   <- este
#:     cuerpo >= 4    1 (0,06%)   1 jugador
#:
#: Con uno, lo tendría el 43% del grupo y no distinguiría a nadie —el error que ya se cometió con una medalla
#: que tenían quince de dieciséis—. Con cuatro solo existiría una en toda la historia. Con tres sale una cada
#: cinco meses y la han logrado siete personas distintas: raro, y de verdad.
MINIMO_CUERPO_DEL_ESPEJO = 3

MINIMO_ARQUITECTO = 4
MINIMO_FLORISTA = 11
MINIMO_ABSTRACTO = 7


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
    Medalla("espejo-perfecto", "Espejo perfecto", "🪞", "legendario", "permanente"),
    Medalla("superviviente", "Superviviente", "🛡️", "legendario", "temporada"),
    Medalla("metronomo", "Metrónom@", "📅", "raro", "temporada"),
    Medalla("verdugo", "Verdugo", "🎯", "comun", "temporada"),
    Medalla("impecable", "Impecable", "✨", "comun", "temporada"),
    Medalla("fondista", "Fondista", "💪", "comun", "temporada"),
    # Las de figura. Todas de temporada: se pueden ganar cada mes, como las de constancia.
    Medalla("ornitologo", "Ornitólog@", "🦜", "legendario", "temporada"),
    Medalla("arquitecto", "Arquitect@", "📐", "legendario", "temporada"),
    Medalla("florista", "Florista", "🌷", "raro", "temporada"),
    Medalla("coleccionista", "Coleccionista", "🗂️", "comun", "temporada"),
    Medalla("abstracto", "Abstract@", "🌀", "comun", "temporada"),
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
    """Las filas de esa temporada, **según el modelo** y no según el prefijo de la fecha.

    Comparar el identificador con el principio de la fecha funcionaba mientras toda temporada era un
    `AAAA-MM`. Con la temporada 0 dejó de funcionar en silencio: ninguna fecha empieza por `0`, así que 181
    jornadas de histórico se quedaron sin una sola medalla de temporada mientras las permanentes seguían
    apareciendo. `temporada_de` es la misma función que decide a qué temporada pertenece un resultado en el
    ranking, así que las dos cosas no pueden volver a divergir.
    """
    return [fila for fila in resultados if temporada_de(fila["date"]) == temporada]


#: Qué categoría y qué umbral pide cada medalla de figura. `coleccionista` no está aquí: no pide cantidad de
#: una categoría sino variedad, así que tiene su propia condición.
UMBRAL_DE_FIGURA: tuple[tuple[str, str, int], ...] = (
    ("ornitologo", "loro", MINIMO_ORNITOLOGO),
    ("arquitecto", "geometrico", MINIMO_ARQUITECTO),
    ("florista", "flores", MINIMO_FLORISTA),
    ("abstracto", "abstracto", MINIMO_ABSTRACTO),
)


def _recuentos_de_figuras(resultados: list[dict], temporada: str) -> dict[str, dict[str, int]]:
    """Cuántas partidas de cada categoría lleva cada jugador, **según el álbum**.

    Se lee del álbum en lugar de contar aquí otra vez: si la tira dice `🦜5` y la medalla no salta, el logro
    parece roto. Un segundo recuento de lo mismo es la forma en que este repositorio ya se ha equivocado
    tres veces.

    El álbum indexa por identificador de Slack y las medallas por nombre, así que se reindexan. Los dos
    índices conviven desde `identidad-canonica-de-jugador` y unificarlos es otro slice.
    """
    from album import album

    return {fila["nombre"]: fila["recuento"] for fila in album(resultados, temporada)["jugadores"]}


def _de_figura(recuento: dict[str, int]) -> list[str]:
    """Las medallas de figura que da un recuento por categoría."""
    ganadas = [
        clave for clave, categoria, umbral in UMBRAL_DE_FIGURA if recuento.get(categoria, 0) >= umbral
    ]
    if all(recuento.get(categoria, 0) >= 1 for _, categoria, _ in UMBRAL_DE_FIGURA):
        ganadas.append("coleccionista")
    return ganadas


def medallas_de_temporada(resultados: list[dict], temporada: str) -> dict[str, list[str]]:
    """Las medallas de temporada de cada jugador en esa temporada.

    `resultados` puede abarcar varias temporadas: la ventana la fija el parámetro, no el reloj.

    Solo cuentan los días laborables, y el filtro va **aquí** y no en cada recuento: así todo lo derivado
    queda limpio de una vez —la dificultad del día, el mejor del día, el número de partidas y, el que
    importa, el conjunto de días que forman la temporada del que depende `Metrónom@`.
    """
    del_mes = _de_la_temporada(solo_laborables(resultados), temporada)
    if not del_mes:
        return {}

    dificultad = _dificultad_por_dia(del_mes)
    mejor = _mejor_del_dia(del_mes)
    dias_de_la_temporada = {fila["wordle_id"] for fila in del_mes}
    # Sobre `resultados` sin filtrar: el álbum aplica su propia definición de qué jornada cuenta, que es la
    # de la temporada. Pasarle `del_mes` le daría los días ya filtrados dos veces por criterios distintos.
    recuentos = _recuentos_de_figuras(resultados, temporada)

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

        if len(dias_de_la_temporada) >= MINIMO_DIAS_PARA_METRONOMO and jugados >= dias_de_la_temporada:
            ganadas.append("metronomo")

        if sum(1 for fila in filas if fila["score"] == mejor[fila["wordle_id"]]) >= MINIMO_VERDUGO:
            ganadas.append("verdugo")

        if len(filas) >= MINIMO_IMPECABLE and all(fila["score"] < FALLO for fila in filas):
            ganadas.append("impecable")

        if len(filas) >= MINIMO_FONDISTA:
            ganadas.append("fondista")

        ganadas.extend(_de_figura(recuentos.get(jugador, {})))

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

        # El espejo perfecto: cuadrícula simétrica fila a fila y con cuerpo suficiente para que sea una gesta.
        # Se mira el rasgo, no la categoría: en `figures.figura()` el espejo se consulta en último lugar, así
        # que una cuadrícula simétrica puede acabar etiquetada como flor —le pasó a la de cuatro filas del
        # 27 de agosto— y la medalla se perdería si dependiera de la etiqueta.
        if "espejo-perfecto" not in palmares[jugador]:
            # Sin comprobar antes si hay patrón: `rasgos(None)` ya devuelve `espejo=False`, así que la guarda
            # era código sin efecto — la prueba de mutación lo destapó al no poder ponerla en rojo.
            r = rasgos(fila.get("pattern"))
            if r.espejo and r.alto >= MINIMO_CUERPO_DEL_ESPEJO:
                palmares[jugador].append("espejo-perfecto")

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

    # **Las medallas que gana exactamente la misma gente van juntas.** Sin esto, el bloque publicaba dos
    # líneas seguidas con los mismos cuatro nombres y distinto emoji —`Metrónom@` e `Impecable` las suele ganar
    # el mismo grupo—, y el mensaje decía dos veces lo mismo. Es la misma medicina que ya se aplicó a los
    # ausentes, a los aplaudidos y a los empatados, en el único bloque al que no había llegado.
    grupos: dict[tuple[str, ...], list] = {}
    for medalla in CATALOGO:  # el catálogo ya está en orden de rareza
        if medalla.clave in por_medalla:
            grupos.setdefault(tuple(sorted(por_medalla[medalla.clave])), []).append(medalla)

    lineas: list[str] = []
    for quienes, medallas in grupos.items():
        emojis = " ".join(m.emoji for m in medallas)
        # El nivel de la primera manda: el catálogo va en orden de rareza, así que es la más difícil del grupo.
        exclamacion = "¡" if medallas[0].nivel == "legendario" else ""
        cierre = "!" if medallas[0].nivel == "legendario" else ""
        nombres = " y ".join(m.nombre for m in medallas) if len(medallas) < 3 else (
            ", ".join(m.nombre for m in medallas[:-1]) + " y " + medallas[-1].nombre
        )
        lineas.append(f"{emojis} {exclamacion}{nombres}{cierre} — {', '.join(quienes)}")

    return "🏅 *Medallas de hoy*\n" + "\n".join(lineas)
