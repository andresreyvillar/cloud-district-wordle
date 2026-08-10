"""El informe de calibración de las menciones del canal. **Solo lee.**

Slice: `voz-de-la-jornada` (openspec/slices/publicacion/voz-de-la-jornada.md).

Responde a la pregunta que decide los umbrales: **¿cada cuánto saldría cada mención?** El criterio del slice
es que salga en una **minoría clara** de las jornadas. Un umbral que nombra a alguien todos los días deja de
ser una mención y pasa a ser una columna; uno que no nombra a nadie nunca es código muerto.

    python3 tools/calibrate_menciones.py    el informe sobre el histórico entero del canal

**No escribe nada, en ningún modo, y no imprime ni un mensaje del canal**: solo horas relativas y recuentos.
El repositorio es público y el canal tiene conversaciones de compañeros identificables.
"""

from __future__ import annotations

import os
import re
import sys
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv
from slack_sdk import WebClient

sys.path.insert(0, str(Path(__file__).resolve().parent))

load_dotenv()

TOKEN = os.environ.get("SLACK_BOT_TOKEN")
CANAL = os.environ.get("SLACK_CHANNEL_ID")

#: Un mensaje es un resultado si trae la cabecera del juego. Es el mismo criterio que usa la ingesta.
ES_RESULTADO = re.compile(r"La palabra del d[íi]a\s*#?(\d+)\s+([1-6X])/6", re.I)

#: Candidatos a umbral, en minutos de distancia respecto al resto del grupo.
HUECOS = (60, 120, 180, 240, 300, 360)


def _jornadas(mensajes: list[dict]) -> dict[int, list[tuple[str, float, int, int]]]:
    """Por jornada: `(usuario, ts, reacciones, respuestas)` de cada resultado. Sin texto."""
    por_jornada: dict[int, list[tuple[str, float, int, int]]] = {}
    for m in mensajes:
        encontrado = ES_RESULTADO.search(m.get("text") or "")
        if not encontrado or not m.get("user"):
            continue
        reacciones = sum(r.get("count", 0) for r in m.get("reactions", []))
        por_jornada.setdefault(int(encontrado.group(1)), []).append(
            (m["user"], float(m["ts"]), reacciones, int(m.get("reply_count", 0)))
        )
    return por_jornada


def informe(por_jornada: dict[int, list[tuple[str, float, int, int]]]) -> None:
    completas = {j: filas for j, filas in por_jornada.items() if len(filas) >= 2}
    print(f"{len(por_jornada)} jornadas leídas · {len(completas)} con dos o más resultados\n")

    print("MADRUGADOR / REZAGADO — en cuántas jornadas saldría, según el hueco exigido")
    print(f"{'hueco':>8}  {'madrugador':>12}  {'rezagado':>10}")
    for hueco in HUECOS:
        madruga = rezaga = 0
        for filas in completas.values():
            horas = sorted(ts for _, ts, _, _ in filas)
            if (horas[1] - horas[0]) / 60 >= hueco:
                madruga += 1
            if (horas[-1] - horas[-2]) / 60 >= hueco:
                rezaga += 1
        n = len(completas) or 1
        print(f"{hueco:>6}m  {madruga:>5} ({100*madruga/n:4.0f}%)  {rezaga:>5} ({100*rezaga/n:4.0f}%)")

    con_reacciones = sum(1 for f in por_jornada.values() if any(r for _, _, r, _ in f))
    con_hilos = sum(1 for f in por_jornada.values() if any(h for _, _, _, h in f))
    n = len(por_jornada) or 1
    print(f"\nMÁS APLAUDIDO: {con_reacciones} jornadas con alguna reacción = {100*con_reacciones/n:.0f}%")
    print(f"MÁS COMENTADO: {con_hilos} jornadas con algún hilo = {100*con_hilos/n:.0f}%")

    reparto = Counter(r for filas in por_jornada.values() for _, _, r, _ in filas if r)
    if reparto:
        print(f"  reacciones por mensaje premiado: mín {min(reparto)} · máx {max(reparto)}")


def main() -> int:
    if not TOKEN or not CANAL:
        print("faltan SLACK_BOT_TOKEN o SLACK_CHANNEL_ID", file=sys.stderr)
        return 1

    # El contexto TLS sale de `extract_slack`, que ya lo resolvió con el bundle de certifi. **No se
    # reimplementa aquí**: la versión anterior de ese módulo usaba `ssl.CERT_NONE` para esquivar el problema
    # de certificados de macOS, y eso mandaba el token del bot por una conexión sin verificar.
    from extract_slack import contexto_tls

    cli = WebClient(token=TOKEN, ssl=contexto_tls())
    mensajes: list[dict] = []
    cursor = None
    while True:
        # El histórico entero: son 187 jornadas y la calibración no se hace todos los días.
        respuesta = cli.conversations_history(channel=CANAL, limit=200, cursor=cursor)
        mensajes += respuesta.get("messages", [])
        cursor = (respuesta.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            break

    informe(_jornadas(mensajes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
