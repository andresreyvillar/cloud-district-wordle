"""Ayudas para probar el juego del evento contra un Postgres local (`tests/postgres_local.py`).

Un evento sintético `t` con tres palabras y una lista de participantes **inventados** en tres grupos. Las funciones se
llaman con el rol `anon`, como las llama la web; el tiempo se simula moviendo las horas con el rol del dueño.
"""

from __future__ import annotations

import json
import uuid

EVENTO = "t"
PIN = "1234"
PALABRAS = {1: "casas", 2: "perro", 3: "lapiz"}
LISTA = [("Ana", "Rojo"), ("Bea", "Rojo"), ("Cris", "Azul"), ("Dani", "Azul"), ("Íñigo Pérez", "Verde"),
         ("Eva", "Verde")]
GRUPOS = sorted({grupo for _, grupo in LISTA})

SEMILLA = (
    "insert into public.event_editions (id, titulo, pin_hash) values "
    f"('{EVENTO}', 'Evento de test', encode(sha256(convert_to('{PIN}', 'UTF8')), 'hex'));\n"
    "insert into public.event_targets (evento, orden, palabra) values "
    + ", ".join(f"('{EVENTO}', {orden}, '{palabra}')" for orden, palabra in PALABRAS.items())
    + ";\ninsert into public.event_roster (evento, nombre, grupo) values "
    + ", ".join(f"('{EVENTO}', '{nombre}', '{grupo}')" for nombre, grupo in LISTA)
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


def reiniciar(db) -> None:
    valor(db, "truncate public.event_rounds cascade; "
              f"update public.event_roster set token = null, elegido_en = null where evento = '{EVENTO}'; "
              "update public.event_editions set empieza_en = null, terminado_en = null, pin_fallos = 0, "
              f"pin_bloqueado_hasta = null, segundos_por_intento = 30 where id = '{EVENTO}'")


def activado(db) -> None:
    valor(db, f"update public.event_editions set empieza_en = now() - interval '1 second' where id = '{EVENTO}'")


def terminado(db) -> None:
    """El evento terminado hace un segundo."""
    valor(db, "update public.event_editions set empieza_en = coalesce(empieza_en, now() - interval '1 hour'), "
              f"terminado_en = now() - interval '1 second' where id = '{EVENTO}'")


def elegir(db, nombre: str, tk: str):
    return rpc(db, "elegir_nombre", EVENTO, nombre, tk)


def jugador(db, nombre: str) -> str:
    """Un móvil que ya ha elegido ese nombre (con el evento activado)."""
    tk = token()
    ok, datos = elegir(db, nombre, tk)
    assert ok, datos
    return tk


def empezar(db, tk: str, orden: int = 1):
    return rpc(db, "empezar_palabra", EVENTO, tk, orden)


def probar(db, tk: str, palabra: str, orden: int = 1, numero: int | None = None):
    """Un intento. Sin `numero`, el siguiente de la ronda, como lo calcula el móvil."""
    if numero is None:
        hechos = valor(db, "select coalesce(max(r.intentos), 0) from public.event_rounds r join public.event_roster p "
                           f"on p.id = r.jugador where p.token::text = '{tk}' "
                           f"and r.orden = (public.evento_orden_de(p.id))[{orden}]")
        numero = int(hechos or 0) + 1
    return rpc(db, "probar_palabra", EVENTO, tk, orden, palabra, numero)


def orden_de(db, tk: str) -> list[int]:
    """Qué palabra del evento (su `orden` en `event_targets`) hay detrás de cada número que ve el participante."""
    texto = valor(db, "select array_to_json(public.evento_orden_de(id)) from public.event_roster "
                      f"where token::text = '{tk}'")
    return json.loads(texto)


def palabra_en(db, tk: str, posicion: int) -> str:
    """La solución de la palabra que el participante ve con ese número."""
    return PALABRAS[orden_de(db, tk)[posicion - 1]]


def hasta_la_palabra(db, tk: str, orden: int) -> int:
    """Deja empezada la palabra `orden` del evento, con las de antes en su orden ya terminadas. Devuelve su número."""
    posicion = orden_de(db, tk).index(orden) + 1
    for anterior in range(1, posicion):
        ok, ronda = empezar(db, tk, anterior)
        assert ok, ronda
        valor(db, "update public.event_rounds set terminada_en = now() where terminada_en is null and jugador = "
                  f"(select id from public.event_roster where token::text = '{tk}')")
    ok, ronda = empezar(db, tk, posicion)
    assert ok, ronda
    return posicion


def estado(db):
    ok, datos = rpc(db, "estado_del_juego", EVENTO)
    assert ok, datos
    return datos


def panel(db, pin: str = PIN):
    ok, datos = rpc(db, "panel_del_evento", EVENTO, pin)
    assert ok, datos
    return datos


def fijar(db, nombre: str, orden: int, segundos: float, intentos: int, resuelta: bool = True) -> None:
    """Deja jugada una palabra con un tiempo y unos intentos exactos, para probar los puntos sin esperar."""
    valor(db, "insert into public.event_rounds (jugador, orden, empezada_en, terminada_en, resuelta, intentos) "
              f"select id, {orden}, now() - interval '1 hour', now() - interval '1 hour' + make_interval(secs => "
              f"{segundos}), {str(resuelta).lower()}, {intentos} from public.event_roster "
              f"where evento = '{EVENTO}' and nombre = '{nombre}'")
