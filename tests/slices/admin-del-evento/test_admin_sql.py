"""Activar, terminar, liberar nombres y puntuar el evento, de `admin-del-evento`, contra un Postgres **local**.

Cambio: `feat-palabras-del-evento`. **No se toca producción**. Participantes, grupos, palabras y PIN inventados.

Puntos: en cada palabra, la marca es el tiempo más 30 s por intento (menos es mejor); quien la resuelve se lleva 1
punto más uno por cada resolvedor con peor marca, y quien no, 0. El grupo puntúa la media de su lista entera.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.evento_sql import (
    EVENTO, PIN, SEMILLA, activado, elegir, empezar, fijar, jugador, panel, probar, reiniciar, rpc, terminado, token,
    valor,
)
from tests.postgres_local import MIGRACIONES, postgres_con_migraciones, sin_postgres

pytestmark = sin_postgres


@pytest.fixture(scope="module")
def db():
    arranque = postgres_con_migraciones()
    sql = next(arranque)
    resultado = sql(SEMILLA)
    assert resultado.returncode == 0, resultado.stderr
    yield sql
    arranque.close()


@pytest.fixture(autouse=True)
def limpio(db):
    reiniciar(db)


def campo(db, columna):
    return valor(db, f"select coalesce({columna}::text, '') from public.event_editions where id = '{EVENTO}'")


def puntos(db):
    datos = panel(db)
    return {j["nombre"]: j["puntos"] for j in datos["jugadores"]}, datos


# ── El PIN ───────────────────────────────────────────────────────────────────────────────────────────────

# @scenarios se-activa-con-el-pin
def test_el_pin_correcto_activa_el_evento_una_sola_vez(db):
    ok, datos = rpc(db, "empezar_evento", EVENTO, PIN)

    assert ok and "error" not in datos, datos
    assert valor(db, "select abs(extract(epoch from now() - empieza_en)) < 5 from public.event_editions") == "t"
    valor(db, "update public.event_editions set empieza_en = empieza_en - interval '1 hour'")
    antes = campo(db, "empieza_en")
    assert rpc(db, "empezar_evento", EVENTO, PIN)[0]
    assert campo(db, "empieza_en") == antes, "activar otra vez no lo mueve"


# @scenarios un-pin-incorrecto-no-hace-nada
@pytest.mark.parametrize("pin", ["", "0000", "1234 ", None])
def test_un_pin_incorrecto_no_activa_termina_libera_ni_ensena_nada(db, pin):
    assert rpc(db, "empezar_evento", EVENTO, pin)[1] == {"error": "PIN incorrecto"}
    assert campo(db, "empieza_en") == ""

    activado(db)
    tk = jugador(db, "Ana")
    assert rpc(db, "terminar_evento", EVENTO, pin)[1] == {"error": "PIN incorrecto"}
    assert rpc(db, "liberar_nombre", EVENTO, pin, "Ana")[1] == {"error": "PIN incorrecto"}
    assert rpc(db, "panel_del_evento", EVENTO, pin)[1] == {"error": "PIN incorrecto"}
    assert campo(db, "terminado_en") == ""
    assert valor(db, "select token::text from public.event_roster where nombre = 'Ana'") == tk


# @scenarios cinco-fallos-bloquean-el-pin-un-minuto
def test_cinco_fallos_seguidos_bloquean_tambien_el_pin_bueno_durante_un_minuto(db):
    for _ in range(5):
        rpc(db, "panel_del_evento", EVENTO, "0000")

    ok, datos = rpc(db, "empezar_evento", EVENTO, PIN)

    assert ok and "espera unos minutos" in datos["error"]
    assert campo(db, "empieza_en") == ""
    assert valor(db, "select pin_bloqueado_hasta between now() + interval '50 seconds' and now() + interval '61 seconds' "
                     "from public.event_editions") == "t"
    valor(db, "update public.event_editions set pin_bloqueado_hasta = now() - interval '1 second'")
    assert "error" not in rpc(db, "empezar_evento", EVENTO, PIN)[1], "pasado el minuto, el bueno vuelve a valer"


# @scenarios cinco-fallos-bloquean-el-pin-un-minuto
def test_cada_bloqueo_dura_el_doble_hasta_una_hora(db):
    esperas = []
    for _ in range(8):
        for _ in range(5):
            rpc(db, "panel_del_evento", EVENTO, "0000")
        esperas.append(round(float(valor(db, "select extract(epoch from pin_bloqueado_hasta - now()) / 60 "
                                             "from public.event_editions"))))
        valor(db, "update public.event_editions set pin_bloqueado_hasta = now() - interval '1 second'")

    assert esperas == [1, 2, 4, 8, 16, 32, 60, 60]
    assert "error" not in panel(db), "el bueno vuelve a valer y pone la cuenta a cero"
    assert campo(db, "pin_fallos") == "0"


# @scenarios cinco-fallos-bloquean-el-pin-un-minuto
def test_el_pin_bueno_reinicia_la_cuenta_de_fallos(db):
    for _ in range(4):
        rpc(db, "panel_del_evento", EVENTO, "0000")
    assert "error" not in panel(db)

    rpc(db, "panel_del_evento", EVENTO, "0000")

    assert "error" not in panel(db), "cuatro fallos, un acierto y un fallo no bloquean"


# @scenarios se-termina-con-el-pin
def test_el_pin_correcto_termina_el_evento_una_sola_vez_y_sin_activar_no_se_termina(db):
    assert "error" in rpc(db, "terminar_evento", EVENTO, PIN)[1]
    assert campo(db, "terminado_en") == ""
    activado(db)

    ok, datos = rpc(db, "terminar_evento", EVENTO, PIN)

    assert ok and "error" not in datos, datos
    valor(db, "update public.event_editions set terminado_en = terminado_en - interval '1 minute'")
    antes = campo(db, "terminado_en")
    assert rpc(db, "terminar_evento", EVENTO, PIN)[0]
    assert campo(db, "terminado_en") == antes
    assert panel(db)["terminado"] is True


# ── Durante el evento ────────────────────────────────────────────────────────────────────────────────────

def a_medias(db, nombre: str, orden: int, segundos: int) -> None:
    """Una palabra empezada hace `segundos` y sin terminar."""
    valor(db, "insert into public.event_rounds (jugador, orden, empezada_en) select id, "
              f"{orden}, now() - make_interval(secs => {segundos}) from public.event_roster "
              f"where evento = '{EVENTO}' and nombre = '{nombre}'")


# @scenarios el-admin-sigue-a-cada-participante
def test_durante_el_evento_el_panel_sigue_a_cada_participante_sin_soluciones(db):
    activado(db)
    for nombre in ("Ana", "Bea", "Cris"):
        jugador(db, nombre)
    fijar(db, "Ana", 1, 30, 2)
    fijar(db, "Ana", 2, 45, 6, resuelta=False)
    a_medias(db, "Bea", 3, 90)

    datos = panel(db)

    contadores = [(p["jugando"], p["resueltas"], p["falladas"]) for p in datos["palabras"]]
    assert contadores == [(0, 1, 0), (0, 0, 1), (1, 0, 0)]
    assert (datos["participantes"], datos["elegidos"]) == (6, 3)
    assert all("palabra" not in p for p in datos["palabras"]), "las soluciones, al terminar"
    filas = {j["nombre"]: j for j in datos["jugadores"]}
    ana, bea, cris, eva = filas["Ana"], filas["Bea"], filas["Cris"], filas["Eva"]
    assert (ana["elegido"], ana["empezadas"], ana["terminadas"], ana["resueltas"], ana["tiempo_ms"]) == (True, 2, 2, 1, 75_000)
    assert ana["jugando_desde"] is None
    assert (bea["empezadas"], bea["terminadas"], bea["tiempo_ms"]) == (1, 0, 0)
    assert valor(db, f"select abs(extract(epoch from now() - '{bea['jugando_desde']}'::timestamptz) - 90) < 5") == "t"
    assert (cris["elegido"], cris["empezadas"]) == (True, 0)
    assert eva["elegido"] is False


# @scenarios el-ranking-se-ve-en-directo
def test_durante_el_evento_el_ranking_cuenta_lo_terminado_hasta_ese_momento(db):
    activado(db)
    fijar(db, "Ana", 1, 30, 2)    # 30 + 60 = 90
    fijar(db, "Bea", 1, 50, 2)    # 50 + 60 = 110
    a_medias(db, "Cris", 1, 10)   # a medias: cero

    datos = panel(db)

    filas = {j["nombre"]: j for j in datos["jugadores"]}
    assert (filas["Ana"]["puesto"], filas["Ana"]["puntos"]) == (1, 15)
    assert (filas["Bea"]["puesto"], filas["Bea"]["puntos"]) == (2, 10)
    assert filas["Cris"]["puntos"] == 0
    grupos = {g["grupo"]: g for g in datos["grupos"]}
    assert (grupos["Rojo"]["puesto"], float(grupos["Rojo"]["puntos_totales"])) == (1, 25)

    fijar(db, "Dani", 1, 10, 1)   # 10 + 30 = 40: la mejor marca, y el extra se reparte de nuevo
    filas = {j["nombre"]: j for j in panel(db)["jugadores"]}
    assert (filas["Dani"]["puntos"], filas["Ana"]["puntos"], filas["Bea"]["puntos"]) == (15, 12.5, 10)


# @scenarios se-libera-un-nombre
def test_liberar_un_nombre_lo_deja_libre_y_borra_lo_jugado(db):
    activado(db)
    tk = jugador(db, "Ana")
    assert empezar(db, tk, 1)[0]

    ok, datos = rpc(db, "liberar_nombre", EVENTO, PIN, "ana")

    assert ok and datos == {"nombre": "Ana"}
    assert valor(db, "select count(*) from public.event_rounds") == "0"
    assert elegir(db, "Ana", token())[0], "otro móvil ya puede elegirlo"
    assert not rpc(db, "mi_juego", EVENTO, tk)[0], "el móvil que lo tenía se queda sin nombre"
    assert "error" in rpc(db, "liberar_nombre", EVENTO, PIN, "Zoe")[1]


# @scenarios se-libera-un-nombre
def test_con_el_evento_terminado_no_se_libera_ningun_nombre(db):
    activado(db)
    tk = jugador(db, "Ana")
    fijar(db, "Ana", 1, 30, 2)
    terminado(db)

    ok, datos = rpc(db, "liberar_nombre", EVENTO, PIN, "Ana")

    assert ok and "terminado" in datos["error"]
    assert valor(db, "select token::text from public.event_roster where nombre = 'Ana'") == tk
    assert valor(db, "select count(*) from public.event_rounds") == "1"


# ── Los puntos ───────────────────────────────────────────────────────────────────────────────────────────

# @scenarios cada-palabra-puntua-por-tiempo-e-intentos
def test_la_marca_es_el_tiempo_mas_treinta_segundos_por_intento(db):
    fijar(db, "Ana", 1, 30, 4)    # 30 + 120 = 150
    fijar(db, "Bea", 1, 70, 3)    # 70 +  90 = 160
    fijar(db, "Cris", 1, 50, 3)   # 50 +  90 = 140
    fijar(db, "Dani", 1, 10, 6, resuelta=False)
    terminado(db)

    tabla, datos = puntos(db)

    # 10 por acertar y hasta 5 por rapidez: el mejor (140) 15, el del medio (150) 12,5, el peor (160) 10.
    assert (tabla["Cris"], tabla["Ana"], tabla["Bea"], tabla["Dani"], tabla["Eva"]) == (15, 12.5, 10, 0, 0)
    assert [j["nombre"] for j in datos["jugadores"][:3]] == ["Cris", "Ana", "Bea"]
    ana = next(j for j in datos["jugadores"] if j["nombre"] == "Ana")
    assert ana["palabras"] == [{"orden": 1, "resuelta": True, "intentos": 4, "tiempo_ms": 30_000,
                                "marca_ms": 150_000, "puntos": 12.5}]


# @scenarios cada-palabra-puntua-por-tiempo-e-intentos
def test_las_palabras_puntuan_por_separado_y_se_suman(db):
    fijar(db, "Ana", 1, 30, 3)
    fijar(db, "Bea", 1, 40, 3)
    fijar(db, "Ana", 2, 90, 4)
    fijar(db, "Bea", 2, 20, 2)
    fijar(db, "Cris", 2, 20, 6)
    terminado(db)

    tabla, _ = puntos(db)

    # Palabra 1: Ana 120, Bea 130. Palabra 2: Bea 80, Cris 200, Ana 210.
    assert (tabla["Ana"], tabla["Bea"], tabla["Cris"]) == (15 + 10, 10 + 15, 0 + 12.5)


# @scenarios cada-palabra-puntua-por-tiempo-e-intentos
def test_una_palabra_a_medias_al_terminar_no_puntua(db):
    activado(db)
    tk = jugador(db, "Ana")
    assert empezar(db, tk, 1)[0]
    fijar(db, "Bea", 1, 300, 6)
    terminado(db)

    tabla, _ = puntos(db)

    assert (tabla["Ana"], tabla["Bea"]) == (0, 15), "a medias no puntúa; quien la resuelve solo se lleva el extra entero"


# @scenarios el-empate-comparte-puntos
def test_la_misma_marca_da_los_mismos_puntos(db):
    fijar(db, "Ana", 1, 60, 3)    # 150
    fijar(db, "Bea", 1, 90, 2)    # 150
    fijar(db, "Cris", 1, 151, 0)  # 151 (sin intentos no pasa en el juego: solo fija la marca)
    terminado(db)

    tabla, datos = puntos(db)

    assert (tabla["Ana"], tabla["Bea"], tabla["Cris"]) == (15, 15, 10), "empatar en cabeza no quita extra"
    assert [j["puesto"] for j in datos["jugadores"][:3]] == [1, 1, 3]


# @scenarios los-segundos-por-intento-se-cambian-sin-codigo
def test_con_otros_segundos_por_intento_cambia_quien_gana(db):
    fijar(db, "Ana", 1, 30, 4)
    fijar(db, "Bea", 1, 70, 3)
    valor(db, "update public.event_editions set segundos_por_intento = 45")
    terminado(db)

    tabla, datos = puntos(db)

    assert (tabla["Bea"], tabla["Ana"]) == (15, 10), "con 45 s, 70 + 135 = 205 gana a 30 + 180 = 210"
    assert datos["segundos_por_intento"] == 45


# @scenarios los-segundos-por-intento-se-cambian-sin-codigo
def test_con_otros_puntos_por_acierto_y_por_rapidez_cambian_los_puntos(db):
    fijar(db, "Ana", 1, 30, 1)
    fijar(db, "Bea", 1, 50, 1)
    fijar(db, "Cris", 1, 70, 1)
    valor(db, "update public.event_editions set puntos_por_acierto = 20, puntos_por_rapidez = 8")
    try:
        terminado(db)
        tabla, _ = puntos(db)
    finally:
        valor(db, "update public.event_editions set puntos_por_acierto = 10, puntos_por_rapidez = 5")

    assert (tabla["Ana"], tabla["Bea"], tabla["Cris"]) == (28, 24, 20)


# @scenarios acertar-pesa-mas-que-la-rapidez
def test_acertar_una_palabra_mas_pesa_mas_que_ser_el_mas_rapido(db):
    fijar(db, "Ana", 1, 300, 6)   # la más lenta en las dos
    fijar(db, "Ana", 2, 300, 6)
    fijar(db, "Bea", 1, 10, 1)    # la más rápida, pero solo una
    fijar(db, "Cris", 2, 10, 1)
    terminado(db)

    tabla, datos = puntos(db)

    assert (tabla["Ana"], tabla["Bea"], tabla["Cris"]) == (20, 15, 15)
    assert datos["jugadores"][0]["nombre"] == "Ana"


# @scenarios la-puntuacion-del-grupo-es-la-media-de-su-lista
def test_el_grupo_puntua_la_media_de_toda_su_lista(db):
    fijar(db, "Ana", 1, 10, 1)    # Rojo: 15 + 0 (Bea no juega) = 15 → 7,5
    fijar(db, "Cris", 1, 20, 1)   # Azul: 12,5 + 10 = 22,5 → 11,25
    fijar(db, "Dani", 1, 30, 1)
    terminado(db)

    _, datos = puntos(db)

    grupos = {g["grupo"]: g for g in datos["grupos"]}
    assert (float(grupos["Rojo"]["puntos_totales"]), float(grupos["Rojo"]["puntos"])) == (15, 7.5)
    assert (float(grupos["Azul"]["puntos_totales"]), float(grupos["Azul"]["puntos"])) == (22.5, 11.25)
    assert (grupos["Rojo"]["miembros"], grupos["Rojo"]["jugaron"]) == (2, 1)
    assert float(grupos["Verde"]["puntos"]) == 0
    assert [g["grupo"] for g in datos["grupos"]] == ["Azul", "Rojo", "Verde"]


# @scenarios la-puntuacion-del-grupo-es-la-media-de-su-lista
def test_el_puesto_del_grupo_sale_de_la_media_sin_redondear(db):
    valor(db, f"insert into public.event_roster (evento, nombre, grupo) "
              f"select '{EVENTO}', 'P' || i, 'Veinte' from generate_series(1, 300) i union all "
              f"select '{EVENTO}', 'Q' || i, 'Veintiuno' from generate_series(1, 301) i")
    try:
        fijar(db, "P1", 1, 60, 3)
        fijar(db, "Q1", 1, 60, 3)   # la misma marca: 15 cada uno; 15/300 = 0,05 y 15/301 = 0,0498 (0,05 redondeado)
        terminado(db)

        grupos = {g["grupo"]: g for g in panel(db)["grupos"]}

        assert float(grupos["Veinte"]["puntos"]) == float(grupos["Veintiuno"]["puntos"]) == 0.05
        assert (grupos["Veinte"]["puesto"], grupos["Veintiuno"]["puesto"]) == (1, 2)
    finally:
        valor(db, f"delete from public.event_roster where evento = '{EVENTO}' and grupo in ('Veinte', 'Veintiuno')")


# @scenarios las-soluciones-solo-se-ven-al-terminar
def test_los_puntos_y_las_soluciones_salen_en_el_panel_al_terminar(db):
    fijar(db, "Ana", 1, 10, 1)
    activado(db)
    assert all("palabra" not in p for p in panel(db)["palabras"]), "en marcha, sin soluciones"

    terminado(db)
    datos = panel(db)

    assert {j["nombre"] for j in datos["jugadores"]} == {"Ana", "Bea", "Cris", "Dani", "Íñigo Pérez", "Eva"}
    assert [p["palabra"] for p in datos["palabras"]] == ["casas", "perro", "lapiz"]
    assert {j["grupo"] for j in datos["jugadores"]} == {"Rojo", "Azul", "Verde"}


# ── El repositorio ───────────────────────────────────────────────────────────────────────────────────────

# @scenarios el-pin-no-esta-en-el-repositorio
def test_las_migraciones_no_traen_palabras_participantes_ni_huella_de_pin():
    for migracion in MIGRACIONES.glob("*.sql"):
        texto = migracion.read_text(encoding="utf-8")
        sin_comentarios = re.sub(r"--[^\n]*", "", texto)
        assert not re.search(r"insert\s+into\s+public\.event_(editions|phrases|targets|roster)\b", sin_comentarios,
                             re.I), migracion.name
        assert not re.search(r"\b[0-9a-f]{64}\b", texto), migracion.name

    semilla = Path(MIGRACIONES).parent / "seeds" / "evento_de_prueba.sql"
    assert "'prueba'" in semilla.read_text(encoding="utf-8"), "en el repositorio solo está el evento de prueba"


# ── El dashboard sin PIN: horario, tablero público, F1, palabras y echar ─────────────────────────────────

def programado(db, desde: str, hasta: str) -> None:
    """El evento programado de `now() + desde` a `now() + hasta` (intervalos de Postgres)."""
    valor(db, f"update public.event_editions set empieza_en = now() + interval '{desde}', "
              f"terminado_en = now() + interval '{hasta}' where id = '{EVENTO}'")


def tablero(db):
    ok, datos = rpc(db, "tablero_del_evento", EVENTO)
    assert ok, datos
    return datos


# @scenarios el-evento-empieza-y-termina-a-su-hora
def test_el_evento_programado_no_empieza_antes_de_su_hora_y_termina_a_la_suya(db):
    programado(db, "1 hour", "7 hours")
    datos = rpc(db, "estado_del_juego", EVENTO)[1]
    assert datos["activo"] is False
    assert set(datos) == {"ahora", "activo", "terminado"}, "antes de su hora, nada"
    ok, error = elegir(db, "Ana", token())
    assert not ok and "no está activo" in error

    programado(db, "-1 second", "6 hours")
    assert rpc(db, "estado_del_juego", EVENTO)[1]["activo"] is True
    assert elegir(db, "Ana", token())[0], "a su hora empieza solo, sin que nadie lo active"

    programado(db, "-7 hours", "-1 second")
    datos = rpc(db, "estado_del_juego", EVENTO)[1]
    assert (datos["activo"], datos["terminado"]) == (False, True), "a su hora termina solo"


# @scenarios el-panel-se-ve-sin-pin
def test_el_tablero_se_ve_sin_pin_y_las_palabras_solo_antes_de_empezar_y_al_terminar(db):
    programado(db, "1 hour", "7 hours")
    datos = tablero(db)
    assert (datos["antes"], datos["activo"], datos["terminado"]) == (True, False, False)
    assert [p["palabra"] for p in datos["palabras"]] == ["casas", "perro", "lapiz"], "antes, para revisarlas"
    assert datos["empieza_en"] and datos["terminado_en"]

    programado(db, "-1 second", "6 hours")
    datos = tablero(db)
    assert (datos["antes"], datos["activo"]) == (False, True)
    assert all("palabra" not in p for p in datos["palabras"]), "durante el juego, nunca"
    assert {"jugadores", "grupos", "grupos_f1", "participantes", "elegidos"} <= set(datos)

    programado(db, "-7 hours", "-1 second")
    assert [p["palabra"] for p in tablero(db)["palabras"]] == ["casas", "perro", "lapiz"], "terminado, otra vez"


def doce_jugadores(db):
    """Doce participantes más, en dos grupos, con una palabra resuelta cada uno: J1 la más rápida, J12 la más lenta."""
    valor(db, f"insert into public.event_roster (evento, nombre, grupo) select '{EVENTO}', 'J' || i, "
              f"case when i % 2 = 1 then 'Impar' else 'Par' end from generate_series(1, 12) i")
    for i in range(1, 13):
        fijar(db, f"J{i}", 1, 10 * i, 1)


def quitar_doce(db):
    valor(db, f"delete from public.event_roster where evento = '{EVENTO}' and nombre like 'J%'")


# @scenarios los-diez-primeros-suman-f1-a-su-grupo
def test_los_diez_primeros_suman_a_su_grupo_los_puntos_de_la_f1(db):
    doce_jugadores(db)
    try:
        programado(db, "-1 hour", "5 hours")
        datos = tablero(db)
    finally:
        quitar_doce(db)

    f1 = {j["nombre"]: float(j["f1"]) for j in datos["jugadores"]}
    assert [f1[f"J{i}"] for i in range(1, 13)] == [25, 18, 15, 12, 10, 8, 6, 4, 2, 1, 0, 0]
    assert f1["Ana"] == 0, "sin puntos, sin F1"
    grupos = {g["grupo"]: g for g in datos["grupos_f1"]}
    assert float(grupos["Impar"]["puntos"]) == 25 + 15 + 10 + 6 + 2
    assert float(grupos["Par"]["puntos"]) == 18 + 12 + 8 + 4 + 1
    assert (grupos["Impar"]["puesto"], grupos["Par"]["puesto"]) == (1, 2)
    assert [(p["nombre"], float(p["puntos"])) for p in grupos["Impar"]["personas"]] == [
        ("J1", 25), ("J3", 15), ("J5", 10), ("J7", 6), ("J9", 2)]
    assert grupos["Rojo"]["personas"] == [] and float(grupos["Rojo"]["puntos"]) == 0


# @scenarios los-diez-primeros-suman-f1-a-su-grupo
def test_los_empatados_en_el_top_diez_se_reparten_los_puntos_de_sus_puestos(db):
    fijar(db, "Ana", 1, 60, 3)    # 150
    fijar(db, "Bea", 1, 90, 2)    # 150: empatan en cabeza
    fijar(db, "Cris", 1, 151, 0)  # 151
    programado(db, "-1 hour", "5 hours")

    f1 = {j["nombre"]: float(j["f1"]) for j in tablero(db)["jugadores"]}

    assert (f1["Ana"], f1["Bea"], f1["Cris"], f1["Dani"]) == (21.5, 21.5, 15, 0), "(25 + 18) / 2 cada uno"


# @scenarios se-cambian-las-palabras-antes-de-empezar
def test_antes_de_empezar_se_cambia_una_palabra_por_otra_del_diccionario(db):
    programado(db, "1 hour", "7 hours")
    try:
        ok, datos = rpc(db, "cambiar_palabra", EVENTO, 2, " Sácos ")
        assert ok and datos == {"orden": 2, "palabra": "sacos"}, datos
        assert [p["palabra"] for p in tablero(db)["palabras"]] == ["casas", "sacos", "lapiz"]
        for palabra, motivo in (("zzzzz", "diccionario"), ("casas", "ya está"), ("casa", "cinco letras")):
            ok, error = rpc(db, "cambiar_palabra", EVENTO, 3, palabra)
            assert not ok and motivo in error, (palabra, error)
        assert not rpc(db, "cambiar_palabra", EVENTO, 9, "salas")[0], "una palabra que no existe"

        programado(db, "-1 second", "6 hours")
        ok, error = rpc(db, "cambiar_palabra", EVENTO, 3, "salas")
        assert not ok and "ya ha empezado" in error
        assert valor(db, f"select palabra from public.event_targets where evento = '{EVENTO}' and orden = 3") == "lapiz"
    finally:
        valor(db, f"update public.event_targets set palabra = 'perro' where evento = '{EVENTO}' and orden = 2")


# @scenarios se-libera-un-nombre
def test_se_echa_a_un_participante_sin_pin_mientras_dura_el_evento(db):
    programado(db, "-1 second", "6 hours")
    tk = jugador(db, "Ana")
    assert empezar(db, tk, 1)[0]

    ok, datos = rpc(db, "echar_participante", EVENTO, "ana")

    assert ok and datos == {"nombre": "Ana"}, datos
    assert valor(db, "select count(*) from public.event_rounds") == "0"
    assert not rpc(db, "mi_juego", EVENTO, tk)[0]
    programado(db, "-7 hours", "-1 second")
    ok, error = rpc(db, "echar_participante", EVENTO, "Bea")
    assert not ok and "terminado" in error


# @scenarios la-web-no-toca-las-tablas-del-evento
def test_el_ayudante_de_la_f1_no_es_publico(db):
    resultado = db("select * from public.evento_f1('t')", rol="anon")
    assert resultado.returncode != 0 and "permission denied for function" in resultado.stderr
