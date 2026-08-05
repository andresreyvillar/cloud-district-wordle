"""Escribe en Supabase los resultados que `extract_slack.py` emite por tubería.

Slice: `ingesta-por-id-de-slack` (openspec/slices/ingesta/ingesta-por-id-de-slack.md).

La identidad de una fila es **el identificador de Slack** de quien publicó el mensaje, nunca su nombre: un
nombre cambia y un renombre partía al jugador en dos. El nombre se guarda aparte, solo para mostrar.

`filas_a_escribir()` es pura y se verifica sin red. El cliente de Supabase se crea dentro de `main()`:
creado al importar —y con un `sys.exit(1)` si faltaban credenciales— el módulo no se podía importar en un
test.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

from dotenv import load_dotenv

from patterns import bloques_de_resultado

load_dotenv()

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Wordle #1485 fue el 2026-01-30
ANCHOR_ID = 1485
ANCHOR_DATE = datetime(2026, 1, 30).date()

#: La clave del índice único de la tabla. El `upsert` va sobre ella, y es lo que hace que reprocesar la
#: ventana de 50 mensajes cada hora actualice en lugar de duplicar.
CLAVE_DE_CONFLICTO = ("slack_user_id", "wordle_id")

#: Etiquetas acordadas para quien muestra un handle en Slack, no un nombre.
#:
#: Son **tres a propósito**. Medido contra la tabla, para 18 de los 21 jugadores el nombre de Slack ya es
#: exactamente el nombre guardado. El diccionario anterior (`USER_IDENTITY`, 11 entradas) casi nunca se
#: aplicaba, porque buscaba por identificador y el extractor emitía nombres; al resolver por identificador
#: habría renombrado a seis personas, y a una de ellas con el nombre de otra.
#:
#: Añadir una entrada aquí cambia el nombre que ve el grupo: se hace con el dato delante, no por gusto.
ETIQUETAS = {
    "U08U27DFDL2": "Andrés R.",  # muestra "Andres R"
    "U1CKSFSSX": "Carlos H.",    # muestra "carlos.h"
    "U09G8KLSE4Q": "Iván A.",    # muestra "ivan.antona"
}


def nombre_para(identificador: str, nombre_de_slack: str | None) -> str:
    """El nombre que se guarda para mostrar.

    La etiqueta acordada gana; si no hay, el nombre de Slack; y si tampoco, el identificador — feo, pero
    no pierde el resultado y el jugador sigue siendo el correcto.
    """
    return ETIQUETAS.get(identificador) or nombre_de_slack or identificador


def fecha_de_puzzle(numero: int) -> str:
    """La fecha de un puzzle, derivada del ancla y no del reloj.

    Es lo que hace que el dato sea correcto aunque alguien publique su resultado con dos días de retraso.
    """
    return (ANCHOR_DATE + timedelta(days=numero - ANCHOR_ID)).strftime("%Y-%m-%d")


def filas_a_escribir(lineas: list[str]) -> tuple[list[dict], list[str]]:
    """Las filas que corresponden a un lote, y los resultados descartados por no tener autor.

    Sin autor no hay identidad, y aquí no se inventa: antes se escribía `"Unknown"` en la columna de
    identidad, que es exactamente el tipo de valor que este slice viene a eliminar.
    """
    filas: list[dict] = []
    descartadas: list[str] = []

    for bloque in bloques_de_resultado(lineas):
        if not bloque.usuario:
            descartadas.append(bloque.texto_resultado[:200])
            continue
        filas.append(
            {
                "slack_user_id": bloque.usuario,
                "player_name": nombre_para(bloque.usuario, bloque.nombre),
                "wordle_id": bloque.numero,
                "score": bloque.score,
                "date": fecha_de_puzzle(bloque.numero),
                "raw_text": bloque.texto_resultado[:200],
                "pattern": bloque.patron,
            }
        )
    return filas, descartadas


def escribir(filas: list[dict], tabla) -> int:
    """Escribe las filas en la tabla. Devuelve cuántas."""
    for fila in filas:
        tabla.upsert(fila, CLAVE_DE_CONFLICTO)
    return len(filas)


class TablaSupabase:
    """La tabla real. El `upsert` va sobre la clave del índice único."""

    def __init__(self, url: str, clave: str) -> None:
        from supabase import create_client

        self.cliente = create_client(url, clave)

    def upsert(self, fila: dict, clave: tuple[str, ...]) -> None:
        self.cliente.table("wordle_results").upsert(
            fila, on_conflict=", ".join(clave)
        ).execute()


def main() -> int:
    if not URL or not KEY:
        print("Error: Credenciales de Supabase no encontradas.", file=sys.stderr)
        return 1

    entrada = sys.stdin.read()
    if not entrada:
        return 0

    filas, descartadas = filas_a_escribir(entrada.split("\n"))
    tabla = TablaSupabase(URL, KEY)

    escritas = 0
    for fila in filas:
        try:
            escribir([fila], tabla)
            dibujo = fila["pattern"] or "sin patrón"
            print(f"OK: {fila['player_name']} ({fila['slack_user_id']}) - #{fila['wordle_id']} [{dibujo}]")
            escritas += 1
        except Exception as error:  # una fila mala no puede tumbar el lote entero
            print(f"Error con {fila['player_name']} #{fila['wordle_id']}: {error}", file=sys.stderr)

    for texto in descartadas:
        print(f"Descartado (sin autor): {texto}", file=sys.stderr)

    print(f"Finalizado. Escritas: {escritas} · descartadas: {len(descartadas)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
