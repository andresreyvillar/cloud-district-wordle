"""La tabla y la función del ranking del juego, de `ranking-del-juego`, contra un Postgres **local**.

Pack: `feat-ranking-del-juego`.

**No se toca producción.** Cada ejecución levanta un Postgres desechable (`tests/postgres_local.py`), le aplica
las migraciones del repositorio tal cual y la prueba con los mismos roles que usa Supabase (`anon`,
`authenticated`). Si la máquina no tiene Postgres, se salta: la verificación en producción se hace aparte, en
transacciones que se deshacen, y queda en `runs.yaml`.

Desde `nivel-congelado`, la función mide contra el nivel congelado de la jornada, así que el fixture congela
uno de 15 tramos.

Los jugadores son sintéticos: el repositorio es público.
"""

from __future__ import annotations

import json

import pytest

from tests.postgres_local import postgres_con_migraciones, sin_postgres

JORNADA = 1722
TRAMOS = 15
# 15 tramos × 8 casillas × 32 px ÷ 450 px/s
MINIMO = TRAMOS * 8 * 32 / 450
JUGADOR = "jugador-00"
SOLO_OTRO_DIA = "jugo-otro-dia"

pytestmark = sin_postgres

FILAS = [f"('j{i}', {JORNADA}, 3, '2026-09-24', 'jugador-{i:02d}', '🟩⬛⬛⬛⬛/🟩🟩🟩🟩🟩')" for i in range(TRAMOS)]
FILAS.append(f"('otro', 1700, 4, '2026-09-02', '{SOLO_OTRO_DIA}', '🟩🟩🟩🟩🟩')")

NIVEL = {
    "widthTiles": TRAMOS * 8 + 5,
    "labels": [{"col": 8 * i + 3, "row": 4, "text": f"j{i}  2/6"} for i in range(TRAMOS)],
    "collectibles": [{"col": 8 * i + 3, "row": 3} for i in range(TRAMOS)],
}


@pytest.fixture(scope="module")
def db():
    arranque = postgres_con_migraciones(
        "insert into public.wordle_results (player_name, wordle_id, score, date, slack_user_id, pattern) values "
        + ",".join(FILAS)
    )
    sql = next(arranque)
    congelado = sql(
        f"insert into public.game_levels (jornada, fecha, nivel) values ({JORNADA}, '2026-09-24', '{json.dumps(NIVEL)}')"
    )
    assert congelado.returncode == 0, congelado.stderr
    yield sql
    arranque.close()


@pytest.fixture(autouse=True)
def sin_marcas(db):
    assert db("truncate public.game_times").returncode == 0


def registrar(db, segundos, jugador=JUGADOR, estrellas=3, jornada=JORNADA):
    return db(f"select public.registrar_tiempo({jornada}, '{jugador}', {segundos}, {estrellas})", rol="anon")


def marca(db, jugador=JUGADOR):
    return db(f"select segundos, estrellas from public.game_times where jornada = {JORNADA} and jugador = '{jugador}'").stdout.strip()


# @scenarios terminar-registra-el-tiempo
def test_la_clave_publica_registra_una_marca_con_la_funcion(db):
    resultado = registrar(db, 42.371)

    assert resultado.returncode == 0, resultado.stderr
    assert '"mejora": true' in resultado.stdout
    assert marca(db) == "42.37|3", "se guarda con centésimas"


# @scenarios solo-se-sobrescribe-si-mejora
def test_un_tiempo_peor_no_pisa_la_marca(db):
    registrar(db, 40, estrellas=5)
    resultado = registrar(db, 55, estrellas=1)

    assert resultado.returncode == 0, resultado.stderr
    assert '"mejora": false' in resultado.stdout
    assert '"segundos": 40' in resultado.stdout, "devuelve la marca que se queda"
    assert marca(db) == "40.00|5"


# @scenarios solo-se-sobrescribe-si-mejora
def test_un_tiempo_igual_tampoco_la_pisa(db):
    registrar(db, 40, estrellas=1)
    resultado = registrar(db, 40, estrellas=5)

    assert '"mejora": false' in resultado.stdout
    assert marca(db) == "40.00|1"


# @scenarios solo-se-sobrescribe-si-mejora
def test_un_tiempo_mejor_si_la_pisa(db):
    registrar(db, 40, estrellas=5)
    resultado = registrar(db, 31.5, estrellas=2)

    assert '"mejora": true' in resultado.stdout
    assert marca(db) == "31.50|2"


# @scenarios solo-se-sobrescribe-si-mejora
def test_la_marca_de_uno_no_toca_la_de_otro(db):
    registrar(db, 40)
    registrar(db, 30, jugador="jugador-01")

    assert marca(db) == "40.00|3"
    assert marca(db, "jugador-01") == "30.00|3"


# @scenarios la-web-no-escribe-en-la-tabla
@pytest.mark.parametrize("sentencia", [
    f"insert into public.game_times (jornada, jugador, segundos, estrellas) values ({JORNADA}, '{JUGADOR}', 20, 1)",
    "update public.game_times set segundos = 10",
    "delete from public.game_times",
    "truncate public.game_times",
])
@pytest.mark.parametrize("rol", ["anon", "authenticated"])
def test_la_clave_publica_no_escribe_en_la_tabla(db, sentencia, rol):
    registrar(db, 40)

    resultado = db(sentencia, rol=rol)

    assert resultado.returncode != 0, f"{rol} pudo ejecutar: {sentencia}"
    assert marca(db) == "40.00|3", "la marca sigue intacta"


# @scenarios la-web-no-escribe-en-la-tabla
def test_la_clave_publica_si_lee_la_tabla(db):
    registrar(db, 40)

    assert db("select count(*) from public.game_times", rol="anon").stdout.strip() == "1"


# @scenarios la-web-no-escribe-en-la-tabla
def test_la_funcion_no_se_deja_secuestrar_por_el_search_path(db):
    """Una función `security definer` con `search_path` abierto ejecuta lo que el llamante ponga delante."""
    config = db("select array_to_string(proconfig, ',') from pg_proc where proname = 'registrar_tiempo'").stdout

    assert 'search_path=""' in config


# @scenarios rechaza-lo-imposible
@pytest.mark.parametrize("llamada, motivo", [
    (dict(jugador="no-existe"), "jugador desconocido"),
    (dict(jornada=1600), "esa jornada no tiene nivel"),
    (dict(estrellas=TRAMOS + 1), "estrellas imposibles"),
    (dict(estrellas=-1), "estrellas imposibles"),
    (dict(segundos=round(MINIMO - 0.1, 2)), "tiempo imposible"),
    (dict(segundos=3600), "tiempo imposible"),
    (dict(segundos=0), "tiempo imposible"),
    (dict(segundos="'NaN'"), "tiempo imposible"),
    (dict(segundos="'Infinity'"), "tiempo imposible"),
    (dict(segundos="'-Infinity'"), "tiempo imposible"),
])
def test_lo_imposible_se_rechaza_y_no_se_escribe(db, llamada, motivo):
    argumentos = {"segundos": 40, **llamada}

    resultado = registrar(db, **argumentos)

    assert resultado.returncode != 0
    assert motivo in resultado.stderr
    assert db("select count(*) from public.game_times").stdout.strip() == "0"


# @scenarios rechaza-lo-imposible
def test_justo_por_encima_del_minimo_entra(db):
    """El mínimo es un suelo, no un filtro de tiempos rápidos: una centésima por encima entra."""
    resultado = registrar(db, round(MINIMO + 0.01, 2))

    assert resultado.returncode == 0, resultado.stderr


# @scenarios rechaza-lo-imposible
def test_quien_jugo_otro_dia_tambien_puede_jugar_este_nivel(db):
    assert registrar(db, 40, jugador=SOLO_OTRO_DIA).returncode == 0
