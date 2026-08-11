"""Las señales de una jornada, derivadas de los mensajes del canal. **De aquí no sale texto.**

Slice: `voz-de-la-jornada` (openspec/slices/publicacion/voz-de-la-jornada.md).

La tabla tiene nueve columnas y no sabe lo que pasó: no guarda la hora a la que cada uno publicó, ni las
reacciones, ni quién contestó a quién. Este módulo lo saca del canal en el momento de publicar.

**Solo salen números y horas.** Ni el mensaje de nadie, ni el contenido de un hilo, ni una cita: el
repositorio es público y el canal tiene conversaciones de compañeros identificables, así que la frontera se
pone aquí y `Senales` no tiene ningún campo de texto donde pudiera colarse.

**Nada se persiste.** Las señales viven lo que dura la ejecución del cron. Además de no necesitar esquema
nuevo para datos de comportamiento de personas, las reacciones son un **dato vivo**: guardarlas en la ingesta
horaria las congelaría a media mañana, mientras que leerlas a las 17:00 cuenta el día completo.

Función **pura**: entran los mensajes ya leídos, sale el objeto. La llamada a Slack se queda en el borde
(§10), que es lo que permite probar esto con fixtures sintéticos y sin red.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

#: Un mensaje es un resultado si trae la cabecera del juego. Mismo criterio que la ingesta: contar un «jajaja»
#: como resultado falsearía la hora de publicación y, peor, dejaría a alguien fuera de la lista de ausentes.
ES_RESULTADO = re.compile(r"La palabra del d[íi]a\s*#?(\d+)\s+([1-6X])/6", re.I)


def _jornada_de(mensaje: dict) -> int | None:
    """El número de puzzle que declara un mensaje, o `None` si no es un resultado."""
    encontrado = ES_RESULTADO.search(mensaje.get("text") or "")
    return int(encontrado.group(1)) if encontrado else None


def veces_que_abrio(mensajes: list[dict], bot: str | None = None) -> tuple[dict[str, int], int]:
    """Cuántas jornadas ha abierto cada jugador, y sobre cuántas jornadas se cuenta.

    Es lo que permite decir «como de costumbre» en lugar de «hoy»: sin histórico, que alguien publique primero
    un día no dice nada de su costumbre. Se cuenta sobre la ventana que se haya leído del canal —no se
    persiste nada— y por eso devuelve también el denominador: una racha de «3» no significa lo mismo sobre 5
    jornadas que sobre 30.

    Se agrupa por el **número de puzzle que declara el mensaje**, no por su fecha: quien publica el resultado
    de ayer a medianoche abrió la jornada de ayer, no la de hoy.
    """
    primeros: dict[str, int] = {}
    por_jornada: dict[int, tuple[str, float]] = {}

    for mensaje in mensajes:
        autor = mensaje.get("user")
        jornada = _jornada_de(mensaje)
        if not autor or autor == bot or jornada is None:
            continue
        try:
            cuando = float(mensaje.get("ts") or 0)
        except (TypeError, ValueError):
            continue
        actual = por_jornada.get(jornada)
        if actual is None or cuando < actual[1]:
            por_jornada[jornada] = (autor, cuando)

    for autor, _ in por_jornada.values():
        primeros[autor] = primeros.get(autor, 0) + 1
    return primeros, len(por_jornada)


@dataclass(frozen=True)
class Senales:
    """Lo que el canal sabe de una jornada y la tabla no.

    **Ningún campo es texto libre.** Es deliberado y es la garantía de la restricción: aunque alguien añada
    más adelante un consumidor descuidado, aquí no hay nada que se pueda publicar por error.
    """

    #: `jugador → marca de tiempo` del mensaje con su resultado.
    publicacion: dict[str, float] = field(default_factory=dict)
    #: `jugador → reacciones` que recibió su resultado.
    reacciones: dict[str, int] = field(default_factory=dict)
    #: `jugador → respuestas` que tiene el hilo que abrió.
    respuestas: dict[str, int] = field(default_factory=dict)
    #: `jugador → jornadas que ha abierto` en la ventana leída. Es lo que sostiene un «como de costumbre».
    aperturas: dict[str, int] = field(default_factory=dict)
    #: Jornadas sobre las que se cuentan las aperturas. Una racha sin denominador no dice nada.
    jornadas_vistas: int = 0


def senales_del_dia(
    mensajes: list[dict],
    bot: str | None = None,
    jornada: int | None = None,
    desde: float | None = None,
) -> Senales:
    """Las señales de los mensajes de una jornada.

    `bot` es el identificador del propio bot, y sus mensajes **se ignoran del todo**: publica el resumen todas
    las tardes con las reacciones que le eche el grupo, así que sería siempre el más aplaudido de su propio
    mensaje.

    Si un jugador publicó dos veces el mismo día —pasa: se corrige o se reenvía— vale **el primero**, que es
    cuando de verdad resolvió.

    `jornada` acota qué resultados cuentan como «de hoy», y `desde` qué **charla** cuenta. Los dos hacen falta
    porque la ventana que se lee del canal es de treinta días —para poder contar las aperturas— y sin filtros
    el mensaje decía que alguien había montado el hilo del día con una conversación de hace tres semanas. Lo
    delató el mensaje compuesto al ampliar la ventana.
    """
    publicacion: dict[str, float] = {}
    reacciones: dict[str, int] = {}
    respuestas: dict[str, int] = {}

    for mensaje in mensajes:
        autor = mensaje.get("user")
        if not autor or autor == bot:
            continue

        # **Un mensaje raro no puede costar las señales del día.** La auditoría adversarial encontró que un
        # `ts` no numérico o un `count` nulo hacían estallar la derivación entera: el envoltorio del borde lo
        # capturaba y el resumen se publicaba, pero sin ninguna mención. Degradar por mensaje y no por día.
        try:
            cuantas = sum(int(r.get("count") or 0) for r in mensaje.get("reactions") or [])
            hilo = int(mensaje.get("reply_count") or 0)
            cuando = float(mensaje.get("ts") or 0)
        except (TypeError, ValueError):
            continue

        # La conversación cuenta para el hilo aunque no sea un resultado: quien abre debate lo abre igual
        # comentando que jugando. Lo que la charla NO da es hora de publicación.
        if hilo and (desde is None or cuando >= desde):
            respuestas[autor] = max(respuestas.get(autor, 0), hilo)

        suya = _jornada_de(mensaje)
        if suya is None or (jornada is not None and suya != jornada):
            continue

        if autor not in publicacion or cuando < publicacion[autor]:
            publicacion[autor] = cuando
            reacciones[autor] = cuantas
        elif cuantas > reacciones.get(autor, 0):
            reacciones[autor] = cuantas

    aperturas, vistas = veces_que_abrio(mensajes, bot)
    return Senales(
        publicacion=publicacion,
        reacciones=reacciones,
        respuestas=respuestas,
        aperturas=aperturas,
        jornadas_vistas=vistas,
    )
