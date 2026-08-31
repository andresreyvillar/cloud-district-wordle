#!/usr/bin/env python3
"""Publica el podio del mes que cierra, una vez al empezar el mes siguiente.

Slice: `podio-de-cierre-de-mes`.

**Qué mes se celebra sale de los datos** (§10): la temporada en curso es la del último resultado y se celebra
la inmediatamente anterior. Nada de fechas del reloj, que es lo que permite fijar el mensaje en un test.

**Es idempotente**, igual que el resumen diario: el título de la imagen lleva el mes celebrado, y si el canal
ya lo tiene no se vuelve a publicar. Por eso el cron corre **del día 1 al 7** en lugar de solo el 1: si GitHub
se salta la ventana —y estos días se salta el 86%—, se publica al día siguiente y no se pierde el cierre.
"""

from __future__ import annotations

import asyncio
import os
import re
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from podio import temporada_que_cierra, texto  # noqa: E402
from post_ranking import (  # noqa: E402
    capture_ranking,
    leer_resultados,
    mensajes_recientes,
    objetivo_del_podio,
    upload_to_slack,
)

#: El título de la imagen lleva el mes celebrado: es la marca que hace posible no repetir el mensaje.
TITULO_DEL_PODIO = "Podio del mes 🏆 · {temporada}"




def ya_celebrado(mensajes: list[dict], temporada: str) -> bool:
    """Si el canal ya tiene el podio de ese mes.

    Se busca **la marca del mes** dentro del título y no el título entero: Slack devuelve el emoji convertido
    a su código corto, y comparar el título completo es justo el fallo que publicó el resumen por triplicado
    los días 28 y 29 de agosto de 2026.
    """
    marca = re.compile(re.escape(f"· {temporada}") + r"(?!\d)")
    for mensaje in mensajes:
        if not mensaje.get("bot_id"):
            continue
        for fichero in mensaje.get("files") or []:
            if marca.search(fichero.get("title") or ""):
                return True
    return False


async def celebrar(
    capturar=capture_ranking,
    subir=upload_to_slack,
    resultados=None,
    leer_mensajes=mensajes_recientes,
) -> int:
    """El flujo del cierre de mes. Devuelve el código de salida.

    Sin mes que cerrar **no es un fallo**: es el caso normal veintitantos días al mes, y también a primera
    hora del día 1 mientras nadie haya jugado todavía.
    """
    filas = leer_resultados() if resultados is None else resultados
    if not filas:
        print("sin resultados: nada que celebrar")
        return 0

    temporada = temporada_que_cierra(filas)
    if not temporada:
        print("no hay mes cerrado que celebrar todavía")
        return 0

    if ya_celebrado(leer_mensajes(), temporada):
        print(f"el podio de {temporada} ya está publicado: no se repite")
        return 0

    jornada = max(fila["wordle_id"] for fila in filas)
    cuerpo = texto(filas, temporada, jornada)
    if not cuerpo:
        print(f"{temporada} no tiene podio que enseñar")
        return 0

    objetivo = objetivo_del_podio(temporada)
    try:
        ruta = await capturar(objetivo)
    except Exception as error:  # noqa: BLE001 — cualquier fallo de navegador es un fallo de publicación
        print(f"error capturando el podio de {temporada}: {error}", file=sys.stderr)
        return 1

    publicado = subir(ruta, cuerpo, TITULO_DEL_PODIO.format(temporada=temporada))

    if os.path.exists(ruta):
        os.remove(ruta)
    return 0 if publicado else 1


async def main() -> int:
    if not os.getenv("SLACK_BOT_TOKEN") or not os.getenv("SLACK_CHANNEL_ID"):
        print("Error: Faltan credenciales en el .env", file=sys.stderr)
        return 1
    return await celebrar()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
