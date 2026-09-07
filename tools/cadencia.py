"""Si la sincronización cumple la cadencia acordada. **Funciones puras.**

Slice: `cadencia-de-sincronizacion` (openspec/slices/ranking/cadencia-de-sincronizacion.md).

El planificador de GitHub no cumple lo que se le declara —medido aquí: 4-9 ejecuciones de 24 al día, con
huecos de hasta 8,6 h— y ningún reloj externo ha funcionado. Así que la cadencia deja de ser una esperanza y
pasa a ser **un requisito con dos números**, auditable contra el histórico real.

Esto no dispara nada: es el criterio, escrito una vez, contra el que se comprueba si el mecanismo —las
ventanas de cron y el latido— está dando lo que se pidió.
"""

from __future__ import annotations

import datetime

#: Ejecuciones mínimas por día completo. Decisión del dueño: no hace falta puntualidad, hace falta frecuencia.
MINIMO_DIARIO = 12

#: Horas máximas de silencio entre dos ejecuciones. Decisión del dueño.
HUECO_MAXIMO_EN_HORAS = 2.0


def _cuando(marca: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(marca.replace("Z", "+00:00"))


def huecos_en_horas(marcas: list[str], hasta: str | None = None) -> list[float]:
    """Los silencios, en horas, de una serie de ejecuciones.

    Cuenta tres cosas, y las tres hacen falta:

    - el hueco **entre** cada dos ejecuciones consecutivas;
    - el tramo desde el comienzo del primer día hasta la primera ejecución;
    - el tramo desde la última ejecución hasta `hasta`, si se da.

    **`hasta` entra por parámetro y nunca se lee del reloj** (§10). Sin él el silencio final no se puede
    juzgar: no se sabe si es silencio o si simplemente todavía no ha pasado el tiempo. Y sin contar los
    bordes, doce ejecuciones agrupadas en dos horas no tenían ningún hueco grande *entre* ellas y dejaban
    veintidós horas de nada sin que se detectara — lo destapó su propio test.
    """
    if not marcas:
        return []
    momentos = sorted(_cuando(m) for m in marcas)
    inicio_del_dia = momentos[0].replace(hour=0, minute=0, second=0, microsecond=0)

    huecos = [(momentos[0] - inicio_del_dia).total_seconds() / 3600]
    huecos += [(b - a).total_seconds() / 3600 for a, b in zip(momentos, momentos[1:])]
    if hasta:
        huecos.append((_cuando(hasta) - momentos[-1]).total_seconds() / 3600)
    return huecos


def evalua(marcas: list[str], hasta: str | None = None) -> dict:
    """Si un conjunto de ejecuciones cumple la cadencia, y por qué no si no la cumple.

    `marcas` son instantes ISO 8601 y `hasta` el momento hasta el que se juzga la cobertura. El mismo
    histórico da siempre el mismo veredicto, que es lo que permite fijarlo en un test.

    El **día de `hasta`** no se juzga por su recuento: se presume en curso, y exigirle doce ejecuciones a media
    mañana suspendería siempre al día de hoy. Sus silencios sí cuentan.

    Sin ejecuciones **no se afirma que la cadencia se cumpla**: un conjunto vacío no es una cadencia buena,
    es la ausencia de datos.
    """
    por_dia: dict[str, list[str]] = {}
    for marca in marcas:
        por_dia.setdefault(marca[:10], []).append(marca)

    huecos = huecos_en_horas(marcas, hasta)
    excesivos = [h for h in huecos if h > HUECO_MAXIMO_EN_HORAS]
    en_curso = (hasta or "")[:10] or (sorted(por_dia)[-1] if por_dia else "")
    flojos = sorted(d for d, suyas in por_dia.items() if len(suyas) < MINIMO_DIARIO and d != en_curso)

    return {
        "dias": len(por_dia),
        "ejecuciones": len(marcas),
        "dias_por_debajo": flojos,
        "hueco_maximo": max(huecos) if huecos else 0.0,
        "huecos_excesivos": len(excesivos),
        "cumple": bool(marcas) and not flojos and not excesivos,
    }
