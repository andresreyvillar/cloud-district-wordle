"""Materializa la instantánea de cada temporada en `season_snapshots`.

Slice: `temporada-mensual` (openspec/slices/ranking/temporada-mensual.md).

    python3 tools/materialize_seasons.py                  # solo la temporada en curso
    python3 tools/materialize_seasons.py --todas           # recalcula el histórico
    python3 tools/materialize_seasons.py --todas --dry-run # cuenta sin escribir

El cron horario la llama sin argumentos después de ingerir. Las temporadas cerradas se recalculan **solo a
mano**, porque recalibrar el pasado es una decisión y no un efecto secundario
([ADR 0008](../openspec/decisions/0008-donde-vive-el-calculo.md)).

`materializar()` recibe la tabla y `ahora` **por parámetro**: no lee el reloj ni abre conexiones, y por eso
se verifica contra un doble.
"""

from __future__ import annotations

import argparse
import datetime
import os
import sys
from dataclasses import dataclass

from dotenv import load_dotenv

from seasons import EN_CURSO, instantanea, temporadas

load_dotenv()

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

TABLA = "season_snapshots"
#: La clave del upsert: una fila por temporada, así que recalcular actualiza en lugar de acumular versiones.
CLAVE = ("temporada",)

PAGINA = 1000
COLUMNAS = "slack_user_id,player_name,wordle_id,score,date"


@dataclass
class Informe:
    materializadas: int = 0
    temporadas: tuple[str, ...] = ()

    def __str__(self) -> str:
        return f"materializadas={self.materializadas} · {', '.join(self.temporadas) or '—'}"


def materializar(
    resultados: list[dict],
    objetivo: list[str],
    tabla,
    ahora: datetime.datetime,
    dry_run: bool = False,
) -> Informe:
    """Calcula y escribe la instantánea de cada temporada de `objetivo`.

    `ahora` se guarda como `updated_at`, que es lo que permite detectar una instantánea rancia. Entra por
    parámetro porque el cálculo no lee el reloj (§10): el borde es `main`.
    """
    escritas: list[str] = []
    for temporada in objetivo:
        fila = {
            "temporada": temporada,
            "payload": instantanea(resultados, temporada),
            "updated_at": ahora.isoformat(),
        }
        if not dry_run:
            tabla.upsert(fila, CLAVE)
        escritas.append(temporada)
    return Informe(materializadas=len(escritas), temporadas=tuple(escritas))


class TablaSupabase:
    def __init__(self, url: str, clave: str) -> None:
        from supabase import create_client

        self.cliente = create_client(url, clave)

    def upsert(self, fila: dict, clave: tuple[str, ...]) -> None:
        self.cliente.table(TABLA).upsert(fila, on_conflict=", ".join(clave)).execute()


def leer_resultados(url: str, clave: str) -> list[dict]:
    """Todos los resultados, paginando de forma explícita."""
    from supabase import create_client

    cliente = create_client(url, clave)
    filas, desplazamiento = [], 0
    while True:
        pagina = (
            cliente.table("wordle_results")
            .select(COLUMNAS)
            .order("wordle_id")
            .range(desplazamiento, desplazamiento + PAGINA - 1)
            .execute()
            .data
        )
        if not pagina:
            return filas
        filas.extend(pagina)
        if len(pagina) < PAGINA:
            return filas
        desplazamiento += PAGINA


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description="Materializa las instantáneas de temporada.")
    analizador.add_argument("--todas", action="store_true", help="recalcula el histórico completo")
    analizador.add_argument("--dry-run", action="store_true", help="cuenta sin escribir")
    argumentos = analizador.parse_args(argv)

    if not (URL and KEY):
        print("Faltan credenciales en el entorno (.env)", file=sys.stderr)
        return 1

    resultados = leer_resultados(URL, KEY)
    lista = temporadas(resultados)
    print(f"{len(resultados)} resultados · {len(lista)} temporadas con datos")

    objetivo = (
        [entrada["temporada"] for entrada in lista]
        if argumentos.todas
        else [entrada["temporada"] for entrada in lista if entrada["estado"] == EN_CURSO]
    )

    for entrada in lista:
        marca = "◀ en curso" if entrada["estado"] == EN_CURSO else ""
        print(f"  {entrada['temporada']}  {entrada['dias']:2} días  {marca}")

    tabla = None if argumentos.dry_run else TablaSupabase(URL, KEY)
    ahora = datetime.datetime.now(datetime.timezone.utc)
    informe = materializar(resultados, objetivo, tabla, ahora, dry_run=argumentos.dry_run)

    print()
    print("ENSAYO (no se ha escrito nada)" if argumentos.dry_run else "EJECUCIÓN REAL")
    print(f"  {informe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
