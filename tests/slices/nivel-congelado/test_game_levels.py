"""La tabla de niveles congelados, de `nivel-congelado`, contra un Postgres **local** (`tests/postgres_local.py`).

Pack: `feat-nivel-congelado`. No se toca producción. Los jugadores son sintéticos.
"""

from __future__ import annotations

import json

import pytest

from tests.postgres_local import postgres_con_migraciones, sin_postgres

pytestmark = sin_postgres

JORNADA = 1722
NIVEL = {
    "widthTiles": 2 * 8 + 5,
    "labels": [{"col": 3, "row": 4, "text": "Ana  2/6"}, {"col": 11, "row": 4, "text": "Bea  2/6"}],
    "collectibles": [{"col": 3, "row": 3}],
}
FILAS = ",".join([
    f"('Ana', {JORNADA}, 2, '2026-09-24', 'U_ANA', '🟩⬛⬛⬛⬛/🟩🟩🟩🟩🟩')",
    f"('Bea', {JORNADA}, 2, '2026-09-24', 'U_BEA', '🟩⬛⬛⬛⬛/🟩🟩🟩🟩🟩')",
    # La 1723 tiene cuadrículas en la tabla pero no está congelada.
    "('Ana', 1723, 3, '2026-09-25', 'U_ANA', '🟩⬛⬛⬛⬛/🟩🟩⬛⬛⬛/🟩🟩🟩🟩🟩')",
])


@pytest.fixture(scope="module")
def db():
    arranque = postgres_con_migraciones(
        "insert into public.wordle_results (player_name, wordle_id, score, date, slack_user_id, pattern) values " + FILAS
    )
    sql = next(arranque)
    congelado = sql(
        f"insert into public.game_levels (jornada, fecha, nivel) values ({JORNADA}, '2026-09-24', '{json.dumps(NIVEL)}')",
        rol="service_role",
    )
    assert congelado.returncode == 0, congelado.stderr
    yield sql
    arranque.close()


@pytest.fixture(autouse=True)
def sin_marcas(db):
    assert db("truncate public.game_times").returncode == 0


def intentar(db, sentencia, rol=None):
    """Un intento de escritura **dentro de una transacción que se deshace**: si una regresión lo dejara pasar,
    el test cae en rojo sin borrar el nivel compartido y arrastrar a los demás."""
    return db(f"begin;\n{sentencia};\nrollback;", rol=rol)


def nivel_guardado(db):
    return json.loads(db(f"select nivel from public.game_levels where jornada = {JORNADA}").stdout)


# @scenarios un-nivel-congelado-no-cambia
@pytest.mark.parametrize("sentencia", [
    f"update public.game_levels set nivel = '{{}}' where jornada = {JORNADA}",
    f"delete from public.game_levels where jornada = {JORNADA}",
    "truncate public.game_levels",
])
@pytest.mark.parametrize("rol", ["service_role", None])
def test_un_nivel_congelado_no_se_cambia_ni_con_la_clave_de_servicio(db, sentencia, rol):
    resultado = intentar(db, sentencia, rol=rol)

    assert resultado.returncode != 0, f"{rol or 'postgres'} pudo ejecutar: {sentencia}"
    assert "un nivel congelado no se cambia" in resultado.stderr
    assert nivel_guardado(db) == NIVEL


# @scenarios un-nivel-congelado-no-cambia
@pytest.mark.parametrize("nivel", ['{}', '{"labels": null, "collectibles": []}', '{"labels": [], "collectibles": {}}'])
def test_un_nivel_mal_formado_no_se_puede_congelar(db, nivel):
    """Después ya no se podría corregir: se rechaza al congelarlo."""
    resultado = intentar(
        db, f"insert into public.game_levels (jornada, fecha, nivel) values (1800, '2026-11-11', '{nivel}')",
        rol="service_role",
    )

    assert resultado.returncode != 0
    assert "nivel_con_forma" in resultado.stderr


# @scenarios un-nivel-congelado-no-cambia
def test_volver_a_congelar_la_misma_jornada_no_la_pisa(db):
    """Lo que hace el script: `on conflict do nothing`. Ni error ni cambio."""
    resultado = db(
        f"insert into public.game_levels (jornada, fecha, nivel) values ({JORNADA}, '2026-09-24', '{{\"labels\": [], \"collectibles\": []}}') "
        "on conflict (jornada) do nothing",
        rol="service_role",
    )

    assert resultado.returncode == 0, resultado.stderr
    assert nivel_guardado(db) == NIVEL


# @scenarios un-nivel-congelado-no-cambia
@pytest.mark.parametrize("sentencia", [
    f"insert into public.game_levels (jornada, fecha, nivel) values (1799, '2026-11-10', '{{}}')",
    f"update public.game_levels set nivel = '{{}}'",
])
@pytest.mark.parametrize("rol", ["anon", "authenticated"])
def test_la_clave_publica_no_congela_ni_cambia_niveles(db, sentencia, rol):
    assert intentar(db, sentencia, rol=rol).returncode != 0
    assert db("select count(*) from public.game_levels").stdout.strip() == "1"


# @scenarios la-web-juega-el-ultimo-nivel-congelado
def test_la_clave_publica_lee_los_niveles(db):
    leido = db(f"select nivel from public.game_levels where jornada = {JORNADA}", rol="anon")

    assert leido.returncode == 0, leido.stderr
    assert json.loads(leido.stdout) == NIVEL


def registrar(db, segundos, estrellas=1, jornada=JORNADA):
    return db(f"select public.registrar_tiempo({jornada}, 'U_ANA', {segundos}, {estrellas})", rol="anon")


# @scenarios el-ranking-se-mide-contra-el-nivel-congelado
def test_una_jornada_con_cuadriculas_pero_sin_congelar_no_admite_marcas(db):
    resultado = registrar(db, 60, jornada=1723)

    assert resultado.returncode != 0
    assert "esa jornada no tiene nivel" in resultado.stderr


# @scenarios el-ranking-se-mide-contra-el-nivel-congelado
def test_el_minimo_sale_de_los_tramos_del_nivel_congelado(db):
    """2 tramos → 2 × 8 × 32 ÷ 450 = 1,14 s. Con la cuenta de `wordle_results` también serían 2, así que el
    caso que decide es el de las estrellas, abajo; este fija el valor."""
    minimo = 2 * 8 * 32 / 450

    assert registrar(db, round(minimo - 0.01, 2)).returncode != 0
    assert registrar(db, round(minimo + 0.01, 2)).returncode == 0


# @scenarios el-ranking-se-mide-contra-el-nivel-congelado
def test_las_estrellas_se_acotan_a_los_coleccionables_del_nivel(db):
    """El nivel tiene 2 tramos pero 1 coleccionable: 2 estrellas son imposibles aunque haya 2 tramos."""
    resultado = registrar(db, 60, estrellas=2)

    assert resultado.returncode != 0
    assert "estrellas imposibles" in resultado.stderr
    assert registrar(db, 60, estrellas=1).returncode == 0
