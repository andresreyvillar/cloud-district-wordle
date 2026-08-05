"""El modelo de temporada: qué es una temporada y qué días la forman.

Slice: `temporada-mensual` (openspec/slices/ranking/temporada-mensual.md).

**Las temporadas son mensuales y el marcador se reinicia el día 1.** Es la única regla del juego decidida
por votación del grupo (6 a favor, 0 en contra).

Funciones puras: los resultados y la temporada entran por parámetro y nada lee el reloj (§10 del protocolo).
La temporada en curso se deriva **de los datos**, no de la fecha del sistema, y por eso el cálculo es
reproducible con fixtures fijos.

Este módulo vive en Python y no en la web por decisión explícita
([ADR 0008](../openspec/decisions/0008-donde-vive-el-calculo.md)): el bot publica en el canal quién va
ganando y la web lo muestra, así que las dos cosas tienen que salir del mismo cálculo por construcción.
"""

from __future__ import annotations

from collections import defaultdict

from calendario import es_laborable

#: Un día solo forma parte de la temporada si lo jugaron al menos estas personas. Con menos, la media del
#: día no calibra nada y una ausencia penalizaría en un día en que el grupo tampoco estaba.
#:
#: Vive **aquí** porque es parte de qué es un día de temporada. `tools/badges.py` lo importa de este módulo
#: en lugar de tener su propia copia: dos definiciones de lo mismo divergen, y una divergencia aquí cambia
#: quién gana el mes.
MUESTRA_MINIMA_DEL_DIA = 5

EN_CURSO = "en curso"
CERRADA = "cerrada"

#: El límite que parte el histórico. **Todo lo jugado antes es la temporada 0**; desde este mes, cada mes
#: natural es una temporada numerada. Decisión del dueño el 2026-08-05.
#:
#: Cambiar esta fecha RENUMERA todas las temporadas, así que conviene que esté acordada antes de tocarla.
INICIO_TEMPORADAS = "2026-08"

#: El identificador de la temporada 0. Los meses usan `AAAA-MM` para que un enlace pegado en el canal siga
#: diciendo de qué mes habla (ADR 0006); la temporada 0 no es un mes, así que usa su número.
TEMPORADA_CERO = "0"

MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)


def temporada_de(fecha) -> str:
    """La temporada de una fecha: `0` si es anterior al límite, su `AAAA-MM` si no.

    Recorta la cadena en lugar de parsear la fecha porque `date` llega como `AAAA-MM-DD` de PostgREST y
    como objeto del pipeline, y `str()` da la misma forma en los dos casos.
    """
    mes = str(fecha)[:7]
    return TEMPORADA_CERO if mes < INICIO_TEMPORADAS else mes


def ordinal(temporada: str) -> int:
    """El número de orden de una temporada. La 0 es la 0; el mes del límite es la 1.

    Se **deriva** del límite en lugar de almacenarse, así que no puede desincronizarse del modelo.
    """
    if temporada == TEMPORADA_CERO:
        return 0
    año, mes = (int(p) for p in temporada.split("-"))
    año0, mes0 = (int(p) for p in INICIO_TEMPORADAS.split("-"))
    return (año - año0) * 12 + (mes - mes0) + 1


def etiqueta(temporada: str) -> str:
    """Cómo se llama una temporada para el grupo."""
    if temporada == TEMPORADA_CERO:
        return "Temporada 0 · el histórico"
    año, mes = (int(p) for p in temporada.split("-"))
    return f"Temporada {ordinal(temporada)} · {MESES[mes - 1]} {año}"


def imputa(temporada: str) -> bool:
    """Si a esta temporada se le imputan las ausencias.

    La 0 no. De sus 159 días válidos, **siete de veinte jugadores tendrían más del 70% imputado** porque se
    incorporaron a lo largo del periodo: a quien entró el 22 de julio se le contarían 156 ausencias desde
    noviembre. Imputar ahí castiga por no jugar antes de estar, y además aplica hacia atrás unas reglas que
    no estaban en vigor.
    """
    return temporada != TEMPORADA_CERO


def _por_jornada(resultados: list[dict]) -> dict[int, list[dict]]:
    agrupado: dict[int, list[dict]] = defaultdict(list)
    for fila in resultados:
        agrupado[fila["wordle_id"]].append(fila)
    return agrupado


def dias_de_temporada(resultados: list[dict], temporada: str) -> list[int]:
    """Las jornadas que forman una temporada, ordenadas.

    En una temporada **numerada**, dos filtros independientes y hacen falta los dos: **día laborable**
    excluye el fin de semana por regla, y **muestra mínima** excluye los laborables en que el grupo tampoco
    jugó (festivos, agosto).

    En la **temporada 0 no se filtra nada**: cuenta toda jornada con algún resultado. Es lo que hacía la v1
    (`js/script.js`: `totalDays = new Set(results.map(r => r.wordleNumber)).size`), y la temporada 0 se rige
    por las reglas que estaban en vigor cuando se jugó. Son 181 jornadas frente a las 159 que quedarían
    filtrando.
    """
    del_mes = [fila for fila in resultados if temporada_de(fila["date"]) == temporada]
    if temporada == TEMPORADA_CERO:
        return sorted(_por_jornada(del_mes))
    return sorted(
        jornada
        for jornada, filas in _por_jornada(del_mes).items()
        if es_laborable(filas[0]["date"]) and len(filas) >= MUESTRA_MINIMA_DEL_DIA
    )


def resultados_de_temporada(resultados: list[dict], temporada: str) -> list[dict]:
    """Los resultados que cuentan en una temporada: los de sus días, en el orden de entrada."""
    dias = set(dias_de_temporada(resultados, temporada))
    return [
        fila
        for fila in resultados
        if temporada_de(fila["date"]) == temporada and fila["wordle_id"] in dias
    ]


def temporadas(resultados: list[dict]) -> list[dict]:
    """Una entrada por temporada con datos, de más reciente a más antigua.

    La más reciente está **en curso** y las demás cerradas. Se deriva de los datos y no del reloj: así el
    archivo no depende de cuándo se mire, y un mes sin jugar no adelanta el cierre del anterior.

    Una temporada cuyos días no alcanzan la muestra mínima **sigue apareciendo**, con cero días: hacerla
    desaparecer del archivo sería peor que mostrarla vacía.
    """
    todas = {temporada_de(fila["date"]) for fila in resultados}
    # La temporada 0 va siempre al final: es el bloque más antiguo y su identificador no ordena por fecha.
    meses = sorted(t for t in todas if t != TEMPORADA_CERO)
    presentes = list(reversed(meses)) + ([TEMPORADA_CERO] if TEMPORADA_CERO in todas else [])
    return [
        {
            "temporada": temporada,
            "ordinal": ordinal(temporada),
            "etiqueta": etiqueta(temporada),
            "estado": EN_CURSO if indice == 0 else CERRADA,
            "dias": len(dias_de_temporada(resultados, temporada)),
        }
        for indice, temporada in enumerate(presentes)
    ]


def instantanea(resultados: list[dict], temporada: str) -> dict:
    """La carga útil que se materializa para una temporada.

    Solo el modelo: qué días la forman, cuántos resultados cuentan y quién participó. **No ordena a nadie** —
    la clasificación y las medallas llegan con sus propios slices y añaden claves a esta carga útil, que es
    justo la razón de que sea JSONB y no columnas.
    """
    # Imports locales para no crear ciclos: los dos módulos importan de este.
    from badges import medallas_de_temporada, medallas_permanentes
    from rules import catalogo, como_json
    from standings import clasificacion, dificultad_por_dia

    dias = dias_de_temporada(resultados, temporada)
    cuentan = resultados_de_temporada(resultados, temporada)
    lista = temporadas(resultados)
    estado = next((e["estado"] for e in lista if e["temporada"] == temporada), CERRADA)

    tabla = clasificacion(resultados, temporada)
    dificultad = dificultad_por_dia(resultados, temporada)
    ordenadas = sorted(dificultad.items(), key=lambda par: (par[1], par[0]))
    mas_facil = ordenadas[0][0] if ordenadas else None
    mas_dificil = ordenadas[-1][0] if ordenadas else None
    media_grupo = (
        round(sum(fila["score"] for fila in cuentan) / len(cuentan), 2) if cuentan else 0.0
    )

    # Los logros, invertidos a `clave -> [quiénes]`, que es como los pinta la vista. Las permanentes se
    # calculan sobre los resultados de ESTA temporada: el palmarés completo es cosa de la ficha de jugador.
    ganadores: dict[str, list[str]] = defaultdict(list)
    for jugador, claves in medallas_de_temporada(resultados, temporada).items():
        for clave in claves:
            ganadores[clave].append(jugador)
    for jugador, claves in medallas_permanentes(cuentan).items():
        for clave in claves:
            if jugador not in ganadores[clave]:
                ganadores[clave].append(jugador)

    return {
        "temporada": temporada,
        "ordinal": ordinal(temporada),
        "etiqueta": etiqueta(temporada),
        "imputada": imputa(temporada),
        "estado": estado,
        "dias": dias,
        "resultados": len(cuentan),
        "jugadores": sorted({fila["slack_user_id"] for fila in cuentan}),
        # Las reglas viajan con la temporada: una cerrada conserva las que se le aplicaron, así que
        # mirar marzo explica marzo y no el mes que viene.
        "reglas": como_json(catalogo()),
        # El cálculo y el contexto que la vista necesita para ser legible. La web lee y pinta: no
        # recalcula, así que no puede divergir de lo que publica el bot (ADR 0008).
        "clasificacion": tabla,
        "dificultad": {str(jornada): media for jornada, media in dificultad.items()},
        "mas_dificil": mas_dificil,
        "mas_facil": mas_facil,
        "media_grupo": media_grupo,
        "logros": {clave: sorted(quienes) for clave, quienes in ganadores.items()},
    }
