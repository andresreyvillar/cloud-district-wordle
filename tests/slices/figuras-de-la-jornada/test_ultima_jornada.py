"""Escenarios de `figuras-de-la-jornada` — el lado del cálculo (Fase 2, TDD rojo).

Las cuadrículas son las mismas que verifica el slice del clasificador, y se comprueban antes de usarse.
"""

from __future__ import annotations

LORO = ".G.../.G..G/.GY../GGGGG"
GEOMETRICO = "..G../..G../GGGGG"
FLOR = "Y...Y/..Y../GGGGG"

HISTORICO = "2026-03-02"


def resultado(nombre, jornada, patron=None, fecha=HISTORICO, score=4):
    return {
        "slack_user_id": f"U_{nombre}",
        "player_name": nombre,
        "wordle_id": jornada,
        "score": score,
        "date": fecha,
        "pattern": patron,
    }


def test_los_fixtures_dibujan_lo_que_dicen_dibujar():
    from figures import figura

    assert (figura(LORO), figura(FLOR), figura(GEOMETRICO)) == ("loro", "flores", "geometrico")


# @scenarios la-figura-de-cada-participante
def test_se_publica_la_jornada_mas_reciente_con_la_figura_de_cada_uno():
    from album import album

    filas = [resultado("Ana", 1500, FLOR), resultado("Ana", 1501, LORO), resultado("Bea", 1501, GEOMETRICO)]

    ultima = album(filas, "0")["ultima_jornada"]

    assert ultima["jornada"] == 1501, "la más reciente, no la primera"
    assert ultima["figuras"] == {"U_Ana": "loro", "U_Bea": "geometrico"}


# @scenarios la-jornada-abierta-tambien-tiene-figuras
def test_una_jornada_que_todavia_no_cuenta_publica_sus_figuras():
    """A media mañana la jornada aún no llega a la muestra mínima. Sus dibujos existen igual."""
    from album import album
    from seasons import dias_de_temporada

    # Temporada numerada: un lunes con dos jugadores no alcanza la muestra mínima de cinco.
    filas = [
        resultado("Ana", 1700, FLOR, fecha="2026-09-07"),
        resultado("Bea", 1700, LORO, fecha="2026-09-07"),
    ]

    assert dias_de_temporada(filas, "2026-09") == [], "la jornada no cuenta todavía"

    ultima = album(filas, "2026-09")["ultima_jornada"]
    assert ultima["jornada"] == 1700
    # **La categoría se deriva del clasificador, no se escribe a mano.** Lo que este escenario comprueba es
    # que los dibujos del día aparecen aunque la jornada no cuente todavía, no qué etiqueta lleva cada uno:
    # el patrón de Bea cumple a la vez la regla del loro y la del geométrico, así que al versionar el orden
    # de reglas (`PRIMERA_JORNADA_DEL_ORDEN_NUEVO`) cambió de categoría y este test se puso rojo por un
    # motivo que no era el suyo.
    from figures import figura

    assert ultima["figuras"] == {
        "U_Ana": figura(FLOR, 1700),
        "U_Bea": figura(LORO, 1700),
    }
    assert set(ultima["figuras"]) == {"U_Ana", "U_Bea"}, "los dos jugadores del día están"


# @scenarios sin-cuadricula-no-hay-figura
def test_un_resultado_sin_cuadricula_no_aparece():
    from album import album

    filas = [resultado("Ana", 1501, FLOR), resultado("Bea", 1501, None)]

    figuras = album(filas, "0")["ultima_jornada"]["figuras"]

    assert "U_Ana" in figuras
    assert "U_Bea" not in figuras, "sin dibujo no se inventa categoría"


# @scenarios instantanea-sin-figuras-no-rompe
def test_una_temporada_sin_resultados_no_inventa_jornada():
    from album import album

    ultima = album([], "2026-09")["ultima_jornada"]

    assert ultima["jornada"] is None
    assert ultima["figuras"] == {}


# @scenarios la-figura-de-cada-participante
def test_la_clave_viaja_en_la_instantanea():
    from seasons import instantanea

    filas = [resultado("Ana", 1501, LORO)]

    assert instantanea(filas, "0")["album"]["ultima_jornada"]["figuras"] == {"U_Ana": "loro"}
