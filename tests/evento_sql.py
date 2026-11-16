"""Ayudas para probar el juego del evento contra un Postgres local (`tests/postgres_local.py`).

Un evento sintético `t` con tres frases que se liberan cada 10 minutos. Las funciones se llaman con el rol `anon`, como
las llama la web; el tiempo se simula moviendo `empieza_en` y las horas de las partidas con el rol del dueño.
"""

from __future__ import annotations

import json
import uuid

EVENTO = "t"
PIN = "pin-de-test"
FRASES = {1: "sol y mar", 2: "El año, canción", 3: "Más vale tarde"}
INTERVALO = 10

SEMILLA = (
    "insert into public.event_editions (id, titulo, intervalo_minutos, pin_hash) values "
    f"('{EVENTO}', 'Evento de test', {INTERVALO}, encode(sha256(convert_to('{PIN}', 'UTF8')), 'hex'));\n"
    "insert into public.event_phrases (evento, orden, frase) values "
    + ", ".join(f"('{EVENTO}', {orden}, '{frase}')" for orden, frase in FRASES.items())
    + ";"
)


def token() -> str:
    return str(uuid.uuid4())


def literal(valor) -> str:
    if valor is None:
        return "null"
    if isinstance(valor, int):
        return str(valor)
    return "$v$" + str(valor) + "$v$"


def rpc(db, funcion: str, *argumentos):
    """Llama a una función como la clave pública. Devuelve `(ok, json_o_error)`."""
    lista = ", ".join(literal(a) for a in argumentos)
    resultado = db(f"select public.{funcion}({lista})", rol="anon")
    if resultado.returncode != 0:
        return False, resultado.stderr
    salida = resultado.stdout.strip()
    return True, json.loads(salida) if salida else None


def valor(db, consulta: str) -> str:
    resultado = db(consulta)
    assert resultado.returncode == 0, resultado.stderr
    return resultado.stdout.strip()


def reiniciar(db, intervalo: int = INTERVALO) -> None:
    valor(db, "truncate public.event_players restart identity cascade; "
              f"update public.event_editions set empieza_en = null, terminado_en = null, clave_hash = null, "
              f"intervalo_minutos = {intervalo} "
              f"where id = '{EVENTO}'")


def empezado_hace(db, segundos: float) -> None:
    """El evento empezó hace tantos segundos: con 10 minutos, 60 libera la frase 1 y 601 también la 2."""
    valor(db, f"update public.event_editions set empieza_en = now() - make_interval(secs => {segundos}) "
              f"where id = '{EVENTO}'")


def unirse(db, nombre: str, tk: str, clave: str | None = None):
    return rpc(db, "unirse_al_evento", EVENTO, nombre, tk, clave)


def empezar(db, tk: str, orden: int = 1):
    return rpc(db, "empezar_frase", EVENTO, tk, orden)


def intentar(db, tk: str, palabra: str, orden: int = 1, numero: int | None = None):
    """Una palabra. Sin `numero`, el siguiente de la partida, como lo calcula el móvil."""
    if numero is None:
        hechos = valor(db, "select coalesce(max(pl.intentos), 0) from public.event_plays pl join public.event_players p "
                           f"on p.id = pl.jugador where p.token::text = '{tk}' and pl.orden = {orden}")
        numero = int(hechos or 0) + 1
    return rpc(db, "intentar_palabra", EVENTO, tk, orden, palabra, numero)


def terminado(db) -> None:
    """El evento terminado hace un segundo."""
    valor(db, "update public.event_editions set terminado_en = now() - interval '1 second' "
              f"where id = '{EVENTO}'")


def estado(db):
    ok, datos = rpc(db, "estado_del_evento", EVENTO)
    assert ok, datos
    return datos


def participante(db, nombre: str, orden: int = 1) -> str:
    """Un participante apuntado con la frase `orden` empezada."""
    tk = token()
    assert unirse(db, nombre, tk)[0]
    ok, datos = empezar(db, tk, orden)
    assert ok, datos
    return tk


def fijar_tiempo(db, tk: str, orden: int, milisegundos: int) -> None:
    """Deja la partida resuelta con un tiempo exacto, para probar el ranking sin esperar."""
    valor(db, "update public.event_plays pl set terminada_en = pl.empezada_en + make_interval(secs => "
              f"{milisegundos} / 1000.0), resuelta = true from public.event_players p "
              f"where p.id = pl.jugador and p.token = '{tk}' and pl.orden = {orden}")
