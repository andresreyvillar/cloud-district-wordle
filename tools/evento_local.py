"""El juego del evento en local, entero, sin tocar Supabase.

    python3 tools/evento_local.py                   # el evento de prueba, con los nombres de quienes juegan al Wordle
    python3 tools/evento_local.py --sin-nombres     # solo los participantes inventados de la semilla
    python3 tools/evento_local.py --puerto 9000

Levanta un Postgres **desechable** con las migraciones del repositorio y el evento de prueba
(`supabase/seeds/evento_de_prueba.sql`), y sirve la v2 en la red local. Para probar el buscador con nombres de
verdad, añade a la lista a quienes juegan al Wordle, repartidos al azar en diez grupos: los lee de Supabase **solo
para leer**, con la clave pública, y no los escribe en ningún fichero. Las llamadas de la web a
`/rest/v1/rpc/<función>` —lo que en producción contesta Supabase— las contesta este servidor ejecutando la función
en ese Postgres con el rol `anon`, el mismo que usa la clave pública. Solo atiende las funciones del evento.

Se puede jugar desde el móvil si está en la misma wifi: el servidor escucha en todas las interfaces y escribe la
dirección al arrancar. Al pararlo (Ctrl+C) la base de datos desaparece: cada arranque empieza de cero.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

from dotenv import load_dotenv

RAIZ_DEL_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ_DEL_REPO))

from serve_v2 import PREFIJO, PUERTO, RAIZ, ManejadorSPA  # noqa: E402
from tests.postgres_local import INITDB, PG_CTL, PSQL, postgres_con_migraciones  # noqa: E402

SEMILLA = RAIZ_DEL_REPO / "supabase" / "seeds" / "evento_de_prueba.sql"
PIN_DE_PRUEBA = "0000"
GRUPOS = 10

#: Lo único que se puede llamar: las funciones públicas del evento, con sus parámetros.
FUNCIONES = {
    "estado_del_juego": ("p_evento",),
    "nombres_del_evento": ("p_evento",),
    "elegir_nombre": ("p_evento", "p_nombre", "p_token"),
    "mi_juego": ("p_evento", "p_token"),
    "empezar_palabra": ("p_evento", "p_token", "p_orden"),
    "probar_palabra": ("p_evento", "p_token", "p_orden", "p_palabra", "p_numero"),
    "panel_del_evento": ("p_evento", "p_pin"),
    "empezar_evento": ("p_evento", "p_pin"),
    "terminar_evento": ("p_evento", "p_pin"),
    "liberar_nombre": ("p_evento", "p_pin", "p_nombre"),
    # El dashboard, sin PIN.
    "tablero_del_evento": ("p_evento",),
    "echar_participante": ("p_evento", "p_nombre"),
    "cambiar_palabra": ("p_evento", "p_orden", "p_palabra"),
    "palabras_del_evento": ("p_evento",),
}

ERROR_DE_POSTGRES = re.compile(r"ERROR:\s+([0-9A-Z]{5}):\s+(.*)")


def literal(valor) -> str:
    """Un valor JSON como literal SQL. Enteros tal cual; el resto, como texto con las comillas dobladas."""
    if valor is None:
        return "null"
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, int):
        return str(valor)
    return "'" + str(valor).replace("'", "''") + "'"


def consulta_de(funcion: str, argumentos: dict) -> str:
    parametros = FUNCIONES[funcion]
    desconocidos = set(argumentos) - set(parametros)
    if desconocidos:
        raise ValueError(f"parámetros desconocidos: {sorted(desconocidos)}")
    lista = ", ".join(f"{nombre} => {literal(argumentos.get(nombre))}" for nombre in parametros)
    return f"\\set VERBOSITY verbose\nselect public.{funcion}({lista});"


def respuesta_de(resultado) -> tuple[int, dict | list | None]:
    """El `CompletedProcess` de psql como lo contestaría PostgREST: 200 con el JSON, o 400 con el error."""
    if resultado.returncode == 0:
        salida = resultado.stdout.strip()
        return 200, json.loads(salida) if salida else None
    error = ERROR_DE_POSTGRES.search(resultado.stderr)
    codigo, mensaje = (error.group(1), error.group(2).strip()) if error else ("XX000", resultado.stderr.strip())
    return 400, {"code": codigo, "message": mensaje, "details": None, "hint": None}


class ManejadorDelEvento(ManejadorSPA):
    """La web de la v2 y, debajo de `/rest/v1/rpc/`, las funciones del evento."""

    sql = None

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self.end_headers()

    def do_POST(self):  # noqa: N802
        funcion = self.path.split("?")[0].removeprefix("/rest/v1/rpc/")
        if not self.path.startswith("/rest/v1/rpc/") or funcion not in FUNCIONES:
            self._json(404, {"code": "PGRST202", "message": "función desconocida"})
            return
        try:
            largo = int(self.headers.get("Content-Length") or 0)
            argumentos = json.loads(self.rfile.read(largo) or b"{}")
            consulta = consulta_de(funcion, argumentos)
        except (ValueError, json.JSONDecodeError) as error:
            self._json(400, {"code": "PGRST100", "message": str(error)})
            return
        self._json(*respuesta_de(self.sql(consulta, rol="anon")))

    def _json(self, estado: int, cuerpo) -> None:
        datos = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
        self.send_response(estado)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)


def nombres_del_wordle() -> list[str]:
    """Los nombres de quienes juegan al Wordle, leídos de Supabase con la clave pública (solo lectura)."""
    import os
    import ssl
    import urllib.request

    try:  # El Python de python.org no trae los certificados raíz; `certifi` sí (viene con `supabase`).
        import certifi
        contexto = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        contexto = ssl.create_default_context()

    url, clave = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_ANON_KEY")
    if not url or not clave:
        return []
    peticion = urllib.request.Request(f"{url}/rest/v1/wordle_results?select=player_name&limit=100000",
                                      headers={"apikey": clave, "Authorization": f"Bearer {clave}"})
    with urllib.request.urlopen(peticion, timeout=15, context=contexto) as respuesta:
        filas = json.load(respuesta)
    return sorted({str(f["player_name"]).strip() for f in filas if str(f.get("player_name") or "").strip()})


def cargar_nombres(sql, nombres: list[str]) -> int:
    """Añade los nombres a la lista del evento de prueba, repartidos al azar en grupos. Devuelve cuántos entraron."""
    import random

    aleatorio = random.Random()
    filas = []
    for i, nombre in enumerate(aleatorio.sample(nombres, len(nombres))):
        nombre = nombre[:60].replace("$", "")
        filas.append(f"('prueba', $n${nombre}$n$, 'Grupo {i % GRUPOS + 1}')")
    if not filas:
        return 0
    resultado = sql("insert into public.event_roster (evento, nombre, grupo) values " + ", ".join(filas)
                    + " on conflict (evento, clave) do nothing")
    return 0 if resultado.returncode else len(filas)


def ip_de_la_red_local() -> str | None:
    """La IP de este ordenador en la wifi. Conectar un socket UDP no envía nada: solo elige la interfaz."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("192.0.2.1", 9))
            return s.getsockname()[0]
    except OSError:
        return None


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    sys.stdout.reconfigure(line_buffering=True)
    analizador = argparse.ArgumentParser(description="El juego del evento en local, sin tocar Supabase.")
    analizador.add_argument("--puerto", type=int, default=PUERTO)
    analizador.add_argument("--sin-nombres", action="store_true",
                            help="no añadir a la lista los nombres de quienes juegan al Wordle")
    argumentos = analizador.parse_args(argv)

    if not (INITDB and PG_CTL and PSQL):
        print("No hay Postgres local (initdb, pg_ctl y psql). Con Homebrew: brew install postgresql@14")
        return 1

    print("Levantando un Postgres desechable con las migraciones y el evento de prueba…")
    arranque = postgres_con_migraciones()
    sql = next(arranque)
    try:
        cargada = sql(SEMILLA.read_text(encoding="utf-8"))
        if cargada.returncode != 0:
            print(cargada.stderr)
            return 1
        if not argumentos.sin_nombres:
            try:
                print(f"Añadidos {cargar_nombres(sql, nombres_del_wordle())} nombres del Wordle a la lista.")
            except OSError as error:
                print(f"No se han podido leer los nombres del Wordle ({error}): solo los inventados.")

        ManejadorDelEvento.sql = staticmethod(sql)
        servidor = ThreadingHTTPServer(("0.0.0.0", argumentos.puerto), partial(ManejadorDelEvento, directory=str(RAIZ)))
        ip = ip_de_la_red_local()
        print()
        print(f"  Participante:  http://localhost:{argumentos.puerto}{PREFIJO}evento")
        print(f"  Admin:         http://localhost:{argumentos.puerto}{PREFIJO}evento/admin   (PIN: {PIN_DE_PRUEBA})")
        if ip:
            print(f"  Desde el móvil (misma wifi):  http://{ip}:{argumentos.puerto}{PREFIJO}evento")
        print("  Activa el evento desde el admin. Ctrl+C para parar: la base de datos se borra.")
        print()
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            servidor.server_close()
    finally:
        arranque.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
