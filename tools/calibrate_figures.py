"""El informe de calibración del clasificador de figuras. **Solo lee.**

Pack: `feat-calibracion-de-figuras` (Slice: N/A).

Rehace las dos medidas que decidieron la calibración, para que sean reproducibles y no una cifra pegada en
un brief:

1. **acuerdo** con las 30 etiquetas humanas del conjunto dorado (sin red: sale del propio source);
2. **reparto** sobre los patrones reales, que es el criterio que tumbó al primer candidato.

    python3 tools/calibrate_figures.py              las dos medidas
    python3 tools/calibrate_figures.py --sin-red    solo el acuerdo, sin tocar la base

No escribe nada, en ningún modo: `select` y a imprimir.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent))

from figures import FIGURAS, VOCABULARIO, figura  # noqa: E402

load_dotenv()

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "docs/context/sources/2026-08-05-etiquetado-de-patrones.md"

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

#: El reparto que etiquetó el humano en las 30 fichas. Es la referencia del segundo criterio: no se espera
#: clavarlo —30 fichas dan ±9 puntos— pero una categoría al 55% cuando el humano puso 37% es una señal.
REPARTO_HUMANO = {"flores": 0.37, "abstracto": 0.33, "loro": 0.17, "geometrico": 0.13}


def conjunto_dorado() -> list[dict]:
    """Las 30 fichas etiquetadas a mano. `loto` se pliega en `flores` (un ejemplo no calibra nada)."""
    fichas = []
    for bloque in re.finditer(
        r"^## (\d+) · #(\d+) · (\d+) intentos\n```\n(.*?)```\netiqueta: (\w+)",
        FUENTE.read_text(encoding="utf-8"),
        re.M | re.S,
    ):
        ficha, puzzle, intentos, rejilla, etiqueta = bloque.groups()
        fichas.append(
            {
                "ficha": ficha,
                "intentos": int(intentos),
                "patron": "/".join(linea for linea in rejilla.strip().split("\n") if linea.strip()),
                "etiqueta": "flores" if etiqueta == "loto" else etiqueta,
            }
        )
    return fichas


def acuerdo(fichas: list[dict]) -> dict:
    """El acuerdo con las etiquetas humanas, con los desacuerdos desglosados por tipo."""
    fallos, ruido, degradadas = [], 0, 0
    for f in fichas:
        veredicto = figura(f["patron"])
        if veredicto == f["etiqueta"]:
            continue
        fallos.append((f["ficha"], f["etiqueta"], veredicto))
        if f["etiqueta"] == "abstracto" and veredicto in FIGURAS:
            ruido += 1
        elif veredicto == "abstracto" and f["etiqueta"] in FIGURAS:
            degradadas += 1
    return {
        "total": len(fichas),
        "aciertos": len(fichas) - len(fallos),
        "fallos": fallos,
        "ruido_ascendido": ruido,
        "figuras_degradadas": degradadas,
    }


def reparto(patrones: list[str]) -> dict[str, int]:
    conteo = {categoria: 0 for categoria in VOCABULARIO}
    for patron in patrones:
        conteo[figura(patron)] += 1
    return conteo


def patrones_de_produccion() -> list[str]:
    """Los patrones guardados. Paginado: PostgREST devuelve 1000 filas por página."""
    from supabase import create_client

    cliente = create_client(URL, KEY)
    patrones, desde = [], 0
    while True:
        lote = (
            cliente.table("wordle_results")
            .select("pattern")
            .range(desde, desde + 999)
            .execute()
            .data
        )
        patrones += [fila["pattern"] for fila in lote if fila.get("pattern")]
        if len(lote) < 1000:
            break
        desde += 1000
    return patrones


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description="Informe de calibración del clasificador.")
    analizador.add_argument("--sin-red", action="store_true", help="solo el acuerdo, sin leer la base")
    argumentos = analizador.parse_args(argv)

    fichas = conjunto_dorado()
    informe = acuerdo(fichas)
    porcentaje = informe["aciertos"] / informe["total"]
    print(f"CRITERIO 1 · acuerdo con las etiquetas humanas: "
          f"{informe['aciertos']}/{informe['total']} = {porcentaje:.0%}")
    print(f"  ruido ascendido a figura: {informe['ruido_ascendido']}"
          f" · figuras degradadas a abstracto: {informe['figuras_degradadas']}")
    for ficha, humano, veredicto in informe["fallos"]:
        print(f"  ficha {ficha}: humano {humano} → {veredicto}")

    if argumentos.sin_red:
        return 0
    if not (URL and KEY):
        print("\nFaltan credenciales en el entorno (.env): no se puede medir el reparto", file=sys.stderr)
        return 1

    patrones = patrones_de_produccion()
    conteo = reparto(patrones)
    total = sum(conteo.values()) or 1
    print(f"\nCRITERIO 2 · reparto sobre {total} patrones reales      (humano en las 30)")
    desvio = 0.0
    for categoria, referencia in REPARTO_HUMANO.items():
        tasa = conteo[categoria] / total
        desvio += abs(tasa - referencia)
        print(f"  {VOCABULARIO[categoria]} {categoria:11} {conteo[categoria]:5}  {tasa:5.0%}"
              f"   ({referencia:.0%})")
    print(f"  desvío total respecto al humano: {desvio / 2:.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
