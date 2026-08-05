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


def temporada_de(fecha) -> str:
    """La temporada de una fecha: `AAAA-MM`.

    Recorta la cadena en lugar de parsear la fecha porque `date` llega como `AAAA-MM-DD` de PostgREST y
    como objeto del pipeline, y `str()` da la misma forma en los dos casos.
    """
    return str(fecha)[:7]


def _por_jornada(resultados: list[dict]) -> dict[int, list[dict]]:
    agrupado: dict[int, list[dict]] = defaultdict(list)
    for fila in resultados:
        agrupado[fila["wordle_id"]].append(fila)
    return agrupado


def dias_de_temporada(resultados: list[dict], temporada: str) -> list[int]:
    """Las jornadas que forman una temporada, ordenadas.

    Dos filtros independientes, y hacen falta los dos: **día laborable** excluye el fin de semana por regla,
    y **muestra mínima** excluye los laborables en que el grupo tampoco jugó (festivos, agosto).
    """
    del_mes = [fila for fila in resultados if temporada_de(fila["date"]) == temporada]
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
    presentes = sorted({temporada_de(fila["date"]) for fila in resultados}, reverse=True)
    return [
        {
            "temporada": temporada,
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
    # Import local para no crear un ciclo: `rules` importa de este módulo para leer sus constantes.
    from rules import catalogo, como_json

    dias = dias_de_temporada(resultados, temporada)
    cuentan = resultados_de_temporada(resultados, temporada)
    lista = temporadas(resultados)
    estado = next((e["estado"] for e in lista if e["temporada"] == temporada), CERRADA)

    return {
        "temporada": temporada,
        "estado": estado,
        "dias": dias,
        "resultados": len(cuentan),
        "jugadores": sorted({fila["slack_user_id"] for fila in cuentan}),
        # Las reglas viajan con la temporada: una cerrada conserva las que se le aplicaron, así que
        # mirar marzo explica marzo y no el mes que viene.
        "reglas": como_json(catalogo()),
    }
