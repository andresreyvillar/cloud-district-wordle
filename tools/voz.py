"""La voz del resumen: qué frase, qué menciones y qué meme lleva el mensaje de la tarde.

Slice: `voz-de-la-jornada` (openspec/slices/publicacion/voz-de-la-jornada.md).
Diccionario: `tools/refranero.py` (solo datos).

Funciones **puras**: entran señales, cifras y el número de jornada; sale texto. **Sin reloj y sin azar**
(§10), y eso no es celo de protocolo: es lo que hace que dos ejecuciones del mismo cron publiquen lo mismo y
que el mensaje entero se pueda comprobar en un test.
"""

from __future__ import annotations

from refranero import (
    AUSENTE,
    DIA_DURO,
    DIA_FACIL,
    DIA_NORMAL,
    LIDER_DEL_ALBUM,
    LIDER_DEL_MARCADOR,
    MADRUGADOR,
    MAS_APLAUDIDO,
    MAS_COMENTADO,
    MEMES,
    REZAGADO,
)

#: Cortes de dificultad entre registros, en intentos medios de la jornada.
DIA_SUAVE_HASTA = 3.5
DIA_DURO_DESDE = 4.5

#: Minutos que hay que sacarle al resto del grupo para que la mención salga. **Medidos sobre 187 jornadas
#: reales del canal**, no elegidos redondos, con el criterio de que la mención caiga en una minoría clara:
#:
#:              60m    120m   240m   360m
#: madrugador   24%     3%     2%     1%
#: rezagado     65%    45%    24%    18%
#:
#: La asimetría es real y tiene explicación: la mañana está apelotonada —casi todo el mundo juega al empezar
#: el día— así que sacar una hora ya destaca. La tarde está dispersa, y con menos de cuatro horas «llegar
#: tarde» le pasa a dos de cada tres jornadas, que es una columna y no una mención.
HUECO_DEL_MADRUGADOR = 60
HUECO_DEL_REZAGADO = 240

#: Añadidos como máximo. **Decisión del dueño al implementar**: sin tope, una jornada movida encadena doce
#: bloques y eso es un muro que nadie lee en Slack — el efecto contrario al que busca el slice.
TOPE_DE_ANADIDOS = 3

#: Fallos que hacen que una partida no cuente como resuelta.
FALLO = 7

#: Resolver en esto o menos vuelca la jornada a incredulidad. Es el mismo umbral que la pulla del sospechoso
#: (`comentarios.RESOLVER_SOSPECHOSO`), y se declara aquí para no importar el módulo entero por un número.
RESOLVER_SOSPECHOSO = 2

#: Cuánto hay que mejorar la media de un día duro para que la jornada sea épica en lugar de una derrota.
MARGEN_HAZANA = 1.5

#: Separación de la media de la temporada que hace notable una jornada. Igual que en `resumen.DELTA_NOTABLE`,
#: medido sobre 166 jornadas.
DELTA_NOTABLE = 0.40


def con_nombre(plantilla: str, jugador: str) -> str:
    """La plantilla con el nombre puesto, sin puntuación duplicada.

    Varios nombres del grupo acaban en punto —«Andrés R.», «Carlos H.»— y una plantilla que termina en punto
    producía «Hoy se ha hablado de Andrés R..». Lo cazó **mirar el mensaje**, no la suite: los tests
    comprobaban que el nombre saliera, no cómo quedaba la frase alrededor.
    """
    texto = plantilla.format(jugador=jugador)
    while ".." in texto:
        texto = texto.replace("..", ".")
    return texto


def _del_ciclo(frases: tuple[str, ...], jornada: int) -> str:
    """La frase que le toca a una jornada.

    El índice sale del **número de jornada**, así que la misma jornada da siempre la misma frase y dos
    consecutivas nunca dan la misma. Precio declarado: el orden es cíclico y por tanto predecible para quien
    se ponga a mirar. Se acepta porque la alternativa —azar— rompe los golden tests del mensaje.
    """
    return frases[jornada % len(frases)]


def frase_del_dia(dificultad: float, jornada: int) -> str:
    """La frase que resume la jornada, con el registro que le corresponde a lo dura que fue.

    Se mantiene para quien solo quiera el registro por dificultad. El resumen usa `cierre`, que lo elige por
    el estado de ánimo de la jornada — así todas las piezas con tono del mensaje vienen del mismo sitio.
    """
    if dificultad <= DIA_SUAVE_HASTA:
        registro = DIA_FACIL
    elif dificultad >= DIA_DURO_DESDE:
        registro = DIA_DURO
    else:
        registro = DIA_NORMAL
    return _del_ciclo(registro, jornada)


def estado_de_animo(dificultad: float | None, media: float | None, mejor: int | None) -> str:
    """El estado de ánimo de una jornada, derivado de los datos y **sin azar**.

    Es lo que da voz única al mensaje: todas las piezas con tono —la pulla, el cierre, los conectores— se
    sacan del mismo estado, en lugar de que cada bloque eligiera del suyo sin saber qué habían elegido los
    demás. El mensaje sonaba a tres personas distintas escribiendo por turnos.

    El orden de las comprobaciones es el criterio: **lo más llamativo manda**. Un uno o un dos convierte la
    jornada en incredulidad aunque el día fuera fácil, porque es de lo único que se va a hablar.
    """
    from refranero import DERROTA, EPICA, FIESTA, INCREDULIDAD, RUTINA

    if mejor is not None and mejor <= RESOLVER_SOSPECHOSO:
        return INCREDULIDAD
    if dificultad is None or media is None:
        return RUTINA

    delta = dificultad - media
    if delta >= DELTA_NOTABLE:
        # Día duro: épico si alguien lo sacó bien de todas formas, derrota si no. La hazaña se mide contra
        # **la dificultad del día**, no contra la media de la temporada: lo épico es destacar sobre lo que
        # sufrió el grupo hoy, y comparar con la temporada hacía que un 3 en un día de 5,2 saliera derrota.
        return EPICA if mejor is not None and mejor <= dificultad - MARGEN_HAZANA else DERROTA
    if delta <= -DELTA_NOTABLE:
        return FIESTA
    return RUTINA


def cierre(estado: str, jornada: int, dato: float | None = None, jugador: str = "") -> str:
    """La frase que cierra el comentario, del registro del estado de ánimo.

    Rellena **los dos huecos posibles**, y de ahí la guarda: cuando el registro pasó a llevar frases con
    `{jugador}` —«{jugador}, esta palabra es tu padre»— esta función solo formateaba `dato`, así que reventaba
    con `KeyError` o publicaba el hueco literal en el canal según qué frase rotara ese día.

    Si no se sabe a quién nombrar, se salta la primera frase que lo pida en lugar de escribir un hueco vacío:
    una frase sin sujeto se lee peor que otra frase.
    """
    from refranero import CIERRE

    registro = CIERRE.get(estado) or CIERRE["rutina"]
    for salto in range(len(registro)):
        plantilla = registro[(jornada + salto) % len(registro)]
        # Se salta la frase que pide un hueco que no se puede rellenar. Escribir «0 intentos» o dejar el
        # `{jugador}` literal es peor que usar otra frase del mismo registro: el tono se conserva igual.
        if ("{jugador}" in plantilla and not jugador) or ("{dato" in plantilla and dato is None):
            continue
        return plantilla.format(dato=dato, jugador=jugador)
    return ""


def conector(estado: str, jornada: int) -> str:
    """El conector que encadena la segunda línea con la primera, del registro del estado."""
    from refranero import CONECTORES

    opciones = CONECTORES.get(estado) or CONECTORES["rutina"]
    return opciones[jornada % len(opciones)]


def pullas_de_lideres(lider_marcador: str | None, lider_album: str | None, jornada: int) -> dict[str, str]:
    """Una pulla para quien manda en cada eje.

    Sin líder de álbum no sale la del álbum: nadie llega al mínimo de partidas y nombrar a quien no tiene
    puesto sería inventarle una corona.

    Los dos registros son listas distintas, así que la misma persona liderando los dos ejes recibe frases
    distintas — que es justo el caso donde repetir cantaría más.
    """
    pullas: dict[str, str] = {}
    if lider_marcador:
        pullas["marcador"] = con_nombre(_del_ciclo(LIDER_DEL_MARCADOR, jornada), lider_marcador)
    if lider_album:
        pullas["album"] = con_nombre(_del_ciclo(LIDER_DEL_ALBUM, jornada), lider_album)
    return pullas


#: Cuánta gente puede nombrar una mención antes de dejar de ser una mención.
#:
#: **Lo cazó un test de otro slice** (`test_el_mensaje_no_crece_con_el_numero_de_jugadores`): nombrando a
#: todos los ausentes, un grupo de treinta llevaba el mensaje de 754 a 1483 caracteres. La propiedad que ese
#: test protege es que **el mensaje no crece con el grupo**, y una lista de nombres la rompe.
#:
#: Y además de largo, señalar a doce personas no señala a nadie: la gracia de la mención es que apunta.
MAXIMO_NOMBRADOS = 2


def _los_de(valores: dict[str, int]) -> list[str]:
    """Quiénes tienen el máximo, si el máximo es al menos uno. Vacío si no hay evidencia.

    Se nombran todos los empatados **hasta el tope**: con diez personas y recuentos pequeños el empate es lo
    normal, y romperlo por el orden en que llegaron las filas sería arbitrario. Pero un empate multitudinario
    no premia a nadie, así que por encima del tope la mención no se concede.
    """
    if not valores:
        return []
    tope = max(valores.values())
    if tope < 1:
        return []
    empatados = sorted(jugador for jugador, cuantos in valores.items() if cuantos == tope)
    return empatados if len(empatados) <= MAXIMO_NOMBRADOS else []


def _nombres_de(jugadores: list[str], nombres: dict[str, str]) -> str:
    """Los nombres como se leen: «Ana», «Ana y Bea».

    Con una coma —«Lo de Gabi, Sandra ha levantado al canal»— la frase se lee como una enumeración cortada.
    Y las frases se reescribieron para que el verbo no concuerde con el número: así una sola plantilla vale
    para uno o para dos, que es lo que el resto del diccionario ya hacía y a las menciones no llegó.
    """
    from comentarios import nombres_unidos

    return nombres_unidos([nombres.get(jugador, jugador) for jugador in jugadores])


def menciones(
    reacciones: dict[str, int],
    respuestas: dict[str, int],
    publicacion: dict[str, float],
    nombres: dict[str, str],
    habituales: list[str] | None = None,
    jornada: int = 0,
) -> dict[str, str]:
    """Las menciones del día, cada una con su evidencia. **Ninguna se concede por defecto.**

    `habituales` son los jugadores de los que se puede decir que faltaron. Sin esa lista no se afirma ninguna
    ausencia: quien no juega nunca no está ausente, simplemente no juega.
    """
    salida: dict[str, str] = {}

    aplaudidos = _los_de(reacciones)
    if aplaudidos:
        salida["aplaudido"] = con_nombre(
            _del_ciclo(MAS_APLAUDIDO, jornada), _nombres_de(aplaudidos, nombres)
        )

    comentados = _los_de(respuestas)
    if comentados:
        salida["comentado"] = con_nombre(
            _del_ciclo(MAS_COMENTADO, jornada), _nombres_de(comentados, nombres)
        )

    # Hacen falta al menos dos publicaciones: con una sola no hay con quién comparar, así que no hay ni
    # madrugador ni rezagado. Es el mismo criterio que hace que un grupo de uno no tenga podio.
    if len(publicacion) >= 2:
        orden = sorted(publicacion.items(), key=lambda par: par[1])
        if (orden[1][1] - orden[0][1]) / 60 >= HUECO_DEL_MADRUGADOR:
            salida["madrugador"] = con_nombre(
                _del_ciclo(MADRUGADOR, jornada), nombres.get(orden[0][0], orden[0][0])
            )
        if (orden[-1][1] - orden[-2][1]) / 60 >= HUECO_DEL_REZAGADO:
            salida["rezagado"] = con_nombre(
                _del_ciclo(REZAGADO, jornada), nombres.get(orden[-1][0], orden[-1][0])
            )

    # Solo se señala una ausencia cuando falta poca gente. Si falta media liga no es una mención, es el dato
    # del día — y nombrarlos a todos hace crecer el mensaje con el grupo.
    faltan = sorted(set(habituales or []) - set(publicacion))
    if faltan and len(faltan) <= MAXIMO_NOMBRADOS:
        salida["ausente"] = con_nombre(_del_ciclo(AUSENTE, jornada), _nombres_de(faltan, nombres))

    return salida


def meme_del_dia(
    del_dia: list[dict],
    jornada: int,
    lider: str | None = None,
    ultimo: str | None = None,
) -> str | None:
    """El meme que describe la jornada, o `None` si la jornada no tiene forma.

    Las condiciones se evalúan **en orden** y gana la primera: la forma más llamativa manda sobre la genérica.
    Si no se cumple ninguna **no hay meme**, y eso es deliberado — un chiste que no encaja delata que lo pone
    una máquina, que es peor que no ponerlo.

    Es **texto**, nunca una imagen. El bot tiene `files:write` y subir una imagen ajena al canal sería un
    problema de derechos y de permisos a la vez; la plantilla consigue el mismo chiste sin ninguno de los dos.
    """
    if not del_dia:
        return None

    plantillas = dict(MEMES)
    total = len(del_dia)
    resueltos = [fila for fila in del_dia if fila["intentos"] < FALLO]
    fallados = total - len(resueltos)
    intentos = [fila["intentos"] for fila in del_dia]
    mejor, peor = min(intentos), max(intentos)

    def nombre(fila: dict) -> str:
        return fila.get("nombre") or fila["jugador"]

    if len(resueltos) == 1 and total >= 3 and fallados >= 2:
        clave = "solo-uno-lo-saca" if resueltos[0]["intentos"] > 1 else "clavada-en-una"
        return plantillas[clave].format(jugador=nombre(resueltos[0]))

    if any(fila["intentos"] == 1 for fila in del_dia):
        clavada = next(fila for fila in del_dia if fila["intentos"] == 1)
        return plantillas["clavada-en-una"].format(jugador=nombre(clavada))

    if resueltos == [] :
        return plantillas["todos-fallan"].format(faltan=fallados, total=total)

    if total >= 4 and mejor == peor:
        return plantillas["todos-el-mismo-numero"].format(total=total, intentos=mejor)

    if lider:
        del_lider = next((fila for fila in del_dia if nombre(fila) == lider), None)
        if del_lider and del_lider["intentos"] >= FALLO - 1:
            return plantillas["el-lider-se-hunde"].format(
                jugador=lider, intentos=del_lider["intentos"]
            )

    if ultimo:
        del_ultimo = next((fila for fila in del_dia if nombre(fila) == ultimo), None)
        if del_ultimo and del_ultimo["intentos"] <= 2:
            return plantillas["el-ultimo-clava"].format(
                jugador=ultimo, intentos=del_ultimo["intentos"]
            )

    if peor - mejor >= 4:
        return plantillas["dia-de-dos-mundos"].format(mejor=mejor, peor=peor)

    return None


#: Orden de prioridad de los añadidos. El meme describe lo que pasó, así que va primero; la frase del día
#: existe para el día que no tiene nada que contar, así que va última y **cede el sitio** cuando hay algo
#: mejor. Las menciones se ordenan por la evidencia que las respalda.
PRIORIDAD_DE_MENCIONES = ("aplaudido", "comentado", "madrugador", "rezagado", "ausente")


def anadidos(
    meme: str | None,
    menciones: dict[str, str],
    frase: str | None,
    tope: int = TOPE_DE_ANADIDOS,
) -> list[str]:
    """Los añadidos que caben en el mensaje, en orden y como mucho `tope`.

    **Las pullas de líder no pasan por aquí.** Acompañan al marcador y al álbum, que salen siempre, así que
    contarlas como añadidos habría hecho que los escenarios del líder dejaran de cumplirse en las jornadas
    movidas — dos escenarios del mismo slice contradiciéndose. Se resolvió dejándolas pegadas a su bloque.
    """
    salida: list[str] = []
    if meme:
        salida.append(meme)
    for clave in PRIORIDAD_DE_MENCIONES:
        if len(salida) >= tope:
            break
        if clave in menciones:
            salida.append(menciones[clave])
    if frase and len(salida) < tope:
        salida.append(frase)
    return salida[:tope]
