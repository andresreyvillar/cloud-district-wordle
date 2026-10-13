#!/usr/bin/env python3
"""Publica el podio del mes que cierra, una vez al empezar el mes siguiente.

Slice: `podio-de-cierre-de-mes`.

**Qué mes se celebra sale de los datos** (§10): la temporada en curso es la del último resultado y se celebra
la inmediatamente anterior. Nada de fechas del reloj, que es lo que permite fijar el mensaje en un test.

**Es idempotente**, igual que el resumen diario: el título de la imagen lleva el mes celebrado, y si el canal
ya lo tiene no se vuelve a publicar. Por eso el cron corre **del día 1 al 3** en lugar de solo el 1: si GitHub
se salta la ventana —y estos días se salta el 86%—, se publica al día siguiente y no se pierde el cierre.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import os
import sys

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from podio import DESDE_TRES_COMPETICIONES, _siguiente, temporada_que_cierra, texto  # noqa: E402
from post_ranking import (  # noqa: E402
    TITULO_DEL_PODIO,
    capture_ranking,
    leer_juego,
    leer_resultados,
    mensajes_recientes,
    objetivo_del_podio,
    upload_to_slack,
    ya_celebrado,
)

#: Días antes del arranque del mes nuevo desde los que se lee el canal. La victoria sale la noche del último
#: laborable del mes cerrado, que puede caer hasta tres días antes del día 1 —un mes que acaba en domingo—, o
#: más con un festivo: una semana lo cubre de sobra sin leer el mes entero.
DIAS_ANTES_DEL_MES_NUEVO = 7


def desde_de_la_comprobacion(temporada: str) -> float:
    """Desde cuándo se lee el canal para saber si `temporada` ya se celebró, en segundos UTC.

    **Sale de la temporada, no del reloj** (§10), y **es una fecha, no un número de mensajes**: el 7 de octubre
    de 2026 el podio de septiembre se republicó porque estaba en la posición 153 y se leían 150. Por fecha, la
    comprobación alcanza lo mismo juegue la gente que juegue.
    """
    año, mes = (int(parte) for parte in _siguiente(temporada).split("-"))
    arranque = dt.datetime(año, mes, 1, tzinfo=dt.timezone.utc)
    return (arranque - dt.timedelta(days=DIAS_ANTES_DEL_MES_NUEVO)).timestamp()


async def celebrar(
    capturar=capture_ranking,
    subir=upload_to_slack,
    resultados=None,
    leer_mensajes=mensajes_recientes,
    leer_el_juego=leer_juego,
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

    # **Por fecha, no por número de mensajes.** Contando, el podio se republicó dos veces: agosto estaba en la
    # posición 44 y se leían 30; septiembre, en la 153 y se leían 150.
    if ya_celebrado(leer_mensajes(limite=200, desde=desde_de_la_comprobacion(temporada)), temporada):
        print(f"el podio de {temporada} ya está publicado: no se repite")
        return 0

    jornada = max(fila["wordle_id"] for fila in filas)
    # El juego solo hace falta desde que se coronan los tres campeones: antes, ni se lee.
    niveles, marcas = leer_el_juego() if temporada >= DESDE_TRES_COMPETICIONES else ([], [])
    cuerpo = texto(filas, temporada, jornada, niveles, marcas)
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
