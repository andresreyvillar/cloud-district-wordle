"""Días laborables: la única definición del proyecto.

Slice: `medallas-en-el-resumen-diario` (regla de temporada, ver
docs/context/briefs/reglas-temporadas.md).

**Una temporada son sus días laborables.** Sábado y domingo no cuentan: no fijan la dificultad de un día,
no cuentan para ningún umbral y no son días que un jugador pueda faltar.

Módulo propio y no un helper dentro de `badges.py` porque la regla la consumen tres dominios: las medallas
(ya), el modelo de participación y el ranking de figuras (cuando existan). El proyecto ya se llevó un
sobresalto por tener dos definiciones de "día difícil" repartidas por el código; con "día laborable" la
tentación es la misma y el resultado sería peor, porque un desfase aquí cambia quién gana el mes.

El día de la semana sale **de la fecha de la fila**, nunca del reloj (§10 del protocolo).

Lo que este módulo NO hace: festivos. Un festivo laborable en el que casi nadie juega ya lo absorbe el
umbral de muestra mínima del día. Un calendario de festivos es un dominio nuevo y nadie lo ha pedido.
"""

from __future__ import annotations

import datetime

#: `isoweekday()` numera lunes=1 … domingo=7. Laborable es hasta el viernes.
ULTIMO_DIA_LABORABLE = 5


def dia_de_la_semana(fecha) -> int | None:
    """El `isoweekday()` de la fecha, o `None` si no se puede interpretar.

    Acepta `date`, `datetime` y cadena ISO: la columna `date` llega como cadena desde PostgREST y como
    objeto desde el código del pipeline, y las dos formas están en el histórico.
    """
    if isinstance(fecha, datetime.date):  # datetime.datetime también entra aquí, es subclase
        return fecha.isoweekday()
    try:
        return datetime.date.fromisoformat(str(fecha)[:10]).isoweekday()
    except (TypeError, ValueError):
        return None


def es_laborable(fecha) -> bool:
    """Si esa fecha es de lunes a viernes.

    Una fecha ilegible **no** es laborable. Excluir es lo conservador: contar una fila cuyo día se
    desconoce la mete en un cálculo de temporada sin saber si le corresponde.
    """
    dia = dia_de_la_semana(fecha)
    return dia is not None and dia <= ULTIMO_DIA_LABORABLE


def solo_laborables(resultados: list[dict]) -> list[dict]:
    """Los resultados de lunes a viernes, en el mismo orden."""
    return [fila for fila in resultados if es_laborable(fila.get("date"))]
