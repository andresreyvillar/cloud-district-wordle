"""Las tablas y funciones del debate de reglas, de `debate-de-reglas`, contra un Postgres **local**.

Pack: `feat-debate-de-reglas`. **No se toca producción**: `tests/postgres_local.py` levanta un Postgres
desechable, aplica las migraciones del repositorio tal cual y lo ataca con los roles de Supabase.

Los jugadores son sintéticos: el repositorio es público.
"""

from __future__ import annotations

import pytest

from tests.postgres_local import postgres_con_migraciones, sin_postgres

pytestmark = sin_postgres

ANA, BEA, NADIE = "jugador-ana", "jugador-bea", "no-ha-jugado"
VOTACION = "anti-spoilers"


@pytest.fixture(scope="module")
def db():
    arranque = postgres_con_migraciones(
        "insert into public.wordle_results (player_name, wordle_id, score, date, slack_user_id) values "
        f"('Ana', 1742, 4, '2026-10-14', '{ANA}'), ('Bea', 1742, 3, '2026-10-14', '{BEA}')"
    )
    sql = next(arranque)
    yield sql
    arranque.close()


@pytest.fixture(autouse=True)
def limpio(db):
    assert db("truncate public.rule_votes, public.rule_proposals; "
              f"update public.rule_polls set abierta = true where id = '{VOTACION}'").returncode == 0


def votar(db, votante, opcion, votacion=VOTACION):
    return db(f"select public.votar_regla('{votacion}', '{votante}', '{opcion}')", rol="anon")


def proponer(db, autor, titulo="Sin spoilers", texto="Nada de pistas antes de las 18:00."):
    return db(f"select public.proponer_regla('{autor}', $t${titulo}$t$, $t${texto}$t$)", rol="anon")


def opciones(db):
    return db(f"select o->>'id' from public.rule_polls, jsonb_array_elements(opciones) o where id = '{VOTACION}'").stdout.split()


# @scenarios la-votacion-abierta-se-ve-con-su-recuento
def test_la_votacion_anti_spoilers_existe_abierta_y_con_la_opcion_de_no_hacer_nada(db):
    fila = db(f"select abierta from public.rule_polls where id = '{VOTACION}'", rol="anon").stdout.strip()

    assert fila == "t"
    assert "nada" in opciones(db), "el grupo puede decidir no hacer nada"
    assert len(opciones(db)) >= 3


# @scenarios se-vota-eligiendo-tu-nombre
def test_la_clave_publica_vota_con_la_funcion_y_el_voto_se_lee(db):
    resultado = votar(db, ANA, opciones(db)[0])

    assert resultado.returncode == 0, resultado.stderr
    assert db("select votante, opcion from public.rule_votes", rol="anon").stdout.strip() == f"{ANA}|{opciones(db)[0]}"


# @scenarios el-voto-se-puede-cambiar
def test_votar_otra_vez_cambia_el_voto_y_no_lo_duplica(db):
    primera, segunda = opciones(db)[:2]
    assert votar(db, ANA, primera).returncode == 0
    assert votar(db, ANA, segunda).returncode == 0

    assert db("select opcion from public.rule_votes", rol="anon").stdout.split() == [segunda]


# @scenarios una-votacion-cerrada-no-admite-votos
def test_una_votacion_cerrada_rechaza_el_voto(db):
    assert db(f"update public.rule_polls set abierta = false where id = '{VOTACION}'").returncode == 0

    resultado = votar(db, ANA, opciones(db)[0])

    assert resultado.returncode != 0
    assert "cerrada" in resultado.stderr
    assert db("select count(*) from public.rule_votes").stdout.strip() == "0"


# @scenarios la-base-de-datos-valida-lo-que-entra
@pytest.mark.parametrize("votante, opcion, votacion, motivo", [
    (NADIE, "nada", VOTACION, "jugador desconocido"),
    (ANA, "inventada", VOTACION, "opción desconocida"),
    (ANA, "nada", "no-existe", "votación desconocida"),
])
def test_un_voto_imposible_se_rechaza(db, votante, opcion, votacion, motivo):
    resultado = votar(db, votante, opcion, votacion)

    assert resultado.returncode != 0
    assert motivo in resultado.stderr
    assert db("select count(*) from public.rule_votes").stdout.strip() == "0"


# @scenarios una-propuesta-queda-pendiente
def test_una_propuesta_entra_pendiente(db):
    resultado = proponer(db, BEA, "  Sin spoilers  ")

    assert resultado.returncode == 0, resultado.stderr
    assert '"pendiente"' in resultado.stdout
    assert db("select autor, titulo, estado from public.rule_proposals").stdout.strip() == f"{BEA}|Sin spoilers|pendiente"


# @scenarios solo-se-ven-las-propuestas-aprobadas, una-propuesta-queda-pendiente
def test_la_clave_publica_solo_lee_las_aprobadas(db):
    for titulo in ("Uno", "Dos", "Tres"):
        assert proponer(db, ANA, titulo).returncode == 0
    assert db("update public.rule_proposals set estado = 'aprobada' where titulo = 'Uno'; "
              "update public.rule_proposals set estado = 'rechazada' where titulo = 'Dos'").returncode == 0

    assert db("select titulo from public.rule_proposals", rol="anon").stdout.split() == ["Uno"]


# @scenarios la-base-de-datos-valida-lo-que-entra
@pytest.mark.parametrize("autor, titulo, texto, motivo", [
    (NADIE, "Sin spoilers", "Nada de pistas antes de las 18:00.", "jugador desconocido"),
    (ANA, "  ", "Nada de pistas antes de las 18:00.", "título"),
    (ANA, "x" * 121, "Nada de pistas antes de las 18:00.", "título"),
    (ANA, "Sin spoilers", "corto", "explicación"),
    (ANA, "Sin spoilers", "\n" * 12, "explicación"),
    (ANA, "\t\n\t\n", "Nada de pistas antes de las 18:00.", "título"),
    (ANA, "Sin spoilers", "x" * 2001, "explicación"),
])
def test_una_propuesta_imposible_se_rechaza(db, autor, titulo, texto, motivo):
    resultado = proponer(db, autor, titulo, texto)

    assert resultado.returncode != 0
    assert motivo in resultado.stderr
    assert db("select count(*) from public.rule_proposals").stdout.strip() == "0"


# @scenarios la-base-de-datos-valida-lo-que-entra
def test_con_tres_pendientes_no_se_admite_una_cuarta(db):
    for titulo in ("Uno", "Dos", "Tres"):
        assert proponer(db, ANA, titulo).returncode == 0

    cuarta = proponer(db, ANA, "Cuatro")

    assert cuarta.returncode != 0
    assert "pendientes" in cuarta.stderr
    assert proponer(db, BEA, "De otra persona").returncode == 0, "el tope es por persona"


# @scenarios la-web-no-escribe-en-las-tablas
@pytest.mark.parametrize("rol", ["anon", "authenticated"])
@pytest.mark.parametrize("sentencia", [
    f"insert into public.rule_votes (votacion, votante, opcion) values ('{VOTACION}', '{ANA}', 'nada')",
    f"insert into public.rule_proposals (autor, titulo, texto, estado) values ('{ANA}', 'X', 'Una explicación', 'aprobada')",
    "update public.rule_polls set abierta = false",
    "delete from public.rule_polls",
    "truncate public.rule_votes",
])
def test_la_clave_publica_no_escribe_en_las_tablas(db, sentencia, rol):
    resultado = db(sentencia, rol=rol)

    assert resultado.returncode != 0, f"{rol} pudo ejecutar: {sentencia}"
    assert "permission denied" in resultado.stderr
