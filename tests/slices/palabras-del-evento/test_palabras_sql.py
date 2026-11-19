"""Las funciones del juego del evento que llama el móvil, de `palabras-del-evento`, contra un Postgres **local**.

Cambio: `feat-palabras-del-evento`. **No se toca producción**: `tests/postgres_local.py` levanta un Postgres
desechable, aplica las migraciones del repositorio tal cual (también el diccionario) y lo ataca con los roles de
Supabase. Participantes, grupos y palabras inventados.

Reglas del Wordle: palabras válidas de cinco letras, seis intentos; verde en su sitio, amarilla en otro sitio, gris si
no está (o no quedan más como ella).
"""

from __future__ import annotations

import json

import pytest

from tests.evento_sql import (
    EVENTO, GRUPOS, LISTA, PALABRAS, SEMILLA, activado, elegir, empezar, estado, hasta_la_palabra, jugador, orden_de,
    palabra_en, panel, probar, reiniciar, rpc, terminado, token, valor,
)
from tests.postgres_local import postgres_con_migraciones, sin_postgres

pytestmark = sin_postgres

TABLAS = ["event_editions", "event_targets", "event_roster", "event_rounds", "event_tries", "event_words"]


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


def jugando(db, nombre="Ana", orden=1):
    """Un móvil con nombre y la palabra `orden` empezada, con el evento activado."""
    activado(db)
    tk = jugador(db, nombre)
    for o in range(1, orden):
        assert empezar(db, tk, o)[0]
        for _ in range(6):
            probar(db, tk, "tunde", o)
    ok, ronda = empezar(db, tk, orden)
    assert ok, ronda
    return tk


def en_la_palabra(db, orden, nombre="Ana"):
    """Un móvil con la palabra `orden` **del evento** empezada, esté en el número que le toque. Devuelve el token y
    ese número."""
    activado(db)
    tk = jugador(db, nombre)
    return tk, hasta_la_palabra(db, tk, orden)


def intento(db, tk, palabra, orden=1):
    ok, ronda = probar(db, tk, palabra, orden)
    assert ok, ronda
    return ronda


# ── Antes de activar ─────────────────────────────────────────────────────────────────────────────────────

# @scenarios antes-de-activar-solo-se-ve-la-espera
def test_antes_de_activar_el_estado_solo_dice_que_no_esta_activo(db):
    datos = estado(db)

    assert set(datos) == {"ahora", "activo", "terminado"}
    assert datos["activo"] is False and datos["terminado"] is False
    assert not rpc(db, "nombres_del_evento", EVENTO)[0], "la lista no sale antes de activar"
    ok, error = elegir(db, "Ana", token())
    assert not ok and "no está activo" in error


# @scenarios la-espera-pasa-sola-al-juego
def test_activado_el_estado_trae_titulo_y_cuantas_palabras_hay_sin_soluciones(db):
    activado(db)

    datos = estado(db)

    assert datos["activo"] is True and datos["titulo"] == "Evento de test" and datos["total"] == 3
    assert datos["soluciones"] is None


# @scenarios el-tiempo-cuenta-y-se-dice
def test_activado_el_estado_dice_los_puntos_por_acertar_y_por_rapidez_y_los_segundos_por_intento(db):
    assert "segundos_por_intento" not in estado(db), "antes de activar, nada"
    assert "puntos_por_acierto" not in estado(db)
    activado(db)
    valor(db, f"update public.event_editions set segundos_por_intento = 45 where id = '{EVENTO}'")

    datos = estado(db)
    assert (datos["segundos_por_intento"], datos["puntos_por_acierto"], datos["puntos_por_rapidez"]) == (45, 10, 5)


# ── El nombre ────────────────────────────────────────────────────────────────────────────────────────────

# @scenarios se-elige-el-nombre-de-la-lista
def test_la_lista_trae_los_nombres_y_si_estan_libres_y_se_elige_sin_mayusculas_ni_tildes(db):
    activado(db)

    ok, datos = elegir(db, "  iñigo perez ", token())
    assert ok, datos
    assert datos == {"nombre": "Íñigo Pérez"}

    ok, nombres = rpc(db, "nombres_del_evento", EVENTO)
    assert ok, nombres
    assert {n["nombre"]: n["libre"] for n in nombres}["Íñigo Pérez"] is False
    assert {n["nombre"]: n["libre"] for n in nombres}["Ana"] is True
    assert len(nombres) == 6


# @scenarios un-nombre-que-no-esta-en-la-lista-no-entra
@pytest.mark.parametrize("nombre", ["Zoe", "", "Ana Rojo", None])
def test_un_nombre_que_no_esta_en_la_lista_se_rechaza(db, nombre):
    activado(db)

    ok, error = elegir(db, nombre, token())

    assert not ok and "no está en la lista" in error
    assert valor(db, "select count(*) from public.event_roster where token is not null") == "0"


# @scenarios un-nombre-elegido-no-lo-coge-otro-movil
def test_un_nombre_elegido_no_lo_coge_otro_movil(db):
    activado(db)
    primero = jugador(db, "Ana")

    ok, error = elegir(db, "ANA", token())

    assert not ok and "ya está elegido" in error
    assert valor(db, "select token::text from public.event_roster where nombre = 'Ana'") == primero


# @scenarios el-mismo-movil-recupera-su-nombre
def test_el_mismo_movil_conserva_su_nombre_y_no_coge_otro(db):
    activado(db)
    tk = jugador(db, "Ana")

    assert elegir(db, "Ana", tk) == (True, {"nombre": "Ana"})
    assert elegir(db, "Bea", tk) == (True, {"nombre": "Ana"}), "un móvil, un nombre"
    assert rpc(db, "mi_juego", EVENTO, tk)[1] == {"nombre": "Ana", "rondas": []}
    assert valor(db, "select token is null from public.event_roster where nombre = 'Bea'") == "t"


# @scenarios el-grupo-no-viaja-al-movil
def test_ninguna_respuesta_del_movil_lleva_el_grupo(db):
    tk = jugando(db)
    intento(db, tk, "sacos")

    respuestas = [estado(db), rpc(db, "nombres_del_evento", EVENTO)[1], rpc(db, "mi_juego", EVENTO, tk)[1],
                  elegir(db, "Ana", tk)[1]]

    texto = json.dumps(respuestas, ensure_ascii=False)
    assert "grupo" not in texto
    assert not any(grupo in texto for grupo in GRUPOS)


# ── Jugar ────────────────────────────────────────────────────────────────────────────────────────────────

# @scenarios el-cronometro-de-cada-palabra-empieza-al-pulsar
def test_empezar_fija_la_hora_de_inicio_una_sola_vez(db):
    activado(db)
    tk = jugador(db, "Ana")

    ok, ronda = empezar(db, tk, 1)
    assert ok, ronda
    assert ronda["intentos"] == [] and ronda["terminada_en"] is None and ronda["tiempo_ms"] is None
    assert valor(db, "select abs(extract(epoch from now() - empezada_en)) < 5 from public.event_rounds") == "t"

    valor(db, "update public.event_rounds set empezada_en = empezada_en - interval '42 seconds'")
    antes = valor(db, "select empezada_en::text from public.event_rounds")
    assert empezar(db, tk, 1)[0]
    assert valor(db, "select empezada_en::text from public.event_rounds") == antes, "volver a pulsar no reinicia"


# @scenarios el-cronometro-de-cada-palabra-empieza-al-pulsar, el-reloj-no-se-pausa
def test_el_tiempo_va_de_empezar_a_resolver_con_la_hora_del_servidor(db):
    tk = jugando(db)
    valor(db, "update public.event_rounds set empezada_en = now() - interval '73.5 seconds'")

    ronda = intento(db, tk, palabra_en(db, tk, 1))

    assert ronda["resuelta"] is True
    assert 73_000 <= ronda["tiempo_ms"] < 80_000


# @scenarios las-palabras-se-juegan-en-orden
def test_la_siguiente_palabra_solo_con_la_anterior_terminada(db):
    tk = jugando(db)

    ok, error = empezar(db, tk, 2)
    assert not ok and "palabra anterior" in error

    intento(db, tk, palabra_en(db, tk, 1))
    assert empezar(db, tk, 2)[0]
    assert not empezar(db, tk, 4)[0], "no hay palabra 4"


def jugar_las_tres(db, tk):
    """Empieza y termina las tres palabras del participante por sus números, y apunta qué palabra del evento se guardó
    detrás de cada uno."""
    jugadas = []
    for posicion in (1, 2, 3):
        ok, ronda = empezar(db, tk, posicion)
        assert ok, ronda
        assert ronda["orden"] == posicion, "la ronda viaja con el número que ve el participante"
        jugadas.append(int(valor(db, "select r.orden from public.event_rounds r join public.event_roster p on "
                                     f"p.id = r.jugador where p.token::text = '{tk}' and r.terminada_en is null")))
        valor(db, "update public.event_rounds set terminada_en = now() where terminada_en is null")
    return jugadas


# @scenarios cada-participante-juega-las-palabras-en-su-orden
def test_cada_participante_juega_todas_las_palabras_en_su_propio_orden(db):
    activado(db)

    jugadas = {nombre: jugar_las_tres(db, jugador(db, nombre)) for nombre, _ in LISTA}

    for nombre, orden in jugadas.items():
        assert sorted(orden) == [1, 2, 3], f"{nombre} juega cada palabra una vez"
    assert len({tuple(orden) for orden in jugadas.values()}) > 1, "no todos en el mismo orden"


# @scenarios el-orden-de-cada-uno-no-cambia
def test_el_orden_de_un_participante_es_el_mismo_al_volver(db):
    activado(db)
    tk = jugador(db, "Ana")
    primera_vez = jugar_las_tres(db, tk)

    valor(db, "truncate public.event_rounds cascade")
    assert rpc(db, "mi_juego", EVENTO, tk)[1]["nombre"] == "Ana", "recarga: el móvil conserva su nombre"

    assert jugar_las_tres(db, tk) == primera_vez


# @scenarios el-orden-no-viaja-al-movil
def test_el_orden_lleva_un_secreto_del_servidor_y_no_sale_solo_de_los_ids(db):
    """El repositorio es público y los ids de la lista, correlativos: con la fórmula y los ids no basta para saber el
    orden de nadie. Con otra huella de PIN, el orden de alguien cambia."""
    activado(db)
    tks = [jugador(db, nombre) for nombre, _ in LISTA]
    antes = [orden_de(db, tk) for tk in tks]

    valor(db, "update public.event_editions set pin_hash = encode(sha256(convert_to('otro', 'UTF8')), 'hex') "
              f"where id = '{EVENTO}'")
    try:
        despues = [orden_de(db, tk) for tk in tks]
    finally:
        valor(db, "update public.event_editions set pin_hash = encode(sha256(convert_to('1234', 'UTF8')), 'hex') "
                  f"where id = '{EVENTO}'")

    assert despues != antes


# @scenarios el-orden-no-viaja-al-movil
def test_las_respuestas_solo_llevan_el_numero_que_ve_el_participante(db):
    activado(db)
    barajado = next((tk for tk in (jugador(db, nombre) for nombre, _ in LISTA) if orden_de(db, tk)[0] != 1), None)
    assert barajado, "algún participante tiene otra palabra detrás de su número 1"
    claves = {"orden", "empezada_en", "terminada_en", "resuelta", "tiempo_ms", "intentos"}

    ok, empezada = empezar(db, barajado, 1)
    assert ok, empezada
    ok, probada = probar(db, barajado, "tunde", 1)
    assert ok, probada
    ok, mio = rpc(db, "mi_juego", EVENTO, barajado)
    assert ok, mio

    assert set(mio) == {"nombre", "rondas"}, "con el evento en marcha, sin palabras"
    for ronda in (empezada, probada, *mio["rondas"]):
        assert set(ronda) == claves
        assert ronda["orden"] == 1


# @scenarios los-puntos-comparan-la-misma-palabra
def test_compiten_por_una_palabra_quienes_la_jugaron_aunque_fuera_en_otro_numero(db):
    activado(db)
    numeros = {}
    for nombre in ("Ana", "Bea", "Cris", "Dani", "Íñigo Pérez", "Eva"):
        tk = jugador(db, nombre)
        numeros.setdefault(orden_de(db, tk).index(1) + 1, (nombre, tk))
    assert len(numeros) > 1, "a dos participantes la palabra 1 les toca en números distintos"
    (rapido, tk_rapido), (lento, tk_lento) = list(numeros.values())[:2]
    for tk, segundos in ((tk_rapido, 20), (tk_lento, 50)):
        posicion = hasta_la_palabra(db, tk, 1)
        assert intento(db, tk, "casas", posicion)["resuelta"] is True
        valor(db, "update public.event_rounds set empezada_en = terminada_en - make_interval(secs => "
                  f"{segundos}) where orden = 1 and jugador = (select id from public.event_roster where "
                  f"token::text = '{tk}')")
    terminado(db)

    jugadores = {j["nombre"]: j for j in panel(db)["jugadores"]}

    palabra_1 = {nombre: next(p for p in jugadores[nombre]["palabras"] if p["orden"] == 1) for nombre in (rapido, lento)}
    assert (palabra_1[rapido]["puntos"], palabra_1[lento]["puntos"]) == (15, 10)


# @scenarios cada-palabra-tiene-seis-intentos-de-cinco-letras
def test_seis_intentos_sin_acertar_terminan_la_palabra_sin_resolver(db):
    tk = jugando(db)
    for palabra in ["tunde", "pique", "chufa", "nieve", "bucle"]:
        assert intento(db, tk, palabra)["terminada_en"] is None

    ronda = intento(db, tk, "letra")

    assert ronda["terminada_en"] is not None and ronda["resuelta"] is False and len(ronda["intentos"]) == 6
    ok, error = probar(db, tk, "casas", 1, 7)
    assert not ok


# @scenarios cada-palabra-tiene-seis-intentos-de-cinco-letras
@pytest.mark.parametrize("palabra", ["casa", "casass", "cas4s", ""])
def test_una_palabra_que_no_tiene_cinco_letras_se_rechaza(db, palabra):
    tk = jugando(db)

    ok, error = probar(db, tk, palabra)

    assert not ok and "cinco letras" in error


# @scenarios una-palabra-que-no-esta-en-la-lista-no-gasta-intento
def test_una_palabra_que_no_esta_en_la_lista_no_gasta_intento(db):
    tk = jugando(db)

    ok, error = probar(db, tk, "zzzzz")

    assert not ok and "no está en la lista" in error
    assert valor(db, "select intentos from public.event_rounds") == "0"


# @scenarios una-palabra-que-no-esta-en-la-lista-no-gasta-intento, la-solucion-no-viaja-al-movil
def test_una_solucion_fuera_del_diccionario_solo_vale_en_su_palabra(db):
    valor(db, f"update public.event_targets set palabra = 'zzqxk' where evento = '{EVENTO}' and orden = 2")
    try:
        ana, en_la_1 = en_la_palabra(db, 1, "Ana")
        ok, error = probar(db, ana, "zzqxk", en_la_1)
        assert not ok and "no está en la lista" in error, "en la palabra 1 no delata la solución de la 2"

        bea, en_la_2 = en_la_palabra(db, 2, "Bea")
        assert intento(db, bea, "zzqxk", en_la_2)["resuelta"] is True, "en su palabra se puede resolver"
    finally:
        valor(db, f"update public.event_targets set palabra = 'perro' where evento = '{EVENTO}' and orden = 2")


# @scenarios los-colores-son-los-del-wordle
@pytest.mark.parametrize("palabra, colores", [
    ("casas", "GGGGG"),
    ("cazas", "GG.GG"),   # en su sitio, verde; la z no está
    ("salas", "YG.GG"),   # la s de delante está en la palabra, en otro sitio
    ("tunde", "....."),
    ("Cásas", "GGGGG"),   # las tildes no cuentan
])
def test_verde_en_su_sitio_amarilla_en_otro_y_gris_si_no_esta(db, palabra, colores):
    tk, posicion = en_la_palabra(db, 1)

    ronda = intento(db, tk, palabra, posicion)

    assert ronda["intentos"][-1]["colores"] == colores


# @scenarios una-letra-repetida-se-colorea-como-en-el-wordle
@pytest.mark.parametrize("orden, palabra, colores", [
    (1, "sacos", "YGY.G"),   # casas: la última s verde, la primera amarilla (quedan s sin verde)
    (2, "error", "YYGY."),   # perro: la tercera r verde, la segunda amarilla, y la última gris (no quedan más r)
    (3, "pizza", "YYY.Y"),   # lapiz: una sola z, así que la segunda sale gris
])
def test_una_letra_repetida_solo_sale_tantas_veces_como_esta(db, orden, palabra, colores):
    tk, posicion = en_la_palabra(db, orden)

    ronda = intento(db, tk, palabra, posicion)

    assert ronda["intentos"][-1]["colores"] == colores


# @scenarios se-gana-con-cinco-verdes
def test_cinco_verdes_resuelven_la_palabra(db):
    tk, posicion = en_la_palabra(db, 1)
    intento(db, tk, "sacos", posicion)

    ronda = intento(db, tk, "casas", posicion)

    assert ronda["resuelta"] is True and ronda["terminada_en"] is not None
    ok, _ = probar(db, tk, "casas", posicion)
    assert not ok, "terminada, no admite más"


# @scenarios la-solucion-no-viaja-al-movil
def test_la_solucion_no_sale_aunque_se_falle_hasta_terminar_el_evento(db):
    tk = jugando(db)
    for palabra in ["tunde", "pique", "chufa", "nieve", "bucle", "letra"]:
        intento(db, tk, palabra)

    texto = json.dumps([estado(db), rpc(db, "mi_juego", EVENTO, tk)[1]], ensure_ascii=False)

    assert PALABRAS[1] not in texto
    assert not any(palabra in texto for palabra in PALABRAS.values())


# @scenarios si-el-servidor-no-responde-el-intento-no-se-pierde
def test_reenviar_un_intento_que_ya_llego_no_gasta_otro(db):
    tk = jugando(db)
    assert probar(db, tk, "sacos", 1, 1)[0]

    ok, ronda = probar(db, tk, "sacos", 1, 1)

    assert ok, ronda
    assert len(ronda["intentos"]) == 1
    assert not probar(db, tk, "salas", 1, 1)[0], "otro intento con el mismo número no vale"
    assert not probar(db, tk, "salas", 1, 3)[0], "ni uno que se salta un número"


# ── Al terminar ──────────────────────────────────────────────────────────────────────────────────────────

# @scenarios al-terminar-el-evento-no-se-admiten-palabras
def test_con_el_evento_terminado_no_se_empieza_ni_se_prueba_nada(db):
    tk = jugando(db)
    terminado(db)

    ok, error = probar(db, tk, "casas")
    assert not ok and "terminado" in error
    assert not empezar(db, tk, 2)[0]
    assert not elegir(db, "Bea", token())[0], "ni se eligen nombres"
    assert not rpc(db, "nombres_del_evento", EVENTO)[0], "ni se entrega la lista: son nombres reales"
    assert valor(db, "select terminada_en is null from public.event_rounds") == "t"


# @scenarios al-terminar-el-evento-se-ven-las-soluciones
def test_terminado_el_evento_el_estado_trae_las_soluciones(db):
    terminado(db)

    datos = estado(db)

    assert datos["terminado"] is True and datos["activo"] is False
    assert [s["palabra"] for s in datos["soluciones"]] == list(PALABRAS.values())


# @scenarios al-terminar-el-evento-se-ven-las-soluciones
def test_terminado_el_evento_cada_uno_recibe_sus_palabras_en_su_orden(db):
    activado(db)
    tk = next((tk for tk in (jugador(db, nombre) for nombre, _ in LISTA) if orden_de(db, tk) != [1, 2, 3]), None)
    assert tk, "algún participante tiene un orden que no es el del evento"
    suyas = [PALABRAS[orden] for orden in orden_de(db, tk)]
    assert "palabras" not in rpc(db, "mi_juego", EVENTO, tk)[1], "en marcha, no"

    terminado(db)

    assert rpc(db, "mi_juego", EVENTO, tk)[1]["palabras"] == suyas


# ── La web no toca las tablas ────────────────────────────────────────────────────────────────────────────

# @scenarios la-web-no-toca-las-tablas-del-evento
@pytest.mark.parametrize("tabla", TABLAS)
def test_la_clave_publica_no_lee_ni_escribe_las_tablas_del_evento(db, tabla):
    for consulta in (f"select * from public.{tabla}", f"delete from public.{tabla}", f"truncate public.{tabla}"):
        resultado = db(f"begin; {consulta}; rollback;", rol="anon")
        assert resultado.returncode != 0, consulta
        assert "permission denied" in resultado.stderr


# @scenarios la-web-no-toca-las-tablas-del-evento
@pytest.mark.parametrize("consulta", [
    "insert into public.event_rounds (jugador, orden, empezada_en) values (1, 1, now())",
    "select public.evento_wordle('casas', 'sacos')",
    "select public.evento_pin('t', '1234')",
    "select * from public.evento_puntos('t')",
    # Diría qué palabra del evento hay detrás de cada número. Se le niega la función, no solo las tablas que lee.
    "select public.evento_orden_de(1) /* función */",
    "select nextval('public.event_roster_id_seq')",
    # El juego de frases ya no se llama desde la web.
    "select public.estado_del_evento('t')",
    "select public.unirse_al_evento('t', 'Ana', gen_random_uuid(), null)",
])
def test_la_clave_publica_no_llama_a_los_ayudantes_ni_al_juego_de_frases(db, consulta):
    resultado = db(consulta, rol="anon")
    assert resultado.returncode != 0
    assert "permission denied" in resultado.stderr
    if "/* función */" in consulta:
        assert "permission denied for function" in resultado.stderr
