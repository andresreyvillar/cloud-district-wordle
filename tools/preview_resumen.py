"""Compone el mensaje de la tarde y lo imprime. **No publica nada.**

Slice: `voz-de-la-jornada` (openspec/slices/publicacion/voz-de-la-jornada.md).

Existe porque los gates no leen. El bug «resolvión» —pegarle una «n» a «resolvió» para hacer el plural— pasó
validate, coverage, mutación y la suite entera, y lo cazó imprimir el mensaje y mirarlo. Antes de mergear algo
que cambie este texto, se mira.

    python3 tools/preview_resumen.py             con las señales reales del canal
    python3 tools/preview_resumen.py --sin-canal solo con lo que sabe la tabla

Lee de Supabase y del canal, y **no escribe en ninguno de los dos**. Del canal no imprime ni un mensaje: solo
el resumen que se publicaría.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from post_ranking import (  # noqa: E402
    OBJETIVOS,
    comentario,
    leer_el_canal,
    leer_resultados,
    objetivo_de_captura,
    resumen_activo,
    temporada_del_resumen,
)
from badges import texto_de_medallas  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="El mensaje de la tarde, sin publicarlo.")
    parser.add_argument("--sin-canal", action="store_true", help="no leer las señales del canal")
    args = parser.parse_args()

    resultados = leer_resultados()
    if not resultados:
        print("sin resultados: no habría mensaje", file=sys.stderr)
        return 1

    jornada = max(fila["wordle_id"] for fila in resultados)
    temporada = temporada_del_resumen(resultados)
    senales = None if args.sin_canal else leer_el_canal()

    print(f"[jornada {jornada} · temporada {temporada} · resumen_activo={resumen_activo()}]")
    print(f"[señales del canal: {'sí' if senales else 'no'}]")
    print("=" * 78)
    print(comentario(texto_de_medallas(resultados, temporada, jornada), objetivo_de_captura(), resultados,
                     senales=senales))
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
