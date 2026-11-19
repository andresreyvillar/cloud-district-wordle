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
    assert (filas["Ana"]["puesto"], filas["Ana"]["puntos"]) == (1, 2)
    assert (filas["Bea"]["puesto"], filas["Bea"]["puntos"]) == (2, 1)
    assert filas["Cris"]["puntos"] == 0
    grupos = {g["grupo"]: g for g in datos["grupos"]}
    assert (grupos["Rojo"]["puesto"], grupos["Rojo"]["puntos_totales"]) == (1, 3)

    fijar(db, "Dani", 1, 10, 1)   # 10 + 30 = 40: la mejor marca, y los demás no bajan
    filas = {j["nombre"]: j for j in panel(db)["jugadores"]}
    assert (filas["Dani"]["puntos"], filas["Ana"]["puntos"], filas["Bea"]["puntos"]) == (3, 2, 1)


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

    assert (tabla["Cris"], tabla["Ana"], tabla["Bea"], tabla["Dani"], tabla["Eva"]) == (3, 2, 1, 0, 0)
    assert [j["nombre"] for j in datos["jugadores"][:3]] == ["Cris", "Ana", "Bea"]
    ana = next(j for j in datos["jugadores"] if j["nombre"] == "Ana")
    assert ana["palabras"] == [{"orden": 1, "resuelta": True, "intentos": 4, "tiempo_ms": 30_000,
                                "marca_ms": 150_000, "puntos": 2}]


# @scenarios cada-palabra-puntua-por-tiempo-e-intentos
def test_las_palabras_puntuan_por_separado_y_se_suman(db):
    fijar(db, "Ana", 1, 30, 3)
    fijar(db, "Bea", 1, 40, 3)
    fijar(db, "Ana", 2, 90, 4)
    fijar(db, "Bea", 2, 20, 2)
    fijar(db, "Cris", 2, 20, 6)
    terminado(db)

    tabla, _ = puntos(db)

    assert (tabla["Ana"], tabla["Bea"], tabla["Cris"]) == (2 + 1, 1 + 3, 0 + 2)


# @scenarios cada-palabra-puntua-por-tiempo-e-intentos
def test_una_palabra_a_medias_al_terminar_no_puntua(db):
    activado(db)
    tk = jugador(db, "Ana")
    assert empezar(db, tk, 1)[0]
    fijar(db, "Bea", 1, 300, 6)
    terminado(db)

    tabla, _ = puntos(db)

    assert (tabla["Ana"], tabla["Bea"]) == (0, 1)


# @scenarios el-empate-comparte-puntos
def test_la_misma_marca_da_los_mismos_puntos(db):
    fijar(db, "Ana", 1, 60, 3)    # 150
    fijar(db, "Bea", 1, 90, 2)    # 150
    fijar(db, "Cris", 1, 151, 0)  # 151 (sin intentos no pasa en el juego: solo fija la marca)
    terminado(db)

    tabla, datos = puntos(db)

    assert (tabla["Ana"], tabla["Bea"], tabla["Cris"]) == (2, 2, 1)
    assert [j["puesto"] for j in datos["jugadores"][:3]] == [1, 1, 3]


# @scenarios los-segundos-por-intento-se-cambian-sin-codigo
def test_con_otros_segundos_por_intento_cambia_quien_gana(db):
    fijar(db, "Ana", 1, 30, 4)
    fijar(db, "Bea", 1, 70, 3)
    valor(db, "update public.event_editions set segundos_por_intento = 45")
    terminado(db)

    tabla, datos = puntos(db)

    assert (tabla["Bea"], tabla["Ana"]) == (2, 1), "con 45 s, 70 + 135 = 205 gana a 30 + 180 = 210"
    assert datos["segundos_por_intento"] == 45


# @scenarios la-puntuacion-del-grupo-es-la-media-de-su-lista
def test_el_grupo_puntua_la_media_de_toda_su_lista(db):
    fijar(db, "Ana", 1, 10, 1)    # Rojo: 3 + 0 (Bea no juega)
    fijar(db, "Cris", 1, 20, 1)   # Azul: 2 + 1
    fijar(db, "Dani", 1, 30, 1)
    terminado(db)

    _, datos = puntos(db)

    grupos = {g["grupo"]: g for g in datos["grupos"]}
    assert (grupos["Rojo"]["puntos_totales"], float(grupos["Rojo"]["puntos"])) == (3, 1.5)
    assert (grupos["Azul"]["puntos_totales"], float(grupos["Azul"]["puntos"])) == (3, 1.5)
    assert (grupos["Rojo"]["miembros"], grupos["Rojo"]["jugaron"]) == (2, 1)
    assert float(grupos["Verde"]["puntos"]) == 0
    assert [g["puesto"] for g in datos["grupos"]] == [1, 1, 3]


# @scenarios la-puntuacion-del-grupo-es-la-media-de-su-lista
def test_el_puesto_del_grupo_sale_de_la_media_sin_redondear(db):
    valor(db, f"insert into public.event_roster (evento, nombre, grupo) "
              f"select '{EVENTO}', 'P' || i, 'Veinte' from generate_series(1, 20) i union all "
              f"select '{EVENTO}', 'Q' || i, 'Veintiuno' from generate_series(1, 21) i")
    try:
        fijar(db, "P1", 1, 60, 3)
        fijar(db, "Q1", 1, 60, 3)   # la misma marca: 1 punto cada uno; 1/20 = 0,05 y 1/21 = 0,0476 (0,05 redondeado)
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
