"""El arranque, las liberaciones, el final y el ranking del evento, de `pantalla-del-evento`, contra un Postgres
**local**.

Cambio: `feat-frase-del-evento`. **No se toca producción**. Participantes, frases y PIN sintéticos.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from tests.evento_sql import (
    EVENTO, PIN, SEMILLA, empezado_hace, estado, fijar_tiempo, intentar, participante, reiniciar, rpc, terminado, valor,
)
from tests.postgres_local import MIGRACIONES, postgres_con_migraciones, sin_postgres

pytestmark = sin_postgres


@pytest.fixture(scope="module")
def db():
    arranque = postgres_con_migraciones()
    sql = next(arranque)
    assert sql(SEMILLA).returncode == 0
    yield sql
    arranque.close()


@pytest.fixture(autouse=True)
def limpio(db):
    reiniciar(db)


def campo(db, columna):
    return valor(db, f"select coalesce({columna}::text, '') from public.event_editions where id = '{EVENTO}'")


def ranking(db):
    ok, datos = rpc(db, "ranking_del_evento", EVENTO)
    assert ok, datos
    return {fila["nombre"]: fila for fila in datos}, datos


def perder(db, tk, orden=1):
    for palabra in ["tunde", "pique", "chufa", "nieve", "bucle"]:
        intentar(db, tk, palabra, orden)


# @scenarios se-empieza-con-el-pin
def test_el_pin_correcto_fija_el_inicio_con_la_hora_del_servidor(db):
    ok, datos = rpc(db, "empezar_evento", EVENTO, PIN)

    assert ok, datos
    assert valor(db, "select abs(extract(epoch from now() - empieza_en)) < 5 from public.event_editions") == "t"
    assert [f["estado"] for f in estado(db)["frases"]] == ["abierta", "pendiente", "pendiente"]


# @scenarios un-pin-incorrecto-no-hace-nada
@pytest.mark.parametrize("pin", ["", "PIN-DE-TEST", "pin-de-test ", None])
def test_un_pin_incorrecto_no_empieza_ni_termina(db, pin):
    ok, error = rpc(db, "empezar_evento", EVENTO, pin)
    assert not ok and "PIN" in error
    assert campo(db, "empieza_en") == ""

    empezado_hace(db, 60)
    ok, error = rpc(db, "terminar_evento", EVENTO, pin)
    assert not ok and "PIN" in error
    assert campo(db, "terminado_en") == ""


# @scenarios empezar-otra-vez-no-reinicia
def test_empezar_un_evento_empezado_no_mueve_el_inicio(db):
    empezado_hace(db, 120)
    antes = campo(db, "empieza_en")

    ok, _ = rpc(db, "empezar_evento", EVENTO, PIN)

    assert ok
    assert campo(db, "empieza_en") == antes


# @scenarios las-frases-se-liberan-cada-intervalo
def test_la_frase_k_se_libera_a_los_k_menos_uno_intervalos_y_sigue_abierta(db):
    empezado_hace(db, 601)
    frases = estado(db)["frases"]

    assert [f["estado"] for f in frases] == ["abierta", "abierta", "pendiente"]
    assert valor(db, f"select (empieza_en + interval '10 minutes')::text from public.event_editions") \
        == valor(db, f"select ('{frases[1]['abre_en']}'::timestamptz)::text")


# @scenarios las-frases-se-liberan-cada-intervalo
def test_sin_empezar_todas_estan_pendientes_y_el_estado_trae_la_hora_del_servidor(db):
    datos = estado(db)

    assert [f["estado"] for f in datos["frases"]] == ["pendiente"] * 3
    assert datos["ahora"] and datos["empieza_en"] is None and datos["terminado"] is False


# @scenarios el-intervalo-se-cambia-sin-codigo
def test_el_intervalo_se_cambia_antes_de_empezar_y_no_despues(db):
    valor(db, f"update public.event_editions set intervalo_minutos = 30 where id = '{EVENTO}'")
    empezado_hace(db, 601)
    assert [f["estado"] for f in estado(db)["frases"]] == ["abierta", "pendiente", "pendiente"]

    cambio = db(f"update public.event_editions set intervalo_minutos = 1 where id = '{EVENTO}'")

    assert cambio.returncode != 0 and "ya ha empezado" in cambio.stderr
    valor(db, f"update public.event_editions set empieza_en = null, intervalo_minutos = 2 where id = '{EVENTO}'")
    assert campo(db, "intervalo_minutos") == "2", "para un ensayo, se vacía el inicio"


# @scenarios los-contadores-no-tienen-nombres
def test_el_estado_cuenta_jugando_resueltas_y_sin_palabras_sin_nombres_ni_tiempos(db):
    empezado_hace(db, 60)
    resuelve, pierde = participante(db, "Ana"), participante(db, "Bea")
    participante(db, "Cris")
    intentar(db, resuelve, "salmo")
    intentar(db, resuelve, "rayos")
    perder(db, pierde)

    datos = estado(db)
    frase = datos["frases"][0]

    assert (frase["jugando"], frase["resueltas"], frase["sin_resolver"]) == (1, 1, 1)
    assert datos["participantes"] == 3
    texto = json.dumps(datos)
    assert not any(nombre in texto for nombre in ("Ana", "Bea", "Cris"))
    assert "tiempo" not in texto


# @scenarios se-termina-con-el-pin
def test_el_pin_correcto_termina_el_evento_y_terminar_otra_vez_no_lo_mueve(db):
    assert not rpc(db, "terminar_evento", EVENTO, PIN)[0], "sin empezar no se termina"
    empezado_hace(db, 1300)

    ok, datos = rpc(db, "terminar_evento", EVENTO, PIN)
    assert ok, datos
    antes = campo(db, "terminado_en")
    assert rpc(db, "terminar_evento", EVENTO, PIN)[0]

    assert campo(db, "terminado_en") == antes
    assert estado(db)["terminado"] is True
    assert [f["estado"] for f in estado(db)["frases"]] == ["cerrada"] * 3


# @scenarios al-terminar-se-ven-las-soluciones
def test_el_estado_trae_las_soluciones_solo_con_el_evento_terminado(db):
    empezado_hace(db, 1300)
    assert all("solucion" not in f for f in estado(db)["frases"])

    terminado(db)

    assert [f.get("solucion") for f in estado(db)["frases"]] == ["sol y mar", "El año, canción", "Más vale tarde"]


# @scenarios el-ranking-ordena-por-frases-y-tiempo
def test_mas_frases_resueltas_va_delante_aunque_tarde_mas(db):
    empezado_hace(db, 601)
    ana, bea = participante(db, "Ana"), participante(db, "Bea")
    valor(db, "insert into public.event_plays (jugador, orden, empezada_en) "
              "select id, 2, now() from public.event_players where nombre = 'Ana'")
    fijar_tiempo(db, ana, 1, 300_000)
    fijar_tiempo(db, ana, 2, 300_000)
    fijar_tiempo(db, bea, 1, 60_000)
    terminado(db)

    filas, lista = ranking(db)

    assert [f["nombre"] for f in lista] == ["Ana", "Bea"]
    assert (filas["Ana"]["resueltas"], filas["Ana"]["tiempo_ms"]) == (2, 600_000)
    assert (filas["Bea"]["resueltas"], filas["Bea"]["tiempo_ms"]) == (1, 60_000)


# @scenarios el-ranking-ordena-por-frases-y-tiempo
def test_con_las_mismas_frases_va_delante_quien_tardo_menos(db):
    empezado_hace(db, 60)
    ana, bea = participante(db, "Ana"), participante(db, "Bea")
    fijar_tiempo(db, ana, 1, 90_000)
    fijar_tiempo(db, bea, 1, 45_500)
    terminado(db)

    _, lista = ranking(db)

    assert [(f["nombre"], f["puesto"]) for f in lista] == [("Bea", 1), ("Ana", 2)]


# @scenarios el-tiempo-cuenta-al-terminar-la-partida
def test_suman_las_resueltas_y_las_perdidas_y_no_las_partidas_a_medias(db):
    empezado_hace(db, 601)
    ana, bea, cris = participante(db, "Ana"), participante(db, "Bea"), participante(db, "Cris")
    fijar_tiempo(db, ana, 1, 60_000)
    perder(db, bea)  # perdida: suma tiempo, no frase
    intentar(db, cris, "sacas")  # a medias: no suma nada y no sale
    valor(db, "update public.event_plays pl set terminada_en = pl.empezada_en + interval '120 seconds' "
              "from public.event_players p where p.id = pl.jugador and p.nombre = 'Bea'")
    terminado(db)

    filas, _ = ranking(db)

    assert (filas["Ana"]["resueltas"], filas["Ana"]["tiempo_ms"]) == (1, 60_000)
    assert (filas["Bea"]["resueltas"], filas["Bea"]["tiempo_ms"]) == (0, 120_000)
    assert "Cris" not in filas


# @scenarios el-empate-comparte-puesto
def test_las_mismas_frases_y_el_mismo_tiempo_comparten_puesto(db):
    empezado_hace(db, 60)
    ana, bea, cris = participante(db, "Ana"), participante(db, "Bea"), participante(db, "Cris")
    fijar_tiempo(db, ana, 1, 100_000)
    fijar_tiempo(db, bea, 1, 100_000)
    fijar_tiempo(db, cris, 1, 100_001)
    terminado(db)

    _, lista = ranking(db)

    assert [f["puesto"] for f in lista] == [1, 1, 3]


# @scenarios el-ranking-sale-al-terminar-el-evento
def test_el_ranking_solo_se_entrega_con_el_evento_terminado(db):
    assert not rpc(db, "ranking_del_evento", EVENTO)[0], "sin empezar"
    empezado_hace(db, 99_999)
    assert not rpc(db, "ranking_del_evento", EVENTO)[0], "con todas liberadas pero sin terminar"

    terminado(db)

    assert rpc(db, "ranking_del_evento", EVENTO)[0]


# @scenarios el-ranking-sale-al-terminar-el-evento, la-pantalla-pide-la-contrasena
def test_con_contrasena_el_ranking_solo_se_entrega_con_ella_o_con_un_token(db):
    empezado_hace(db, 60)
    tk = participante(db, "Ana")
    fijar_tiempo(db, tk, 1, 60_000)
    terminado(db)
    valor(db, "update public.event_editions set clave_hash = encode(sha256(convert_to('cl4ve', 'UTF8')), 'hex')")

    assert not rpc(db, "ranking_del_evento", EVENTO)[0]
    assert not rpc(db, "ranking_del_evento", EVENTO, None, "mala")[0]
    assert rpc(db, "ranking_del_evento", EVENTO, None, "cl4ve")[1][0]["nombre"] == "Ana"
    assert rpc(db, "ranking_del_evento", EVENTO, tk, None)[0]
    assert "solucion" not in json.dumps(rpc(db, "estado_del_evento", EVENTO)[1]), "cerrado no enseña las frases"


# @scenarios el-pin-no-esta-en-el-repositorio
def test_las_migraciones_no_traen_frases_ni_huella_de_pin():
    for migracion in MIGRACIONES.glob("*.sql"):
        texto = migracion.read_text(encoding="utf-8")
        sin_comentarios = re.sub(r"--[^\n]*", "", texto)
        assert not re.search(r"insert\s+into\s+public\.event_(editions|phrases)\b", sin_comentarios, re.I), migracion.name
        assert not re.search(r"\b[0-9a-f]{64}\b", texto), migracion.name

    semilla = Path(MIGRACIONES).parent / "seeds" / "evento_de_prueba.sql"
    assert "'prueba'" in semilla.read_text(encoding="utf-8"), "en el repositorio solo está el evento de prueba"
