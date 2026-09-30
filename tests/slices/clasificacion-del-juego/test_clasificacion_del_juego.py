"""La clasificación del SuperWordleBros en la temporada, de `clasificacion-del-juego` (Fase 2 — TDD rojo).

Pack: `feat-juego-en-la-temporada`.

Todo entra por parámetro —resultados, niveles y marcas—, así que aquí no hay red. Los jugadores y las fechas
son sintéticos: el repositorio es público.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))


SEPTIEMBRE = "2026-09"
OCTUBRE = "2026-10"

#: Jornadas sintéticas y sus fechas. Lunes 28 y miércoles 30 de septiembre cuentan (laborables con cinco
#: jugadores); el sábado 26 no (fin de semana) y el martes 29 tampoco (solo cuatro jugadores); el jueves 1 de
#: octubre cuenta en octubre.
LUNES, SABADO, MARTES_CORTO, ULTIMO_DE_MES, PRIMERO_DE_OCTUBRE = 100, 98, 101, 102, 103
FECHAS = {
    SABADO: "2026-09-26",
    LUNES: "2026-09-28",
    MARTES_CORTO: "2026-09-29",
    ULTIMO_DE_MES: "2026-09-30",
    PRIMERO_DE_OCTUBRE: "2026-10-01",
}
JUGADORES = [f"J{i}" for i in range(9)]


def fila(jugador: str, jornada: int, nombre: str | None = None) -> dict:
    return {
        "slack_user_id": jugador,
        "player_name": nombre or f"Nombre {jugador}",
        "wordle_id": jornada,
        "score": 3,
        "date": FECHAS[jornada],
        "pattern": "🟩🟩🟩🟩🟩",
    }


def resultados() -> list[dict]:
    filas = []
    for jornada in (LUNES, SABADO, ULTIMO_DE_MES, PRIMERO_DE_OCTUBRE):
        filas += [fila(j, jornada) for j in JUGADORES[:5]]
    filas += [fila(j, MARTES_CORTO) for j in JUGADORES[:4]]
    return filas


NIVELES = [{"jornada": j, "fecha": f} for j, f in FECHAS.items()]


def marca(jornada: int, jugador: str, segundos: float, estrellas: int = 1) -> dict:
    return {"jornada": jornada, "jugador": jugador, "segundos": segundos, "estrellas": estrellas}


def puntos(tabla: dict) -> dict[str, int]:
    return {f["jugador"]: f["puntos"] for f in tabla["clasificacion"]}


def calcular(marcas, temporada=SEPTIEMBRE, filas=None, niveles=None):
    from juego import clasificacion_del_juego

    return clasificacion_del_juego(filas or resultados(), niveles or NIVELES, marcas, temporada)


# @scenarios puntua-cada-nivel-por-puesto
def test_cada_nivel_reparte_10_8_6_5_4_3_2_y_1_del_octavo_en_adelante():
    marcas = [marca(LUNES, j, 30 + i) for i, j in enumerate(JUGADORES)]

    assert [puntos(calcular(marcas))[j] for j in JUGADORES] == [10, 8, 6, 5, 4, 3, 2, 1, 1]


# @scenarios las-estrellas-pesan-mas-que-el-tiempo
def test_mas_estrellas_van_delante_aunque_sean_mas_lentas():
    marcas = [marca(LUNES, "J0", 12.03, estrellas=9), marca(LUNES, "J1", 13, estrellas=13)]

    assert puntos(calcular(marcas)) == {"J1": 10, "J0": 8}


# @scenarios los-empates-en-un-nivel-comparten-puntos
def test_mismo_tiempo_con_distintas_estrellas_no_es_empate():
    marcas = [marca(LUNES, "J0", 30, estrellas=2), marca(LUNES, "J1", 30, estrellas=3)]

    assert puntos(calcular(marcas)) == {"J1": 10, "J0": 8}


# @scenarios los-empates-en-un-nivel-comparten-puntos
def test_un_empate_en_centesimas_comparte_puesto_y_puntos():
    marcas = [marca(LUNES, "J0", 30.001), marca(LUNES, "J1", 30.004), marca(LUNES, "J2", 31)]

    assert puntos(calcular(marcas)) == {"J0": 10, "J1": 10, "J2": 6}


# @scenarios el-mes-suma-los-puntos
def test_el_mes_suma_los_puntos_y_cuenta_niveles_y_victorias():
    marcas = [
        marca(LUNES, "J0", 30), marca(LUNES, "J1", 31),
        marca(ULTIMO_DE_MES, "J1", 25), marca(ULTIMO_DE_MES, "J0", 26), marca(ULTIMO_DE_MES, "J2", 40),
    ]

    tabla = calcular(marcas)["clasificacion"]

    assert [(f["jugador"], f["puntos"], f["niveles"], f["victorias"]) for f in tabla] == [
        ("J0", 18, 2, 1), ("J1", 18, 2, 1), ("J2", 6, 1, 0),
    ]
    assert calcular(marcas)["niveles"] == 2


# @scenarios los-empates-del-mes-comparten-puesto
def test_a_igualdad_de_puntos_se_comparte_puesto_y_ordena_la_victoria():
    # J3 gana los dos niveles (20); J0 hace 8 + 6 y J1 6 + 8: 14 cada uno, sin victorias.
    marcas = [
        marca(LUNES, "J3", 20), marca(LUNES, "J0", 30), marca(LUNES, "J1", 31),
        marca(ULTIMO_DE_MES, "J3", 20), marca(ULTIMO_DE_MES, "J1", 25), marca(ULTIMO_DE_MES, "J0", 26),
    ]

    tabla = calcular(marcas)["clasificacion"]

    assert [(f["posicion"], f["jugador"], f["puntos"]) for f in tabla] == [
        (1, "J3", 20), (2, "J0", 14), (2, "J1", 14),
    ]


# @scenarios los-empates-del-mes-comparten-puesto
def test_el_empate_se_lista_con_el_de_mas_victorias_delante():
    # J1 gana un nivel y es tercero en otro (10 + 6 = 16); J0 es segundo en los dos (8 + 8 = 16). El otro nivel
    # lo gana J3, que así no empata con nadie (10).
    marcas = [
        marca(LUNES, "J1", 20), marca(LUNES, "J0", 30), marca(LUNES, "J2", 40),
        marca(ULTIMO_DE_MES, "J3", 20), marca(ULTIMO_DE_MES, "J0", 30), marca(ULTIMO_DE_MES, "J1", 40),
    ]

    tabla = calcular(marcas)["clasificacion"]
    empatados = [f for f in tabla if f["puntos"] == 16]

    assert [f["jugador"] for f in empatados] == ["J1", "J0"]
    assert {f["posicion"] for f in empatados} == {empatados[0]["posicion"]}


# @scenarios solo-puntuan-los-niveles-de-dias-de-temporada
def test_ni_el_sabado_ni_un_laborable_con_cuatro_jugadores_dan_puntos():
    marcas = [marca(SABADO, "J0", 30), marca(MARTES_CORTO, "J1", 30)]
    solo_esos = [n for n in NIVELES if n["jornada"] in (SABADO, MARTES_CORTO)]

    tabla = calcular(marcas, niveles=solo_esos)

    assert tabla["clasificacion"] == []
    assert tabla["niveles"] == 0


# @scenarios el-nivel-cuenta-en-el-mes-de-su-jornada
def test_el_nivel_del_ultimo_dia_cuenta_en_su_mes():
    marcas = [marca(ULTIMO_DE_MES, "J0", 30)]

    assert puntos(calcular(marcas, SEPTIEMBRE)) == {"J0": 10}
    assert calcular(marcas, OCTUBRE)["clasificacion"] == []


# @scenarios sin-marcas-la-clasificacion-esta-vacia
def test_sin_marcas_la_clave_juego_esta_vacia_y_el_resto_no_cambia():
    from seasons import instantanea

    sin_juego = instantanea(resultados(), SEPTIEMBRE, "abc")
    con_juego_vacio = instantanea(resultados(), SEPTIEMBRE, "abc", niveles=NIVELES, marcas=[])

    assert con_juego_vacio["juego"]["clasificacion"] == []
    assert {k: v for k, v in con_juego_vacio.items() if k != "juego"} == {
        k: v for k, v in sin_juego.items() if k != "juego"
    }


# @scenarios sin-marcas-la-clasificacion-esta-vacia
def test_la_instantanea_trae_la_clasificacion_del_juego():
    from seasons import instantanea

    carga = instantanea(resultados(), SEPTIEMBRE, "abc", niveles=NIVELES, marcas=[marca(LUNES, "J0", 30)])

    assert carga["juego"]["clasificacion"][0]["jugador"] == "J0"
    assert carga["juego"]["escala"] == [10, 8, 6, 5, 4, 3, 2, 1]


# @scenarios los-nombres-son-los-del-grupo
def test_el_nombre_es_el_de_la_fila_mas_reciente_y_si_no_hay_filas_el_identificador():
    # Una jornada posterior a todas las del fixture, con el nombre cambiado.
    renombrado = {**fila("J0", PRIMERO_DE_OCTUBRE, "Nombre nuevo"), "wordle_id": 104, "date": "2026-10-02"}
    filas = resultados() + [renombrado]
    marcas = [marca(LUNES, "J0", 30), marca(LUNES, "U_SIN_FILAS", 31)]

    nombres = {f["jugador"]: f["nombre"] for f in calcular(marcas, filas=filas)["clasificacion"]}

    assert nombres == {"J0": "Nombre nuevo", "U_SIN_FILAS": "U_SIN_FILAS"}


# @scenarios la-clasificacion-es-determinista
def test_el_orden_de_entrada_no_cambia_la_clasificacion():
    marcas = [marca(j, jug, 20 + i) for i, (j, jug) in enumerate(
        [(LUNES, "J0"), (LUNES, "J1"), (ULTIMO_DE_MES, "J2"), (ULTIMO_DE_MES, "J0"), (LUNES, "J2")]
    )]
    barajadas, filas, niveles = marcas[:], resultados(), NIVELES[:]
    random.Random(7).shuffle(barajadas)
    random.Random(7).shuffle(filas)
    random.Random(7).shuffle(niveles)

    assert calcular(marcas) == calcular(barajadas, filas=filas, niveles=niveles)


class _Consulta:
    """Un cliente de supabase-py falso: devuelve páginas y apunta cualquier intento de escribir."""

    def __init__(self, tablas: dict[str, list[dict]], pagina: int, registro: list):
        self.tablas, self.pagina, self.registro = tablas, pagina, registro

    def table(self, nombre):
        self.tabla, self.rango = nombre, (0, 0)
        return self

    def select(self, _columnas):
        return self

    def order(self, _columna):
        return self

    def range(self, desde, hasta):
        self.rango = (desde, hasta)
        self.registro.append(("range", self.tabla, desde))
        return self

    def execute(self):
        desde, hasta = self.rango
        return type("R", (), {"data": self.tablas[self.tabla][desde:hasta + 1]})

    def __getattr__(self, nombre):  # insert, update, upsert, delete…
        self.registro.append(("escritura", nombre))
        raise AssertionError(f"la materialización no escribe en las tablas del juego ({nombre})")


# @scenarios la-materializacion-lee-niveles-y-marcas
def test_la_materializacion_lee_niveles_y_marcas_paginando_y_sin_escribir(monkeypatch):
    import materialize_seasons

    monkeypatch.setattr(materialize_seasons, "PAGINA", 2)
    marcas = [marca(LUNES, f"J{i}", 30 + i) for i in range(5)]
    registro: list = []
    cliente = _Consulta({"game_levels": NIVELES, "game_times": marcas}, 2, registro)

    niveles_leidos, marcas_leidas = materialize_seasons.leer_juego(cliente)

    assert niveles_leidos == NIVELES
    assert marcas_leidas == marcas
    assert ("range", "game_times", 4) in registro, "pagina las marcas"
    assert not [r for r in registro if r[0] == "escritura"]
