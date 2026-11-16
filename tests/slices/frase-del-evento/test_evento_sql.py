"""Las tablas y funciones del juego del evento, de `frase-del-evento`, contra un Postgres **local**.

Cambio: `feat-frase-del-evento`. **No se toca producción**: `tests/postgres_local.py` levanta un Postgres
desechable, aplica las migraciones del repositorio tal cual (también el diccionario) y lo ataca con los roles de
Supabase.

Reglas de «La frase del día»: palabras válidas de cinco letras, cinco como mucho; verde destapa en toda la frase,
amarilla si ya estaba destapada, gris si no está; se gana al destapar todas las letras.

Los participantes y las frases son sintéticos: el repositorio es público y las frases reales no entran en él.
"""

from __future__ import annotations

import json

import pytest

from tests.evento_sql import (
    EVENTO, SEMILLA, empezado_hace, empezar, estado, intentar, participante, reiniciar, rpc, terminado, token, unirse,
    valor,
)
from tests.postgres_local import postgres_con_migraciones, sin_postgres

pytestmark = sin_postgres

TABLAS = ["event_editions", "event_phrases", "event_players", "event_plays", "event_guesses", "event_words"]


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
    empezado_hace(db, 60)  # la frase 1 liberada


def jugar(db, tk, palabra, orden=1):
    ok, partida = intentar(db, tk, palabra, orden)
    assert ok, partida
    return partida


def contar(db, tabla):
    return int(valor(db, f"select count(*) from public.{tabla}"))


# ── Entrar ────────────────────────────────────────────────────────────────────────────────────────────────

# @scenarios se-entra-con-un-nombre
def test_unirse_apunta_al_participante_y_devuelve_su_nombre(db):
    tk = token()

    ok, datos = unirse(db, "  Ana  ", tk)

    assert ok, datos
    assert datos == {"nombre": "Ana"}
    assert rpc(db, "mi_partida_del_evento", EVENTO, tk)[1]["nombre"] == "Ana", "al recargar sigue dentro"


# @scenarios se-entra-con-un-nombre
@pytest.mark.parametrize("nombre", ["María José", "O'Donnell", "Ana-Belén", "Iñaki", "Andrés R.", "João", "Ana 2",
                                    "François"])
def test_los_nombres_de_verdad_se_aceptan(db, nombre):
    ok, datos = unirse(db, nombre, token())

    assert ok, datos
    assert datos["nombre"] == nombre


# @scenarios un-nombre-no-se-repite
@pytest.mark.parametrize("otro", ["ANA ", "Ána", "  ana", "Ana\f", "Ana\u00a0", "\u200bAna\u200b", "A\u0301na"])
def test_un_nombre_ocupado_se_rechaza_sin_distinguir_mayusculas_acentos_ni_espacios(db, otro):
    assert unirse(db, "Ana", token())[0]

    ok, error = unirse(db, otro, token())

    assert not ok
    assert "nombre" in error
    assert contar(db, "event_players") == 1


# @scenarios un-nombre-no-se-repite, la-base-de-datos-valida-lo-que-entra
@pytest.mark.parametrize("nombre", ["\u0410na", "\u200b", "\v", "<b>", "...", "-", "Ana\u00d7", "", "x" * 31])
def test_un_nombre_vacio_largo_invisible_o_de_otro_alfabeto_se_rechaza(db, nombre):
    ok, _ = unirse(db, nombre, token())

    assert not ok, nombre
    assert contar(db, "event_players") == 0


# @scenarios un-evento-con-contrasena-solo-deja-entrar-a-quien-la-sabe
def test_con_contrasena_solo_entra_quien_la_sabe_y_un_movil_apuntado_no_la_repite(db):
    valor(db, "update public.event_editions set clave_hash = encode(sha256(convert_to('cl4ve-larga', 'UTF8')), 'hex')")
    assert estado(db)["con_clave"] is True
    assert "clave_hash" not in json.dumps(estado(db))
    tk = token()

    for mala in (None, "", "CL4VE-LARGA", "cl4ve-larga "):
        ok, error = unirse(db, "Ana", tk, mala)
        assert not ok and "contraseña" in error, mala
    assert contar(db, "event_players") == 0

    assert unirse(db, "Ana", tk, "cl4ve-larga") == (True, {"nombre": "Ana"})
    assert unirse(db, "Ana", tk) == (True, {"nombre": "Ana"}), "ya apuntado, no la vuelve a pedir"


# @scenarios un-evento-con-contrasena-solo-deja-entrar-a-quien-la-sabe
def test_con_contrasena_el_estado_no_ensena_nada_a_quien_no_la_da(db):
    valor(db, "update public.event_editions set clave_hash = encode(sha256(convert_to('cl4ve-larga', 'UTF8')), 'hex')")
    tk = token()

    for clave in (None, "mala"):
        ok, cerrado = rpc(db, "estado_del_evento", EVENTO, None, clave)
        assert ok and set(cerrado) == {"ahora", "con_clave", "bloqueado"}, cerrado
        assert cerrado["bloqueado"] is True
    assert rpc(db, "estado_del_evento", EVENTO)[1]["bloqueado"] is True, "la versión de un parámetro, también cerrada"
    abierto = rpc(db, "estado_del_evento", EVENTO, None, "cl4ve-larga")[1]
    assert abierto["bloqueado"] is False and abierto["titulo"] == "Evento de test"

    assert unirse(db, "Ana", tk, "cl4ve-larga")[0]
    dentro = rpc(db, "estado_del_evento", EVENTO, tk, None)[1]
    assert dentro["bloqueado"] is False and len(dentro["frases"]) == 3, "dentro, basta el token"


# @scenarios un-evento-con-contrasena-solo-deja-entrar-a-quien-la-sabe
def test_un_evento_sin_contrasena_no_la_pide(db):
    assert estado(db)["con_clave"] is False
    assert unirse(db, "Ana", token())[0]


# @scenarios un-movil-entra-con-un-solo-nombre
def test_un_token_apuntado_conserva_su_primer_nombre(db):
    tk = token()
    assert unirse(db, "Ana", tk)[0]

    ok, datos = unirse(db, "Bea", tk)

    assert ok
    assert datos == {"nombre": "Ana"}
    assert contar(db, "event_players") == 1


# @scenarios la-base-de-datos-valida-lo-que-entra
def test_un_evento_completo_no_admite_mas_participantes(db):
    valor(db, "insert into public.event_players (evento, nombre, clave, token) "
              "select 't', 'p' || i, 'p' || i, gen_random_uuid() from generate_series(1, 500) i")

    ok, error = unirse(db, "Ana", token())

    assert not ok and "completo" in error
    assert contar(db, "event_players") == 500


# ── Empezar ───────────────────────────────────────────────────────────────────────────────────────────────

# @scenarios el-tablero-sale-al-pulsar-empezar, el-cronometro-empieza-en-cero, una-partida-por-frase
def test_empezar_devuelve_la_frase_tapada_y_fija_la_hora_de_inicio_una_sola_vez(db):
    tk = token()
    assert unirse(db, "Ana", tk)[0]
    assert rpc(db, "mi_partida_del_evento", EVENTO, tk)[1]["partidas"] == [], "antes de pulsar no hay forma"

    ok, primera = empezar(db, tk)
    assert ok, primera
    ok, segunda = empezar(db, tk)

    assert primera["visible"] == "___ _ ___"
    assert primera["intentos"] == [] and primera["tiempo_ms"] is None
    assert segunda["empezada_en"] == primera["empezada_en"]
    assert valor(db, "select abs(extract(epoch from now() - empezada_en)) < 5 from public.event_plays") == "t"
    assert contar(db, "event_plays") == 1


# @scenarios el-tablero-sale-al-pulsar-empezar
def test_la_forma_conserva_signos_y_tildes(db):
    empezado_hace(db, 601)
    tk = participante(db, "Ana", 2)

    assert rpc(db, "mi_partida_del_evento", EVENTO, tk)[1]["partidas"][0]["visible"] == "__ ___, _______"


# @scenarios el-reloj-no-se-pausa
def test_al_volver_la_partida_sigue_con_su_hora_de_inicio_y_sus_palabras(db):
    tk = participante(db, "Ana")
    jugar(db, tk, "sacas")
    inicio = valor(db, "select empezada_en from public.event_plays")

    vuelta = rpc(db, "mi_partida_del_evento", EVENTO, tk)[1]["partidas"][0]

    assert [i["palabra"] for i in vuelta["intentos"]] == ["sacas"]
    assert valor(db, "select empezada_en from public.event_plays") == inicio
    assert vuelta["terminada_en"] is None


# @scenarios una-frase-liberada-se-juega-hasta-el-final
def test_una_frase_liberada_sigue_jugable_aunque_salgan_otras(db):
    empezado_hace(db, 3 * 600 + 60)  # mucho después de liberar la última
    tk = token()
    assert unirse(db, "Ana", tk)[0]

    assert [f["estado"] for f in estado(db)["frases"]] == ["abierta"] * 3
    assert empezar(db, tk, 1)[0]
    assert jugar(db, tk, "sacas")["visible"] == "s__ _ _a_"


# ── Jugar ─────────────────────────────────────────────────────────────────────────────────────────────────

# @scenarios cada-intento-es-una-palabra-de-cinco-letras, verde-destapa-la-letra-en-toda-la-frase, gris-si-no-esta
def test_verde_destapa_la_letra_en_toda_la_frase_y_repetida_sale_verde_las_dos_veces(db):
    tk = participante(db, "Ana")

    partida = jugar(db, tk, "sacas")

    assert partida["intentos"] == [{"palabra": "sacas", "colores": "GG.GG"}]
    assert partida["visible"] == "s__ _ _a_"
    assert partida["descubiertas"] == "as"


# @scenarios amarilla-si-ya-estaba-destapada
def test_amarilla_si_la_letra_ya_estaba_destapada(db):
    tk = participante(db, "Ana")
    jugar(db, tk, "sacas")

    partida = jugar(db, tk, "sosos")

    assert partida["intentos"][-1]["colores"] == "YGYGY"
    assert partida["visible"] == "so_ _ _a_"


# @scenarios los-acentos-no-cuentan-y-la-ene-si
def test_las_tildes_se_ignoran_y_la_ene_es_otra_letra(db):
    empezado_hace(db, 601)
    tk = participante(db, "Ana", 2)

    con_n = jugar(db, tk, "NACEN", 2)
    con_ene = jugar(db, tk, "cañón", 2)

    assert "ñ" not in con_n["descubiertas"] and "n" in con_n["descubiertas"]
    assert con_n["visible"] == "E_ a__, canc__n", "la n destapa las n y no la ñ"
    assert con_ene["visible"] == "E_ año, canc_ón", "sin tilde, la o destapa la ó"


# @scenarios una-palabra-que-no-esta-en-la-lista-no-gasta-intento
@pytest.mark.parametrize("palabra", ["aeiou", "zzzzz", "solym"])
def test_una_palabra_que_no_esta_en_la_lista_se_rechaza_sin_gastar_intento(db, palabra):
    tk = participante(db, "Ana")

    ok, error = intentar(db, tk, palabra)

    assert not ok and "no está en la lista" in error
    assert contar(db, "event_guesses") == 0
    assert jugar(db, tk, "sacas")["intentos"][0]["palabra"] == "sacas", "el intento 1 sigue libre"


# @scenarios se-gana-al-destapar-todas-las-letras
def test_destapar_todas_las_letras_resuelve_con_la_hora_del_servidor(db):
    tk = participante(db, "Ana")
    jugar(db, tk, "salmo")

    partida = jugar(db, tk, "RAYOS")

    assert partida["resuelta"] is True
    assert partida["visible"] == "sol y mar"
    assert partida["terminada_en"] is not None and partida["tiempo_ms"] >= 0
    assert partida["intentos"][-1]["colores"] == "GYGYY"
    assert "puesto" not in partida
    assert intentar(db, tk, "sacas")[0] is False, "resuelta, no admite más palabras"


# @scenarios cinco-palabras-sin-destaparla-se-pierde
def test_la_quinta_palabra_sin_destaparla_termina_sin_resolver(db):
    tk = participante(db, "Ana")
    for palabra in ["tunde", "pique", "chufa", "nieve"]:
        assert jugar(db, tk, palabra)["terminada_en"] is None

    quinta = jugar(db, tk, "sacas")
    sexta_ok, _ = intentar(db, tk, "salmo")

    assert quinta["terminada_en"] is not None and quinta["resuelta"] is False
    assert not sexta_ok
    assert contar(db, "event_guesses") == 5


# @scenarios la-solucion-no-viaja-al-movil
def test_ninguna_funcion_devuelve_la_frase_entera_antes_de_terminar(db):
    tk = token()
    salidas = [unirse(db, "Ana", tk)[1], empezar(db, tk)[1], intentar(db, tk, "sacas")[1],
               rpc(db, "mi_partida_del_evento", EVENTO, tk)[1], estado(db)]

    texto = json.dumps(salidas, ensure_ascii=False).lower()

    assert "sol y mar" not in texto
    assert all("solucion" not in f for f in estado(db)["frases"])


# @scenarios la-solucion-se-ve-al-terminar-el-evento
def test_la_solucion_aparece_en_el_estado_al_terminar_el_evento(db):
    tk = participante(db, "Ana")
    jugar(db, tk, "salmo")
    jugar(db, tk, "rayos")
    assert "solucion" not in estado(db)["frases"][0], "resuelta pero sin terminar el evento: no se ve"

    terminado(db)

    assert [f.get("solucion") for f in estado(db)["frases"]] == ["sol y mar", "El año, canción", "Más vale tarde"]


# @scenarios al-terminar-el-evento-no-se-admiten-palabras
def test_con_el_evento_terminado_se_rechazan_palabras_y_la_partida_a_medias_no_termina(db):
    tk = participante(db, "Ana")
    terminado(db)

    ok, error = intentar(db, tk, "sacas")

    assert not ok and "no está abierta" in error
    assert valor(db, "select resuelta, terminada_en is null from public.event_plays") == "f|t"
    assert not empezar(db, token(), 1)[0]


# @scenarios durante-el-evento-no-se-ve-la-posicion
def test_el_ranking_se_rechaza_mientras_el_evento_no_ha_terminado(db):
    tk = participante(db, "Ana")
    jugar(db, tk, "salmo")
    jugar(db, tk, "rayos")
    empezado_hace(db, 99_999)

    ok, error = rpc(db, "ranking_del_evento", EVENTO)

    assert not ok and "al terminar" in error
    texto = json.dumps([estado(db), rpc(db, "mi_partida_del_evento", EVENTO, tk)[1]])
    assert "puesto" not in texto


# ── Reenvíos y validación ─────────────────────────────────────────────────────────────────────────────────

# @scenarios si-el-servidor-no-responde-el-intento-no-se-pierde
def test_reenviar_una_palabra_que_ya_llego_no_gasta_otra(db):
    tk = participante(db, "Ana")
    primero = intentar(db, tk, "sacas", numero=1)[1]

    ok, reenvio = intentar(db, tk, "SACAS", numero=1)

    assert ok, reenvio
    assert reenvio == primero
    assert contar(db, "event_guesses") == 1


# @scenarios si-el-servidor-no-responde-el-intento-no-se-pierde, se-gana-al-destapar-todas-las-letras
def test_reenviar_la_palabra_que_resolvio_devuelve_la_partida_resuelta(db):
    tk = participante(db, "Ana")
    jugar(db, tk, "salmo")
    assert intentar(db, tk, "rayos", numero=2)[1]["resuelta"]

    ok, reenvio = intentar(db, tk, "rayos", numero=2)

    assert ok and reenvio["resuelta"] and reenvio["terminada_en"]


# @scenarios la-base-de-datos-valida-lo-que-entra
@pytest.mark.parametrize("caso", ["token-desconocido", "frase-no-liberada", "sin-empezar", "letras-de-mas",
                                  "letras-de-menos", "caracteres-raros", "fuera-de-orden", "numero-repetido-distinto",
                                  "sin-numero"])
def test_la_base_de_datos_rechaza_lo_que_no_vale_sin_guardar_nada(db, caso):
    tk = participante(db, "Ana")
    assert intentar(db, tk, "sacas")[0]
    antes = (contar(db, "event_players"), contar(db, "event_plays"), contar(db, "event_guesses"))
    otro = token()

    ok, _ = {
        "token-desconocido": lambda: intentar(db, otro, "salmo", numero=1),
        "frase-no-liberada": lambda: empezar(db, tk, 2),
        "sin-empezar": lambda: (unirse(db, "Bea", otro), intentar(db, otro, "salmo", numero=1))[1],
        "letras-de-mas": lambda: intentar(db, tk, "salmos"),
        "letras-de-menos": lambda: intentar(db, tk, "salm"),
        "caracteres-raros": lambda: intentar(db, tk, "salm0"),
        "fuera-de-orden": lambda: intentar(db, tk, "salmo", numero=4),
        "numero-repetido-distinto": lambda: intentar(db, tk, "salmo", numero=1),
        "sin-numero": lambda: rpc(db, "intentar_palabra", EVENTO, tk, 1, "salmo", None),
    }[caso]()

    assert not ok
    despues = (contar(db, "event_players"), contar(db, "event_plays"), contar(db, "event_guesses"))
    if caso == "sin-empezar":
        despues = (despues[0] - 1, *despues[1:])  # Bea sí se apuntó; lo que no entra es su palabra
    assert despues == antes


# @scenarios la-web-no-toca-las-tablas-del-evento
@pytest.mark.parametrize("tabla", TABLAS)
def test_la_clave_publica_no_lee_ni_escribe_las_tablas_del_evento(db, tabla):
    for consulta in (f"select * from public.{tabla}", f"delete from public.{tabla}", f"truncate public.{tabla}"):
        resultado = db(f"begin; {consulta}; rollback;", rol="anon")
        assert resultado.returncode != 0, consulta
        assert "permission denied" in resultado.stderr


# @scenarios la-web-no-toca-las-tablas-del-evento
@pytest.mark.parametrize("consulta", [
    "insert into public.event_plays (jugador, orden, empezada_en) values (1, 1, now())",
    "select public.evento_colores('abc', '', 'abcde')",
    "select public.evento_visible('sol y mar', 'solymar')",
    "select public.evento_con_pin('t', 'x')",
    "select nextval('public.event_players_id_seq')",
])
def test_la_clave_publica_no_inserta_ni_llama_a_los_ayudantes(db, consulta):
    assert db(consulta, rol="anon").returncode != 0
