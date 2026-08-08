"""Los comentarios de la jornada: qué ha pasado hoy que merezca una broma.

Slice: `comentarios-de-la-jornada` (openspec/slices/publicacion/comentarios-de-la-jornada.md).

**Los hechos se detectan; la gracia se escribe.** Los detectores emiten `Hecho`, no texto, así que cambiar
quién redacta —la plantilla de aquí hoy, un modelo mañana— no toca la detección, que es lo único que se
puede cubrir con tests.

Funciones puras: sin reloj, sin red y **sin azar** (§10 del protocolo). La variedad sale del número de
jornada, que es un dato: dos ejecuciones del mismo día dan exactamente el mismo mensaje, y eso es lo que
permite fijar en un test lo que el grupo va a leer.

Los umbrales están **calibrados por frecuencia** sobre las 186 jornadas que cuentan: un chiste que sale a
diario deja de ser chiste.

    sospechoso    0,07 por jornada    el chiste estrella, por raro
    sembrado      0,24
    no inspirado  0,24
    rajado        0,18

Los del brief eran otros porque se midieron antes de la regla de días laborables: daban 0,71 a «no
inspirado» con margen 1,5, y con las reglas de hoy ese margen da 0,48. El propio brief ya pedía subirlo a
2,0; con 2,0 la frecuencia real es 0,24.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

# El umbral de día difícil se **reutiliza** del catálogo de medallas. Declarar aquí otro haría que «día
# difícil» significase dos cosas distintas en el mismo mensaje.
from badges import UMBRAL_DIA_DIFICIL
from seasons import MUESTRA_MINIMA_DEL_DIA

#: Cuánto hay que separarse de la media del día para que se comente.
MARGEN_SEMBRADO = 1.5
MARGEN_NO_INSPIRADO = 2.0

#: Media del día a partir de la cual resolver en dos o menos es «sospechoso».
UMBRAL_DIA_EXIGENTE = 4.0
RESOLVER_SOSPECHOSO = 2

#: Cuántos comentarios como mucho. La sección es el remate del mensaje, no un muro.
MAXIMO_COMENTARIOS = 3

#: Cuánto hueco tiene que dejar el último en publicar, y a partir de qué hora, para que llegar tarde sea
#: noticia. Calibrado: con 4h de hueco sale 0,24 por jornada; con 3h, 0,31.
HUECO_DEL_REZAGADO = 4
HORA_DEL_REZAGADO = 14

#: Cuánto mejor que la media del día tiene que ser la nota del rezagado para que la broma sea de sospecha y
#: no de retraso. Con esto la combinación sale 0,06 por jornada: el chiste bueno, por raro.
VENTAJA_SOSPECHOSA = 1.0

#: Orden de notabilidad: si alguien dispara dos, sale por el más raro. Es el orden de la frecuencia medida
#: sobre las 186 jornadas que cuentan:
#:
#:     clavada 0,01 · rezagado-con-suerte 0,06 · sospechoso 0,06 · rajado 0,18
#:     rezagado 0,24 · sembrado 0,24 · no-inspirado 0,24
NOTABILIDAD = (
    "clavada",
    "rezagado-con-suerte",
    "sospechoso",
    "rajado",
    "rezagado",
    "sembrado",
    "no-inspirado",
)


@dataclass(frozen=True)
class Hecho:
    """Algo que ha pasado hoy y merece comentario. **No es texto**: es el dato.

    `varios` existe porque un hecho puede ser de más de una persona —las ausencias van juntas en una línea—
    y el castellano concuerda: «no ha aparecido» frente a «no han aparecido». La redacción necesita saberlo,
    y sacarlo de si el nombre lleva una coma sería adivinar.
    """

    clave: str
    jugador: str
    dato: float | None = None
    varios: bool = False


#: Las frases de cada hecho. Varias por clave para que el mismo suceso no se cuente siempre igual.
FRASES: dict[str, tuple[str, ...]] = {
    "sospechoso": (
        "{jugador} lo ha sacado en {dato:.0f} un día en que el resto sufría. Sospechoso 🤨",
        "Un {dato:.0f} de {jugador} en un día así… ¿alguien le ha visto el diccionario? 🤨",
        "{jugador} ha resuelto en {dato:.0f} mientras el grupo se dejaba los intentos. Muy fuerte 🤨",
    ),
    "sembrado": (
        "{jugador} está sembrad@ hoy 🌟",
        "Día fino de {jugador}, muy por encima de la media 🌟",
        "{jugador} ha ido a lo suyo y le ha salido bien 🌟",
    ),
    "no-inspirado": (
        "{jugador} hoy no estaba inspirad@ 😅",
        "A {jugador} se le ha atragantado la palabra 😅",
        "Día para olvidar de {jugador} 😅",
    ),
    "clavada": (
        "{jugador} lo ha sacado a la PRIMERA. Que alguien revise el diccionario 🍀",
        "A la primera, {jugador}. Esto o es brujería o es que ya la sabía 🍀",
        "{jugador} ha resuelto en 1. Sin comentarios 🍀",
    ),
    "rezagado": (
        "{jugador} ha subido el resultado con el día ya vencido ⏰",
        "Aparece {jugador} a última hora, como siempre ⏰",
        "{jugador} publicando cuando ya nadie miraba ⏰",
    ),
    "rezagado-con-suerte": (
        "{jugador} publica el último y con un {dato:.0f}. Habiendo visto los demás, claro 🕵️",
        "Curioso: {jugador} llega tarde y clava un {dato:.0f}. Nada que declarar 🕵️",
        "El último en publicar es {jugador}, y con un {dato:.0f}. Cosas del azar 🕵️",
    ),
    "rajado": (
        "{jugador} no ha aparecido justo el día difícil 👀",
        "Silencio de {jugador} en la jornada dura 👀",
        "{jugador} se ha rajado hoy, con lo que costaba 👀",
    ),
    # Las ausencias van juntas en una línea, así que hacen falta las dos concordancias.
    "rajado-varios": (
        "{jugador} no han aparecido justo el día difícil 👀",
        "Silencio de {jugador} en la jornada dura 👀",
        "{jugador} se han rajado hoy, con lo que costaba 👀",
    ),
}


def _del_dia(resultados: list[dict], jornada: int) -> list[dict]:
    return [fila for fila in resultados if fila["wordle_id"] == jornada]


def _nombre(fila: dict) -> str:
    return fila.get("player_name") or fila["slack_user_id"]


def dificultad(del_dia: list[dict]) -> float | None:
    """La media del día, o `None` si no hay muestra para calibrarla.

    Con menos de cinco jugadores la media no dice nada del día sino de quién apareció, y comentar sobre eso
    sería inventarse un hecho. Se usa el mismo mínimo que define un día de temporada.
    """
    if len(del_dia) < MUESTRA_MINIMA_DEL_DIA:
        return None
    return statistics.mean(fila["score"] for fila in del_dia)


def hechos_de_la_jornada(resultados: list[dict], temporada: str, jornada: int) -> list[Hecho]:
    """Los hechos notables del día, uno por persona como mucho.

    Una persona sale **una sola vez**, con su hecho más notable: dos líneas seguidas sobre el mismo jugador
    convierten el remate en una novela.

    Las ausencias se miden contra **quien juega esta temporada**, no contra quien jugó alguna vez: llamar
    «rajado» a alguien que jugó una partida en marzo por no aparecer en agosto es un chiste sobre alguien
    que ya no está.
    """
    del_dia = _del_dia(resultados, jornada)
    media = dificultad(del_dia)
    if media is None:
        return []

    encontrados: list[Hecho] = []
    encontrados.extend(_por_la_hora(del_dia, media))
    for fila in del_dia:
        jugador, score = _nombre(fila), fila["score"]
        if score == 1:
            encontrados.append(Hecho("clavada", jugador, score))
        if score <= RESOLVER_SOSPECHOSO and media >= UMBRAL_DIA_EXIGENTE:
            encontrados.append(Hecho("sospechoso", jugador, score))
        if score <= media - MARGEN_SEMBRADO:
            encontrados.append(Hecho("sembrado", jugador, score))
        if score >= media + MARGEN_NO_INSPIRADO:
            encontrados.append(Hecho("no-inspirado", jugador, score))

    if media >= UMBRAL_DIA_DIFICIL:
        from seasons import resultados_de_temporada

        presentes = {_nombre(fila) for fila in del_dia}
        de_la_temporada = {_nombre(fila) for fila in resultados_de_temporada(resultados, temporada)}
        ausentes = sorted(de_la_temporada - presentes)
        if ausentes:
            # **Una sola línea con todos**, no una por persona: tres líneas seguidas señalando a tres
            # ausentes deja de ser una broma y es una lista de morosos.
            encontrados.append(Hecho("rajado", ", ".join(ausentes), varios=len(ausentes) > 1))

    return _uno_por_persona(encontrados)


def _publicado(fila: dict):
    """Cuándo se registró la fila, **solo si es utilizable como hora de publicación**.

    `created_at` es cuando el cron escribió la fila, así que aproxima la publicación con un margen de hasta
    una hora — suficiente para distinguir «por la mañana» de «a media tarde», que es lo único que estos
    chistes necesitan.

    Se exige que caiga **el mismo día que el puzzle**. Las 268 filas del backfill se insertaron todas de
    golpe en otra fecha: ahí el margen no es de una hora sino de meses, y el chiste señalaría a alguien por
    algo que no hizo.
    """
    marca = fila.get("created_at")
    if not marca or str(marca)[:10] != str(fila["date"])[:10]:
        return None
    import datetime

    return datetime.datetime.fromisoformat(str(marca))


def _por_la_hora(del_dia: list[dict], media: float) -> list[Hecho]:
    """Los hechos que dependen de cuándo se publicó: llegar el último, y llegar el último con suerte."""
    con_hora = [(fila, _publicado(fila)) for fila in del_dia]
    con_hora = [(fila, cuando) for fila, cuando in con_hora if cuando is not None]
    if len(con_hora) < 3:
        return []

    con_hora.sort(key=lambda par: par[1])
    (ultimo, cuando), (_, penultimo) = con_hora[-1], con_hora[-2]

    hueco = (cuando - penultimo).total_seconds() >= HUECO_DEL_REZAGADO * 3600
    if not (hueco and cuando.hour >= HORA_DEL_REZAGADO):
        return []

    # Llegar tarde es un chiste; llegar tarde y además clavarla es OTRO, y mejor: es el de haber visto lo
    # que hacían los demás. Se separan porque su frecuencia es muy distinta (0,24 frente a 0,06).
    clave = "rezagado-con-suerte" if ultimo["score"] <= media - VENTAJA_SOSPECHOSA else "rezagado"
    return [Hecho(clave, _nombre(ultimo), ultimo["score"])]


def _uno_por_persona(hechos: list[Hecho]) -> list[Hecho]:
    """El hecho más notable de cada persona, en orden de notabilidad y luego por nombre."""
    mejor: dict[str, Hecho] = {}
    for hecho in hechos:
        actual = mejor.get(hecho.jugador)
        if actual is None or NOTABILIDAD.index(hecho.clave) < NOTABILIDAD.index(actual.clave):
            mejor[hecho.jugador] = hecho
    return sorted(mejor.values(), key=lambda h: (NOTABILIDAD.index(h.clave), h.jugador.lower()))


def frase(
    clave: str, jornada: int, jugador: str, dato: float | None = None, varios: bool = False
) -> str:
    """La frase de un hecho. **Varía sin azar**: la elige el número de jornada, que es un dato.

    `random` daría variedad y rompería la reproducibilidad: dos ejecuciones del mismo día darían mensajes
    distintos y ningún test podría fijar lo que el grupo va a leer.
    """
    opciones = FRASES.get(f"{clave}-varios" if varios else clave) or FRASES[clave]
    plantilla = opciones[jornada % len(opciones)]
    return plantilla.format(jugador=jugador, dato=dato if dato is not None else 0)


def seccion_de_comentarios(resultados: list[dict], temporada: str, jornada: int) -> str:
    """La sección del mensaje, o cadena vacía si hoy no ha pasado nada.

    **Un comentario por tipo como mucho.** Sin esta regla, un día duro llenaba la sección con el mismo
    chiste tres veces —lo enseñó el mensaje real, no un test—: la notabilidad ordena, y todos los hechos de
    la clase más notable se comían el hueco.
    """
    hechos = hechos_de_la_jornada(resultados, temporada, jornada)
    if not hechos:
        return ""

    vistos: set[str] = set()
    elegidos: list[Hecho] = []
    for hecho in hechos:
        if hecho.clave in vistos:
            continue
        vistos.add(hecho.clave)
        elegidos.append(hecho)
        if len(elegidos) == MAXIMO_COMENTARIOS:
            break

    lineas = [f"• {frase(h.clave, jornada, h.jugador, h.dato, h.varios)}" for h in elegidos]
    return "💬 *La jornada*\n" + "\n".join(lineas)
