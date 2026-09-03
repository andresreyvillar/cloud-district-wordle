"""La clasificación de una temporada, con el modelo de imputación por dificultad.

Slice: `clasificacion-de-temporada` (openspec/slices/ranking/clasificacion-de-temporada.md).

**La tabla se calcula sobre los días de la temporada, no sobre las partidas jugadas.** A quien no jugó un
día se le pone una nota en función de lo que el grupo sufrió ese día:

    imputado(día) = min( max( dificultad(día), media_personal ) + margen(nº de ausencia) , 7 )

Cada pieza responde a un fallo medido sobre el histórico, no a una intuición:

- `dificultad(día)` — faltar un día fácil apenas penaliza; faltar uno duro sí. Era el objetivo de la regla.
- `max(…, media_personal)` — **faltar nunca puede mejorar tu media**. Sin esto ocurría en 9 ocasiones del
  histórico, con hasta −0,18 de premio por ausentarse nueve días.
- `margen` — ausentarse nunca es mejor que publicar. Sin él el día imputado es neutro y callarse un mal
  resultado sigue teniendo premio. **Crece con las ausencias** (`MARGEN + PASO × (n−1)`): fijo, premiaba a
  quien no aparecía —quien jugó 1 de 21 jornadas de agosto de 2026 quedaba por delante de quien jugó 18—,
  porque el `max` de arriba le aplica su propia media como suelo y el castigo se reduce al margen.
- `min(…, 7)` — el tope es el fallo: ninguna ausencia penaliza más que la peor partida posible.

`media_personal` se calcula **solo con los días jugados**, a propósito: usar la media ya imputada volvería la
fórmula circular.

Y el denominador es el mismo para todos —los días de la temporada—, así que las medias se comparan sin
mecanismos añadidos y **no hace falta un umbral mínimo de días para clasificar**.

Funciones puras: sin reloj y sin red (§10 del protocolo).
"""

from __future__ import annotations

import statistics
from collections import defaultdict

from badges import FALLO
from seasons import dias_de_temporada, imputa, resultados_de_temporada

#: Lo que se suma a la **primera** ausencia del mes. Con 0,5 y con 1,0 el campeón es el mismo en los 8 meses
#: del histórico; 0,5 mueve menos a quien juega a diario, así que es el que menos castiga por el borde.
MARGEN = 0.5

#: Cuánto sube el margen por cada ausencia adicional. La primera falta cuesta `MARGEN`, la segunda
#: `MARGEN + PASO`, la enésima `MARGEN + PASO × (n − 1)`, siempre con el tope del fallo.
#:
#: **Un margen fijo premiaba a quien no aparecía.** Con 0,5 fijo, en agosto de 2026 quien jugó 1 de 21
#: jornadas quedaba por delante de quien jugó 18: veinte ausencias le costaban 0,80 en total, porque el
#: `max(dificultad, media_personal)` le aplica su propia media como suelo y el castigo real se reduce al
#: margen. Lo vio el dueño.
#:
#: 0,15 sale de comparar cuatro opciones sobre agosto. Es el que **concentra el castigo en quien no aparece
#: sin tocar a quien falta poco**: con 20 faltas el coste pasa de +0,80 a +2,14, y con 4 faltas se queda en
#: +0,28 —donde el margen fijo de 1,0 lo subía a +0,31—. Con 0,25 el tramo medio se desordena: quien jugó 11
#: de 21 caía seis puestos. El campeón de agosto es el mismo con las cuatro opciones.
PASO_DEL_MARGEN = 0.15

#: Partidas mínimas para clasificar en la temporada 0. **Es el umbral del legacy**, no uno inventado: la v1
#: exigía cinco partidas para coronar la "Mejor Media" (`js/script.js`, `MIN_GAMES_FOR_BEST_AVG = 5`).
#:
#: La temporada 0 se rige por las reglas que estaban en vigor cuando se jugó, y esa era una de ellas. En una
#: temporada numerada no aplica: la imputación ya impide que unos pocos días buenos ganen el mes.
#:
#: Quien no llega al umbral **no desaparece**: sale en la tabla marcado como sin clasificar, porque verse en
#: su sitio informa más que no verse. Es también lo que hacía la v1, cuyo umbral afectaba a la tarjeta de
#: campeón pero no a la tabla.
MINIMO_PARA_CLASIFICAR = 5

#: Los decimales con los que se comparan dos medias. Sin redondear, el ruido del coma flotante decidiría
#: empates que a la vista son idénticos.
PRECISION = 6


def dificultad_por_dia(resultados: list[dict], temporada: str) -> dict[int, float]:
    """La media del grupo en cada jornada válida de la temporada."""
    cuentan = resultados_de_temporada(resultados, temporada)
    por_dia: dict[int, list[int]] = defaultdict(list)
    for fila in cuentan:
        por_dia[fila["wordle_id"]].append(fila["score"])
    return {jornada: round(statistics.mean(scores), 4) for jornada, scores in por_dia.items()}


def margen_de(ausencia: int) -> float:
    """El margen de la enésima ausencia del mes, contando desde 1.

    **Crece con las ausencias**, y eso es lo que arregla el fallo que tenía el margen fijo: la primera falta
    cuesta `MARGEN` y cada siguiente `PASO_DEL_MARGEN` más.
    """
    return MARGEN + PASO_DEL_MARGEN * max(0, ausencia - 1)


def imputar(dificultad: float, media_personal: float, ausencia: int = 1) -> float:
    """La nota de un día no jugado. `ausencia` es la enésima falta de ese jugador en la temporada."""
    return min(max(dificultad, media_personal) + margen_de(ausencia), float(FALLO))


def clasificacion(resultados: list[dict], temporada: str) -> list[dict]:
    """La tabla de una temporada, ordenada.

    Orden: media imputada ascendente; a igualdad, **más días jugados delante** —premia la participación en
    el desempate— y luego el nombre, para que el resultado sea determinista y no dependa del orden de las
    filas que llegan de la base de datos.
    """
    dias = dias_de_temporada(resultados, temporada)
    if not dias:
        return []

    # La temporada 0 no imputa: se ordena por lo que cada uno jugó de verdad (ver `seasons.imputa`).
    con_imputacion = imputa(temporada)

    cuentan = resultados_de_temporada(resultados, temporada)
    dificultad = dificultad_por_dia(resultados, temporada)
    fecha_de = {fila["wordle_id"]: str(fila["date"])[:10] for fila in cuentan}

    jugadas: dict[str, dict[int, int]] = defaultdict(dict)
    nombre_de: dict[str, str] = {}
    for fila in cuentan:
        jugador = fila["slack_user_id"]
        jugadas[jugador][fila["wordle_id"]] = fila["score"]
        nombre_de[jugador] = fila.get("player_name") or jugador

    filas: list[dict] = []
    for jugador, suyas in jugadas.items():
        media_personal = statistics.mean(suyas.values())

        por_dia = []
        # Las ausencias se cuentan **en orden de jornada**, así que la enésima falta del mes es la que paga el
        # margen enésimo. `dias` viene ordenado, que es lo que hace esto determinista.
        ausencias = 0
        for jornada in (dias if con_imputacion else sorted(suyas)):
            if jornada in suyas:
                por_dia.append(
                    {
                        "jornada": jornada,
                        "fecha": fecha_de[jornada],
                        "intentos": float(suyas[jornada]),
                        "imputado": False,
                    }
                )
            else:
                ausencias += 1
                por_dia.append(
                    {
                        "jornada": jornada,
                        "fecha": fecha_de[jornada],
                        "intentos": round(
                            imputar(dificultad[jornada], media_personal, ausencias), 2
                        ),
                        "imputado": True,
                    }
                )

        media_temporada = statistics.mean(dia["intentos"] for dia in por_dia)
        distribucion = [0] * 7
        for score in suyas.values():
            distribucion[min(score, FALLO) - 1] += 1

        filas.append(
            {
                "jugador": jugador,
                "nombre": nombre_de[jugador],
                "dias": len(dias),
                "jugados": len(suyas),
                "media_jugada": round(media_personal, 2),
                "media_temporada": round(media_temporada, 2),
                "mejor": min(suyas.values()),
                "peor": max(suyas.values()),
                "distribucion": distribucion,
                "por_dia": por_dia,
            }
        )

    # Sin imputación hace falta un mínimo para clasificar; con imputación no, porque la propia imputación
    # ya impide que unos pocos días buenos ganen la temporada.
    minimo = 1 if con_imputacion else MINIMO_PARA_CLASIFICAR
    for fila in filas:
        fila["clasificado"] = fila["jugados"] >= minimo

    filas.sort(
        key=lambda fila: (
            not fila["clasificado"],  # los que no clasifican, al final
            round(fila["media_temporada"], PRECISION),
            -fila["jugados"],
            fila["nombre"].lower(),
        )
    )
    # Puesto compartido cuando la media es la misma: dos jugadores con 3,58 no han hecho uno mejor que el
    # otro, y el desempate interno existe para que el orden sea determinista, no para separarlos. El
    # siguiente salta tantos números como gente lleve por delante.
    #
    # Se compara sobre la media **publicada**, no sobre el flotante crudo: si a la vista son el mismo
    # número, separarlos es incomprensible para quien lo lee.
    #
    # Empatar no es raro: el 62% de las jornadas que cuentan tienen empate en la mejor nota del día.
    posicion = 0
    vistos = 0
    anterior = None
    for fila in filas:
        if not fila["clasificado"]:
            fila["posicion"] = None
            continue
        vistos += 1
        if fila["media_temporada"] != anterior:
            posicion = vistos
            anterior = fila["media_temporada"]
        fila["posicion"] = posicion
    return filas
