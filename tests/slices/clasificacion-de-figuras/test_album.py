"""Escenarios de `clasificacion-de-figuras` (Fase 2 — TDD rojo).

Fixtures a mano, con **patrones reales verificados contra el clasificador**: cada cuadrícula de este
fichero se comprueba en `test_los_fixtures_dibujan_lo_que_dicen_dibujar` antes de usarse. Un fixture que
creyera dibujar un loro y dibujara un abstracto haría pasar tests que no prueban nada.

Casi todos los escenarios usan la **temporada 0**, donde no hay filtros de jornada: así el fixture prueba
el álbum y no el modelo de temporada, que ya tiene sus propios tests. El único que necesita una temporada
numerada es el que comprueba justamente que el álbum hereda sus días.
"""

from __future__ import annotations

import pytest

MOTIVO = "TDD rojo — tools/album.py no existe todavía"

#: Cuadrículas de cada categoría, en el formato en que la ingesta las guarda (`G/Y/.` separado por barras).
LORO = ".G.../.G..G/.GY../GGGGG"
GEOMETRICO = "..G../..G../GGGGG"
FLOR = "Y...Y/..Y../GGGGG"
ABSTRACTO = "GG.GG/GGYGG/GG.GG/GGGGG"

#: Una jornada de la temporada 0 (anterior al límite de temporadas, así que no filtra ni finde ni muestra).
HISTORICO = "2026-03-02"


def resultado(
    jugador: str,
    jornada: int,
    patron: str | None,
    fecha: str = HISTORICO,
    nombre: str | None = None,
    score: int = 4,
) -> dict:
    return {
        "slack_user_id": jugador,
        "player_name": nombre or jugador,
        "wordle_id": jornada,
        "score": score,
        "date": fecha,
        "pattern": patron,
    }


def partidas(jugador: str, patrones: list[str | None], nombre: str | None = None) -> list[dict]:
    """Una partida por patrón, cada una en su jornada."""
    return [
        resultado(jugador, 1500 + indice, patron, nombre=nombre)
        for indice, patron in enumerate(patrones)
    ]


def fila_de(carga: dict, jugador: str) -> dict:
    return next(fila for fila in carga["jugadores"] if fila["jugador"] == jugador)


def test_los_fixtures_dibujan_lo_que_dicen_dibujar():
    """El fixture se verifica contra el clasificador, no contra la intención de quien lo escribió."""
    from figures import figura

    assert figura(LORO) == "loro"
    assert figura(GEOMETRICO) == "geometrico"
    assert figura(FLOR) == "flores"
    assert figura(ABSTRACTO) == "abstracto"


# @scenarios figura-de-cada-partida
def test_cada_partida_aporta_su_categoria_al_recuento_del_jugador():
    from album import album

    filas = partidas("U1", [LORO, FLOR, FLOR, GEOMETRICO, ABSTRACTO], nombre="Ana")

    carga = album(filas, "0")
    ana = fila_de(carga, "U1")

    assert ana["recuento"] == {"loro": 1, "flores": 2, "geometrico": 1, "abstracto": 1}
    assert ana["nombre"] == "Ana"
    assert carga["reparto"] == {"loro": 1, "flores": 2, "geometrico": 1, "abstracto": 1}


# @scenarios figura-de-cada-partida
def test_la_categoria_no_se_escribe_en_ninguna_fila():
    """Se deriva del patrón: las filas de entrada salen intactas y siguen sin columna de categoría."""
    from album import album

    filas = partidas("U1", [LORO, FLOR, FLOR, GEOMETRICO, ABSTRACTO])
    antes = [dict(fila) for fila in filas]

    album(filas, "0")

    assert filas == antes


# @scenarios sin-patron-no-cuenta
def test_una_partida_sin_patron_no_es_una_figura_ni_un_abstracto():
    from album import album

    filas = partidas("U1", [FLOR, FLOR, FLOR, FLOR, FLOR, None, None, None])

    carga = album(filas, "0")
    fila = fila_de(carga, "U1")

    assert fila["partidas"] == 5, "las tres sin patrón no entran en el denominador"
    assert fila["recuento"]["abstracto"] == 0, "sin dibujo no hay veredicto de abstracto"
    assert fila["tasa"] == 1.0


# @scenarios sin-patron-no-cuenta
def test_la_instantanea_declara_cuantas_partidas_se_quedaron_sin_clasificar():
    """Es la cobertura del álbum: sin ella, un ranking sobre el 24% de las partidas parece uno completo."""
    from album import album

    filas = partidas("U1", [FLOR, None, None, None])

    carga = album(filas, "0")

    assert carga["clasificadas"] == 1
    assert carga["sin_patron"] == 3


# @scenarios tasa-de-figuras-por-partida
def test_la_puntuacion_es_la_proporcion_de_partidas_con_figura():
    from album import album

    filas = partidas("U1", [FLOR, FLOR, FLOR, ABSTRACTO, ABSTRACTO])

    fila = fila_de(album(filas, "0"), "U1")

    assert fila["figuras"] == 3
    assert fila["partidas"] == 5
    assert fila["tasa"] == 0.6


# @scenarios tasa-de-figuras-por-partida
def test_jugar_mas_no_sube_la_tasa_por_si_solo():
    """El criterio descartado —recuento absoluto— coronaba a quien más juega. Este no puede."""
    from album import album

    constante = partidas("U1", [FLOR, ABSTRACTO], nombre="constante")
    prolifico = partidas("U2", [FLOR, ABSTRACTO] * 10, nombre="prolifico")

    carga = album(constante + prolifico, "0")

    assert fila_de(carga, "U1")["tasa"] == fila_de(carga, "U2")["tasa"]
    assert fila_de(carga, "U2")["partidas"] == 20


# @scenarios abstracto-se-registra-y-no-puntua
def test_un_abstracto_aparece_en_el_recuento_y_baja_la_tasa():
    from album import album

    solo_figuras = partidas("U1", [FLOR] * 4, nombre="limpia")
    con_abstracto = partidas("U2", [FLOR] * 4 + [ABSTRACTO], nombre="con ruido")

    carga = album(solo_figuras + con_abstracto, "0")
    ruidosa = fila_de(carga, "U2")

    assert ruidosa["recuento"]["abstracto"] == 1, "el abstracto se registra, no desaparece"
    assert ruidosa["tasa"] < fila_de(carga, "U1")["tasa"]


# @scenarios minimo-de-partidas-para-clasificar
def test_por_debajo_del_minimo_no_hay_puesto_aunque_la_tasa_sea_la_mejor():
    """Con mínimo 3, la temporada 0 la ganaba alguien con un 100% de tres partidas.

    Las cantidades van **literales, 4 y 5**, y no derivadas de la constante: un fixture que se ajuste solo
    al umbral deja de medir cuál es el umbral, y el número es justo lo que aquí se decidió.
    """
    from album import album

    perfecta_pero_corta = partidas("U1", [FLOR] * 4, nombre="Sandra")
    regular_pero_larga = partidas("U2", [FLOR] * 4 + [ABSTRACTO], nombre="Juan")

    carga = album(perfecta_pero_corta + regular_pero_larga, "0")
    sandra, juan = fila_de(carga, "U1"), fila_de(carga, "U2")

    assert sandra["tasa"] > juan["tasa"]
    assert sandra["clasificado"] is False and sandra["posicion"] is None
    assert juan["clasificado"] is True and juan["posicion"] == 1
    assert carga["jugadores"][0]["jugador"] == "U2", "quien no clasifica no encabeza"


# @scenarios minimo-de-partidas-para-clasificar
def test_quien_no_llega_al_minimo_sigue_apareciendo():
    """Verse en el sitio de uno informa más que no verse. Es lo mismo que hace la tabla de puntuación."""
    from album import album

    carga = album(partidas("U1", [FLOR]), "0")

    assert [fila["jugador"] for fila in carga["jugadores"]] == ["U1"]
    assert carga["jugadores"][0]["clasificado"] is False


# @scenarios orden-determinista-del-album
def test_a_igualdad_de_tasa_va_delante_quien_aporto_mas_figuras():
    from album import album

    pocas = partidas("U1", [FLOR] * 5, nombre="zeta")
    muchas = partidas("U2", [FLOR] * 9, nombre="alfa")

    carga = album(pocas + muchas, "0")

    assert [fila["jugador"] for fila in carga["jugadores"]] == ["U2", "U1"]
    assert carga["jugadores"][0]["figuras"] == 9


# @scenarios orden-determinista-del-album
def test_el_empate_total_se_rompe_por_nombre_y_no_por_el_orden_de_entrada():
    from album import album

    zeta = partidas("U1", [FLOR] * 5, nombre="Zeta")
    alfa = partidas("U2", [FLOR] * 5, nombre="Alfa")

    de_una_forma = [fila["nombre"] for fila in album(zeta + alfa, "0")["jugadores"]]
    de_la_otra = [fila["nombre"] for fila in album(alfa + zeta, "0")["jugadores"]]

    assert de_una_forma == de_la_otra == ["Alfa", "Zeta"]


# @scenarios el-album-hereda-los-dias-de-la-temporada
def test_un_patron_de_un_dia_que_no_cuenta_no_entra_en_el_album():
    """Sábado con cinco jugadores: lo único que lo excluye es el fin de semana, no la falta de muestra."""
    from album import album

    sabado = [
        resultado(f"U{n}", 1898, LORO, fecha="2026-09-05", nombre=f"j{n}") for n in range(1, 6)
    ]
    lunes = [
        resultado(f"U{n}", 1900, FLOR, fecha="2026-09-07", nombre=f"j{n}") for n in range(1, 6)
    ]

    carga = album(sabado + lunes, "2026-09")

    assert carga["reparto"]["loro"] == 0, "el patrón del sábado no entra"
    assert carga["reparto"]["flores"] == 5
    assert fila_de(carga, "U1")["partidas"] == 1


# @scenarios temporada-sin-patrones-no-inventa-ranking
def test_una_temporada_sin_ningun_patron_no_produce_campeon_de_belleza():
    """El estado real de agosto de 2026: 61 de 80 filas sin patrón porque el cron aún no lo guardaba."""
    from album import album

    carga = album(partidas("U1", [None] * 10), "0")

    assert carga["jugadores"] == []
    assert carga["clasificadas"] == 0
    assert carga["sin_patron"] == 10


# @scenarios temporada-sin-patrones-no-inventa-ranking
def test_una_temporada_sin_resultados_devuelve_un_album_vacio_y_no_revienta():
    from album import album

    carga = album([], "2026-09")

    assert carga["jugadores"] == []
    assert carga["clasificadas"] == 0


# @scenarios figura-de-cada-partida
def test_el_album_viaja_en_la_instantanea_con_el_vocabulario_de_emojis():
    """La web pinta el emoji que dice Python: un mapa duplicado en JavaScript sería una segunda verdad."""
    from seasons import instantanea

    filas = partidas("U1", [LORO, FLOR, FLOR, GEOMETRICO, ABSTRACTO], nombre="Ana")

    carga = instantanea(filas, "0")

    assert carga["album"]["jugadores"][0]["recuento"]["loro"] == 1
    assert carga["album"]["vocabulario"]["loro"] == "🦜"
