"""Recupera del histórico del canal los patrones de las filas que se guardaron sin él.

Slice: `backfill-de-patrones` (openspec/slices/ingesta/backfill-de-patrones.md).

Ejecución manual y puntual:

    python3 tools/backfill_patterns.py --dry-run    # ensayo obligatorio: cuenta sin escribir
    python3 tools/backfill_patterns.py              # escribe

`rellenar()` recibe el canal y la tabla **por parámetro**: es lo que permite verificar los siete
escenarios contra dobles en memoria, sin tocar Slack ni Supabase. Los adaptadores reales están al
final del archivo y son la parte que solo el ensayo contra producción puede validar.
"""

from __future__ import annotations

import argparse
import os
import ssl
import sys
from dataclasses import dataclass

# El repo no tiene layout de paquete: como script sys.path[0] es tools/, como módulo importado
# (los tests) la raíz. Se soportan las dos formas para no reimplementar la extracción.
try:  # pragma: no cover - depende de cómo se invoque
    from patterns import RESULTADO_RE, filas_de_cuadricula, normalizar_patron
except ImportError:  # pragma: no cover
    from tools.patterns import RESULTADO_RE, filas_de_cuadricula, normalizar_patron


@dataclass
class Informe:
    """Recuento de una ejecución. Las tres cantidades del Requirement, más los resultados
    del canal que no existen como fila (que este slice no inserta)."""

    rellenadas: int = 0
    intactas: int = 0
    no_resueltas: int = 0
    resultados_sin_registrar: int = 0

    def __str__(self) -> str:
        return (
            f"rellenadas: {self.rellenadas} · intactas: {self.intactas} · "
            f"no resueltas: {self.no_resueltas} · "
            f"resultados del canal sin fila: {self.resultados_sin_registrar}"
        )


def rellenar(canal, tabla, dry_run: bool = False) -> Informe:
    """Escribe el patrón en las filas que lo tienen vacío, y solo en ellas.

    El patrón se extrae con las MISMAS funciones que usa la ingesta (`tools/patterns.py`): si
    hubiera una segunda implementación, los patrones antiguos y los nuevos podrían divergir.
    """
    informe = Informe()
    localizadas: set = set()

    for pagina in canal.paginar():
        for mensaje in pagina:
            resultado = RESULTADO_RE.search(mensaje["texto"])
            if resultado is None:
                continue

            numero = int(resultado.group(1))
            fila = tabla.buscar(numero, mensaje["autor"])
            if fila is None:
                # el canal tiene un resultado que la tabla no registró: se cuenta, no se inserta
                informe.resultados_sin_registrar += 1
                continue

            localizadas.add(fila["id"])
            if fila.get("pattern"):
                informe.intactas += 1
                continue

            patron = normalizar_patron(filas_de_cuadricula(mensaje["texto"]))
            if patron is None:
                continue  # el mensaje no traía cuadrícula: no hay nada que rellenar

            informe.rellenadas += 1
            if not dry_run:
                tabla.actualizar(fila["id"], {"pattern": patron})

    informe.no_resueltas = sum(1 for f in tabla.sin_patron() if f["id"] not in localizadas)
    return informe


# ─────────────────────────── adaptadores reales ───────────────────────────
# Sin tests: los escenarios se verifican con dobles. Lo que valida esta parte es el ensayo
# `--dry-run` contra producción (tarea 4 del change pack).
#
# Usan los clientes que el pipeline ya declara como dependencia (`slack_sdk`, `supabase`) en lugar
# de un cliente HTTP propio. La primera versión de este archivo usaba urllib y falló en el ensayo
# por certificados; el arreglo correcto no es desactivar la verificación TLS —como hace
# extract_slack.py— sino apuntar al bundle de `certifi`.


def contexto_tls() -> ssl.SSLContext:
    """Contexto con verificación completa, usando el bundle de certifi.

    En macOS el almacén del sistema no siempre resuelve para Python, y ese es el motivo por el que
    `tools/extract_slack.py` desactiva la verificación. Desactivarla expone el token del bot a un
    intermediario; certifi resuelve el problema sin renunciar a nada.
    """
    import certifi

    return ssl.create_default_context(cafile=certifi.where())


class CanalSlack:
    """Histórico del canal, paginado con el cursor de la API."""

    PAGINA = 200

    def __init__(self, token: str, canal: str) -> None:
        from slack_sdk import WebClient

        self.canal = canal
        self.cliente = WebClient(token=token, ssl=contexto_tls())
        self.autores = self._mapa_de_autores()

    def _mapa_de_autores(self) -> dict:
        """id de Slack → nombre mostrado, paginando: el workspace tiene más de una página."""
        mapa, cursor = {}, None
        while True:
            respuesta = self.cliente.users_list(limit=self.PAGINA, cursor=cursor)
            for miembro in respuesta["members"]:
                perfil = miembro.get("profile", {})
                mapa[miembro["id"]] = (
                    perfil.get("display_name")
                    or perfil.get("real_name")
                    or miembro.get("real_name")
                    or miembro.get("name")
                    or miembro["id"]
                )
            cursor = respuesta.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                return mapa

    def paginar(self):
        cursor = None
        while True:
            respuesta = self.cliente.conversations_history(
                channel=self.canal, limit=self.PAGINA, cursor=cursor
            )
            yield [
                {"autor": self.autores.get(m.get("user"), m.get("user")), "texto": m.get("text", "")}
                for m in respuesta["messages"]
                if "subtype" not in m
            ]
            cursor = respuesta.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                return


class TablaSupabase:
    """Las filas de `wordle_results`, cargadas una vez y escritas de una en una.

    La lectura pagina de forma explícita: PostgREST devuelve 1000 filas por página y contar sobre
    una sola página ya produjo una cifra equivocada una vez (docs/lecciones.md).
    """

    PAGINA = 1000
    COLUMNAS = "id,wordle_id,player_name,slack_user_id,pattern"

    def __init__(self, url: str, clave: str) -> None:
        from supabase import create_client

        self.cliente = create_client(url, clave)
        self.filas = self._cargar()
        self._indice: dict = {}
        for fila in self.filas:
            self._indice.setdefault(fila["wordle_id"], []).append(fila)

    def _cargar(self) -> list[dict]:
        filas, desplazamiento = [], 0
        while True:
            pagina = (
                self.cliente.table("wordle_results")
                .select(self.COLUMNAS)
                .order("wordle_id")
                .range(desplazamiento, desplazamiento + self.PAGINA - 1)
                .execute()
                .data
            )
            if not pagina:
                return filas
            filas.extend(pagina)
            if len(pagina) < self.PAGINA:
                return filas
            desplazamiento += self.PAGINA

    def sin_patron(self) -> list[dict]:
        return [fila for fila in self.filas if not fila.get("pattern")]

    def buscar(self, wordle_id: int, autor: str) -> dict | None:
        """La fila de ese puzzle cuyo autor coincide.

        La comparación se hace contra `slack_user_id` y contra `player_name` porque la columna de
        identidad contiene un nombre mostrado en cuatro de cada cinco filas. **No se traduce nada**:
        la identidad se arregla en su propio slice, y lo que aquí no coincide se declara como no
        resuelto en lugar de adivinarse.
        """
        for fila in self._indice.get(wordle_id, []):
            if autor and autor in (fila.get("slack_user_id"), fila.get("player_name")):
                return fila
        return None

    def actualizar(self, fila_id, campos: dict) -> None:
        self.cliente.table("wordle_results").update(campos).eq("id", fila_id).execute()
        for fila in self.filas:
            if fila["id"] == fila_id:
                fila.update(campos)


def main(argv: list[str] | None = None) -> int:
    from dotenv import load_dotenv

    load_dotenv()

    analizador = argparse.ArgumentParser(description="Recupera los patrones del histórico del canal.")
    analizador.add_argument(
        "--dry-run", action="store_true", help="cuenta lo que haría sin escribir en la tabla"
    )
    argumentos = analizador.parse_args(argv)

    token = os.environ.get("SLACK_BOT_TOKEN")
    canal_id = os.environ.get("SLACK_CHANNEL_ID")
    url = os.environ.get("SUPABASE_URL")
    clave = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not all([token, canal_id, url, clave]):
        print("Faltan credenciales en el entorno (.env)", file=sys.stderr)
        return 1

    print("Cargando filas de la tabla...")
    tabla = TablaSupabase(url, clave)
    print(f"  {len(tabla.filas)} filas · {len(tabla.sin_patron())} sin patrón")

    print("Recorriendo el histórico del canal...")
    canal = CanalSlack(token, canal_id)

    informe = rellenar(canal, tabla, dry_run=argumentos.dry_run)

    print()
    print("ENSAYO (no se ha escrito nada)" if argumentos.dry_run else "EJECUCIÓN REAL")
    print(f"  {informe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
