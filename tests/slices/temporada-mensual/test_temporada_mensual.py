"""Escenarios de `temporada-mensual` (Fase 2 — TDD rojo).

Fixtures a mano y un doble de la tabla con la semántica del `upsert` real: la clave decide si inserta o
actualiza. El doble imita la **restricción**, no solo la interfaz — un doble más permisivo que producción ya
dejó pasar un fallo que reventó una migración a mitad (docs/lecciones.md, 2026-08-05).

Las fechas de los fixtures se calculan: agosto de 2026 empieza en sábado, así que numerar del 1 al 15
metería cinco fines de semana en un fixture de "quince días laborables".
"""

from __future__ import annotations

import calendar
import datetime

import pytest

MOTIVO = "TDD rojo — tools/seasons.py no existe todavía"

AHORA = datetime.datetime(2026, 8, 5, 7, 0, tzinfo=datetime.timezone.utc)


def _dias(mes: str, laborables: bool) -> list[int]:
    año, m = (int(parte) for parte in mes.split("-"))
    return [
        dia
        for dia in range(1, calendar.monthrange(año, m)[1] + 1)
        if (datetime.date(año, m, dia).isoweekday() <= 5) is laborables
    ]


def dia_laborable(n: int, mes: str) -> int:
    return _dias(mes, laborables=True)[n]


def dia_de_finde(n: int, mes: str) -> int:
    return _dias(mes, laborables=False)[n]


def jornada(wordle: int, mes: str, dia: int, jugadores: int, score: int = 4) -> list[dict]:
    """Una jornada con `jugadores` participantes, para controlar si alcanza la muestra mínima."""
    return [
        {
            "player_name": f"j{indice}",
            "slack_user_id": f"U_J{indice}",
            "wordle_id": wordle,
            "score": score,
            "date": f"{mes}-{dia:02d}",
        }
        for indice in range(jugadores)
    ]


class TablaFalsa:
    """Doble con la semántica del `upsert`: la clave decide si inserta o actualiza."""

    def __init__(self) -> None:
        self.por_clave: dict[tuple, dict] = {}
        self.escrituras = 0

    def upsert(self, fila: dict, clave: tuple[str, ...]) -> None:
        self.escrituras += 1
        self.por_clave[tuple(fila[columna] for columna in clave)] = fila

    @property
    def filas(self) -> list[dict]:
        return list(self.por_clave.values())


# @scenarios temporada-es-el-mes-de-la-fecha
def test_la_temporada_es_el_mes_de_la_fecha_y_el_dia_1_ya_es_la_nueva():
    from tools.seasons import temporada_de

    assert temporada_de("2026-08-01") == "2026-08"
    assert temporada_de("2026-07-31") == "2026-07"
    # sin periodo de gracia: el día 1 no pertenece al mes anterior
    assert temporada_de("2026-08-01") != temporada_de("2026-07-31")


# @scenarios temporada-es-el-mes-de-la-fecha
def test_la_temporada_sale_de_la_fecha_del_puzzle_y_no_de_cuando_se_publico():
    """La columna de fecha se deriva del número de puzzle, así que un resultado publicado tarde cae en su mes."""
    from tools.seasons import resultados_de_temporada

    # el puzzle del 31 de julio, aunque se publicase en agosto, tiene fecha de julio
    filas = jornada(1668, "2026-07", 31, 6) + jornada(1669, "2026-08", 3, 6)

    de_julio = resultados_de_temporada(filas, "2026-07")
    assert {fila["wordle_id"] for fila in de_julio} == {1668}


# @scenarios solo-los-dias-laborables-forman-la-temporada
def test_el_fin_de_semana_no_forma_parte_de_la_temporada():
    """Y no por falta de muestra: el sábado del fixture tiene seis jugadores."""
    from tools.seasons import dias_de_temporada

    sabado = jornada(1700, "2026-08", dia_de_finde(0, "2026-08"), 6)
    lunes = jornada(1701, "2026-08", dia_laborable(0, "2026-08"), 6)

    assert dias_de_temporada(sabado + lunes, "2026-08") == [1701]


# @scenarios dia-sin-muestra-no-forma-parte
def test_un_dia_de_pocos_jugadores_no_forma_parte_de_la_temporada():
    from tools.seasons import MUESTRA_MINIMA_DEL_DIA, dias_de_temporada

    assert MUESTRA_MINIMA_DEL_DIA == 5

    flojo = jornada(1710, "2026-08", dia_laborable(0, "2026-08"), MUESTRA_MINIMA_DEL_DIA - 1)
    justo = jornada(1711, "2026-08", dia_laborable(1, "2026-08"), MUESTRA_MINIMA_DEL_DIA)

    assert dias_de_temporada(flojo + justo, "2026-08") == [1711]


# @scenarios dia-sin-muestra-no-forma-parte
def test_una_temporada_sin_ningun_dia_valido_existe_y_esta_vacia():
    """Desaparecer del archivo sería peor que aparecer vacía."""
    from tools.seasons import instantanea, temporadas

    flojo = jornada(1720, "2026-08", dia_laborable(0, "2026-08"), 2)

    assert instantanea(flojo, "2026-08")["dias"] == []
    assert "2026-08" in {entrada["temporada"] for entrada in temporadas(flojo)}


# @scenarios temporada-en-curso-se-deriva-de-los-datos
def test_la_temporada_mas_reciente_con_datos_esta_en_curso():
    from tools.seasons import temporadas

    filas = (
        jornada(1600, "2026-06", dia_laborable(0, "2026-06"), 6)
        + jornada(1640, "2026-07", dia_laborable(0, "2026-07"), 6)
        + jornada(1670, "2026-08", dia_laborable(0, "2026-08"), 6)
    )
    lista = temporadas(filas)

    assert [entrada["temporada"] for entrada in lista] == ["2026-08", "2026-07", "2026-06"]
    assert lista[0]["estado"] == "en curso"
    assert {entrada["estado"] for entrada in lista[1:]} == {"cerrada"}


# @scenarios calculo-determinista
def test_el_calculo_no_depende_del_orden_ni_del_reloj():
    from tools.seasons import instantanea

    filas = jornada(1730, "2026-08", dia_laborable(0, "2026-08"), 6) + jornada(
        1731, "2026-08", dia_laborable(1, "2026-08"), 6
    )

    directo = instantanea(filas, "2026-08")
    invertido = instantanea(list(reversed(filas)), "2026-08")

    assert directo == invertido
    assert instantanea(filas, "2026-08") == directo


# @scenarios instantanea-queda-materializada
def test_materializar_deja_una_fila_con_su_carga_util_y_su_marca_de_tiempo():
    from tools.materialize_seasons import materializar

    filas = jornada(1740, "2026-08", dia_laborable(0, "2026-08"), 6)
    tabla = TablaFalsa()

    materializar(filas, ["2026-08"], tabla, ahora=AHORA)

    assert len(tabla.filas) == 1
    fila = tabla.filas[0]
    assert fila["temporada"] == "2026-08"
    assert fila["payload"]["dias"] == [1740]
    assert fila["updated_at"] == AHORA.isoformat()


# @scenarios recalcular-actualiza-en-lugar-de-duplicar
def test_materializar_dos_veces_actualiza_la_misma_fila():
    from tools.materialize_seasons import materializar

    filas = jornada(1750, "2026-08", dia_laborable(0, "2026-08"), 6)
    tabla = TablaFalsa()
    despues = AHORA + datetime.timedelta(hours=1)

    materializar(filas, ["2026-08"], tabla, ahora=AHORA)
    materializar(filas, ["2026-08"], tabla, ahora=despues)

    assert len(tabla.filas) == 1
    assert tabla.escrituras == 2
    assert tabla.filas[0]["updated_at"] == despues.isoformat()


# @scenarios instantanea-queda-materializada
def test_el_ensayo_cuenta_igual_pero_no_escribe():
    from tools.materialize_seasons import materializar

    filas = jornada(1760, "2026-08", dia_laborable(0, "2026-08"), 6)
    real, ensayo = TablaFalsa(), TablaFalsa()

    informe_real = materializar(filas, ["2026-08"], real, ahora=AHORA)
    informe_ensayo = materializar(filas, ["2026-08"], ensayo, ahora=AHORA, dry_run=True)

    assert informe_ensayo.materializadas == informe_real.materializadas == 1
    assert ensayo.escrituras == 0
    assert ensayo.filas == []
