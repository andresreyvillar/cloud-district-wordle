"""El texto del resumen diario: qué pasó hoy, contado en palabras.

Slice: `resumen-diario-compuesto` (openspec/slices/publicacion/resumen-diario-compuesto.md).

Funciones **puras**: entran los resultados, la temporada y la jornada, y sale texto. Sin reloj, sin Slack y
sin navegador (§10 del protocolo), y por eso el mensaje que el grupo va a ver se puede fijar en un test.

**No recalcula nada.** El marcador sale de `standings.clasificacion` y el álbum de `album.album`, que son
los mismos que publica la web ([ADR 0008](../openspec/decisions/0008-donde-vive-el-calculo.md)). Un
publicador con su propia versión de las reglas diría cosas distintas de la web, y el grupo tendría dos
verdades.

**Dos premios y no uno.** Medido sobre 17 jornadas: exigir mejor puntuación *y* figura reconocible deja el
premio vacío el 94% de los días, porque la figura sale de las partidas que salen mal. Jugador del día y obra
del día son premios distintos a propósito, y casi nunca los gana la misma persona.
"""

from __future__ import annotations

import calendar
import datetime
import statistics

from album import album
from comentarios import nombres_unidos, seccion_de_comentarios
from figures import CULO, FIGURAS, figura, rasgos
from juego import ESCALA, PUNTOS_DESDE_EL_OCTAVO, clasificacion_del_juego, niveles_que_puntuan, puestos_de_nivel
from podios import lista_de_texto, podio_de_texto
from personas import HUECO, concuerda
from seasons import MUESTRA_MINIMA_DEL_DIA, TEMPORADA_CERO, dias_de_temporada, es_laborable, resultados_de_temporada
from standings import clasificacion

#: Los puestos de cada podio del mensaje: el marcador, el juego y las figuras. Tres: la cabeza, no la tabla —
#: la tabla está en la web—. Se corta **por puesto**: un empate en el tercero sube entero.
TOP = 3

#: Cuántos del álbum. El mismo podio de tres.
CABEZA_DEL_ALBUM = 3

#: Límite de `initial_comment` en Slack, para dejar constancia de contra qué se mide.
#:
#: **No hay recorte, y a propósito**: el mensaje está acotado por construcción —dos líneas, tres podios de
#: tres puestos con como mucho tres nombres por escalón, y el bloque del momento del mes— así que no crece con
#: el grupo por muchos jugadores que haya. Se escribió un recorte antes
#: de comprobarlo, y su test pasaba con 499 caracteres contra 3000: no ejercitaba nada. Lo que se verifica
#: ahora es la propiedad de verdad, que el mensaje no crece.
LIMITE_DE_SLACK = 3000


def _del_dia(resultados: list[dict], jornada: int) -> list[dict]:
    return [fila for fila in resultados if fila["wordle_id"] == jornada]


def _nombre(fila: dict) -> str:
    return fila.get("player_name") or fila["slack_user_id"]


def bloque_jugador_del_dia(del_dia: list[dict]) -> str:
    """Quién mejor puntuó hoy. **Los empates se nombran todos.**

    Con diez jugadores y notas de 1 a 7 el empate es lo normal, no la excepción: elegir uno por el orden en
    que llegaron las filas sería arbitrario y además no determinista.
    """
    if not del_dia:
        return ""
    mejor = min(fila["score"] for fila in del_dia)
    quienes = sorted({_nombre(fila) for fila in del_dia if fila["score"] == mejor})
    # Las dos palabras cambian con el número, y las dos se conjugan enteras. Pegarle una «n» a «resolvió»
    # daba «resolvión», que estuvo a punto de publicarse en el canal: el plural de un pretérito no se forma
    # añadiendo una letra. El test de este bloque comprobaba a quién se nombra, nunca cómo se conjuga.
    uno = len(quienes) == 1
    titulo = "Jugador del día" if uno else "Jugadores del día"
    verbo = "resolvió" if uno else "resolvieron"
    return f"🏆 *{titulo}:* {', '.join(quienes)} — {verbo} en {mejor}."


def rareza(resultados: list[dict], temporada: str) -> dict[str, int]:
    """Cuántas veces ha salido cada categoría en la temporada. Menos veces, más rara.

    Se deriva **del reparto de la propia temporada** y no de una tabla escrita a mano: recalibrar el
    clasificador cambia qué figura es rara, y una lista fija se quedaría atrás en silencio.
    """
    return album(resultados, temporada)["reparto"]


def bloque_obra_del_dia(resultados: list[dict], temporada: str, jornada: int) -> str:
    """La figura más rara dibujada hoy, con su autor.

    Empates: primero la categoría menos frecuente de la temporada; luego **la simetría**, porque un espejo
    perfecto es más difícil que una forma escasa y el clasificador, que solo devuelve categorías, no sabe
    distinguirlos; luego **más intentos**, porque la figura sale del lienzo y el lienzo lo deja quien tarda
    (2,9 intentos de media en las partidas sin figura frente a 4,7 en las que la tienen); y por último el
    nombre, para que el resultado no dependa del orden de las filas.

    La simetría por delante de los intentos es **decisión del dueño**, y cambia a quién se premia: el día que
    se decidió había dos geométricos, uno simétrico resuelto en 3 y otro escaso resuelto en 4, y el premio se
    lo llevaba el segundo.
    """
    ganadoras = _obra_del_dia(resultados, temporada, jornada)
    if not ganadoras:
        return "🖼️ *Obra del día:* desierta — hoy no ha salido ninguna figura reconocible."
    from figures import emoji

    categoria = ganadoras[0][1]
    intentos = ganadoras[0][0]["score"]
    # Todas las empatadas tienen la misma categoría y los mismos intentos: es lo que las empata.
    quienes = _y([_nombre(fila) for fila, _ in ganadoras])
    return f"🖼️ *Obra del día:* {emoji(categoria)} de {quienes} ({intentos} intentos)."


def _obra_del_dia(resultados: list[dict], temporada: str, jornada: int):
    """La figura premiada del día como `(fila, categoria)`, o `None` si no hay ninguna reconocible.

    Separada del texto para que la use también `bloque_la_jornada` **sin reimplementar el desempate**: la
    regla de qué dibujo gana vive en un solo sitio, y una segunda copia habría divergido en la primera
    recalibración.
    """
    candidatas = [
        (fila, figura(fila["pattern"], jornada))
        for fila in _del_dia(resultados, jornada)
        if fila.get("pattern")
    ]
    reconocibles = [(fila, cat) for fila, cat in candidatas if cat in FIGURAS]
    if not reconocibles:
        return None

    frecuencia = rareza(resultados, temporada)

    def merito(par):
        """Lo que hace mejor a un dibujo, de más importante a menos. **Sin el nombre.**"""
        return (
            frecuencia.get(par[1], 0),
            not rasgos(par[0]["pattern"]).espejo,  # el espejo primero
            -par[0]["score"],
        )

    # **El premio se comparte, decisión del dueño.** Antes el nombre entraba en el desempate y elegía un
    # ganador arbitrario: el día que se decidió, Claire y Raquel tenían el mismo culo en los mismos intentos y
    # ganaba Claire por la «C». Medido sobre 204 jornadas con obra, **el 25% tiene empate** —36 de dos, 10 de
    # tres y hasta una de seis—, así que era un cuarto de los premios repartido por orden alfabético.
    #
    # El nombre sigue ordenando la lista, pero ya no decide: es lo que mantiene el cálculo determinista.
    mejor = min(merito(par) for par in reconocibles)
    return sorted(
        (par for par in reconocibles if merito(par) == mejor),
        key=lambda par: _nombre(par[0]).lower(),
    )


def _figura_del_dia_por_jugador(resultados: list[dict], jornada: int) -> dict[str, str]:
    from figures import emoji

    dibujos = {}
    for fila in _del_dia(resultados, jornada):
        if fila.get("pattern"):
            dibujos[fila["slack_user_id"]] = emoji(figura(fila["pattern"], jornada))
    return dibujos


def _figuras_reconocibles_del_dia(resultados: list[dict], jornada: int) -> dict[str, str]:
    """Solo los dibujos **premiables** del día, por jugador.

    Distinta de `_figura_del_dia_por_jugador`, que devuelve el emoji de cualquier cuadrícula —abstractos
    incluidos— porque el marcador quiere poner algo al lado de cada nombre. Aquí hace falta lo contrario:
    saber si hubo arte de verdad, para no llamar «figura» a una mancha ni decir que no hubo ninguna cuando lo
    que falta es el patrón.
    """
    from figures import emoji

    dibujos = {}
    for fila in _del_dia(resultados, jornada):
        if not fila.get("pattern"):
            continue
        categoria = figura(fila["pattern"], jornada)
        if categoria in FIGURAS:
            dibujos[fila["slack_user_id"]] = emoji(categoria)
    return dibujos


def bloque_palabra(palabra: tuple[str, str] | None) -> str:
    """La palabra de la jornada con su significado, o nada si no se pudo averiguar.

    **Abre el mensaje**, por delante de todo lo demás: es el dato que el grupo no tiene por su cuenta —cada
    uno conoce su resultado, pero nadie ve la palabra escrita ni lo que significa—.

    Entra por parámetro y no se busca aquí: la red vive en el borde (§10), y así el mensaje entero sigue
    siendo reproducible en un test. Sin acepción se publica la palabra sola, que ya es más de lo que había.
    """
    if not palabra:
        return ""
    termino, acepcion = palabra
    if not termino:
        return ""
    if not acepcion:
        return f"📖 *La palabra de hoy:* {termino.upper()}"
    return f"📖 *La palabra de hoy:* {termino.upper()} — {acepcion}"


def bloque_top(resultados: list[dict], temporada: str, jornada: int) -> str:
    """El podio del marcador: los tres primeros puestos con su media.

    **Se corta por puesto, no por número de filas.** Con puestos compartidos, quedarse con las tres primeras
    filas puede partir un empate por la mitad. Empatar es lo normal: el 62% de las jornadas tiene empate en la
    mejor nota del día.

    El dibujo del día ya no va aquí: el podio es un bloque de ancho fijo y un emoji ocupa dos columnas. Sigue
    en la obra del día. `jornada` se conserva en la firma para no cambiar a quien la llama.
    """
    clasificados = [fila for fila in clasificacion(resultados, temporada) if fila["clasificado"]]
    puestos = [
        {"posicion": fila["posicion"], "nombre": fila["nombre"], "cifra": _cifra(fila["media_temporada"])}
        for fila in clasificados
        if fila["posicion"] <= TOP
    ]
    return podio_de_texto(f"📊 *Marcador · {_etiqueta(resultados, temporada)}*", puestos)


def _tiempo(segundos) -> str:
    """El tiempo del juego con centésimas, como lo enseña su ranking: `0:31.20`."""
    centesimas = max(0, round(float(segundos) * 100))
    minutos, resto = divmod(centesimas, 6000)
    return f"{minutos}:{resto / 100:05.2f}"


def _nivel_del_dia(niveles, jornada: int) -> int | None:
    """El nivel que se jugó el día de la jornada: el último congelado **anterior** a ella.

    El de la jornada de hoy se congela mañana. Tras un fin de semana es el del viernes, que se ha jugado de
    sábado a lunes.
    """
    anteriores = [nivel["jornada"] for nivel in niveles or () if nivel["jornada"] < jornada]
    return max(anteriores) if anteriores else None


def bloque_juego(resultados: list[dict], temporada: str, jornada: int, niveles=(), marcas=()) -> str:
    """El SuperWordleBros: quién ganó el nivel del día, y el podio del mes por puntos.

    La clasificación sale de `juego.clasificacion_del_juego`, la misma que guarda la instantánea que pinta la
    web: el mensaje no tiene su propia versión de la escala.
    """
    del_nivel = []
    nivel = _nivel_del_dia(niveles, jornada)
    if nivel is not None:
        # El orden del ranking del nivel: más estrellas primero y, con las mismas, menos tiempo.
        del_nivel = sorted(
            (m for m in marcas or () if m["jornada"] == nivel),
            key=lambda m: (-int(m.get("estrellas") or 0), round(float(m["segundos"]) * 100)),
        )

    tabla = clasificacion_del_juego(resultados, list(niveles or ()), list(marcas or ()), temporada)
    puestos = [
        {"posicion": fila["posicion"], "nombre": fila["nombre"], "cifra": f"{fila['puntos']} pts"}
        for fila in tabla["clasificacion"]
        if fila["posicion"] <= TOP
    ]
    if not del_nivel and not puestos:
        return ""

    if del_nivel:
        nombres = _nombres_por_jugador(resultados)
        clave = lambda m: (int(m.get("estrellas") or 0), round(float(m["segundos"]) * 100))  # noqa: E731
        # Por nombre entre los empatados: el orden de las filas de la base de datos no puede cambiar el mensaje.
        ganadores = sorted(
            (nombres.get(m["jugador"], m["jugador"]) for m in del_nivel if clave(m) == clave(del_nivel[0])),
            key=str.lower,
        )
        estrellas = int(del_nivel[0].get("estrellas") or 0)
        verbo = "lo ganan" if len(ganadores) > 1 else "lo gana"
        cuantos = len(del_nivel)
        titulo = (
            f"🎮 *SuperWordleBros* — el nivel #{nivel} {verbo} {_y(ganadores)} con ⭐ {estrellas} en "
            f"{_tiempo(del_nivel[0]['segundos'])} ({cuantos} {'jugador' if cuantos == 1 else 'jugadores'})"
        )
    else:
        titulo = f"🎮 *SuperWordleBros · {_etiqueta(resultados, temporada)}*"

    if not puestos:
        return titulo
    # En lista y no en dibujo: el podio ASCII es del marcador general (decisión del dueño, 2026-10-02).
    return lista_de_texto(titulo, puestos)


def _nombres_por_jugador(resultados: list[dict]) -> dict[str, str]:
    """El nombre de la fila más reciente de cada jugador, como en la clasificación del juego."""
    ultima: dict[str, dict] = {}
    for fila in resultados:
        previa = ultima.get(fila["slack_user_id"])
        if previa is None or fila["wordle_id"] > previa["wordle_id"]:
            ultima[fila["slack_user_id"]] = fila
    return {jugador: fila.get("player_name") or jugador for jugador, fila in ultima.items()}


#: Ventaja que deja de ser ventaja, en media de intentos por día. Con siete jornadas, 0,15 es un solo intento
#: en todo el mes: quien va segundo lo remonta con una jornada buena. Es el mismo umbral que usa el titular
#: de la web (`v2/js/ui/temporada.js`), y por la misma razón.
VENTAJA_MINIMA = 0.15

#: Jornadas previas que hace falta que tenga la temporada para hablar de un relevo. Con menos, quitar la de
#: hoy deja un marcador que no representa nada y cualquier orden parece un cambio de líder.
JORNADAS_PARA_HABLAR_DE_RELEVO = 3



#: Cuánto se separa la jornada de la media de su temporada para que se comente, en intentos.
#:
#: **Medido sobre 166 jornadas reales.** Con ±0,40 el 55% de los días quedan en «normal», «más difícil de lo
#: habitual» sale en el 19% y «más fácil» en el 25%. Con ±0,20 saldría en dos de cada tres jornadas y dejaría
#: de informar; con ±0,60 solo en una de siete. El adverbio «mucho» entra en ±0,80, que es el percentil 90.
DELTA_NOTABLE = 0.40
DELTA_MUCHO = 0.80

#: Personas que se nombran en una línea antes de resumir el resto. Tres nombres se leen; siete o doce son una
#: lista, hacen crecer el mensaje con el grupo y dejan de señalar a nadie. Se usa para los ausentes y para los
#: mejores del día, que es donde el empate múltiple es lo normal.
AUSENTES_NOMBRADOS = 3

#: Fracción de jornadas abiertas que convierte «hoy ha madrugado» en «como de costumbre».
COSTUMBRE = 0.5

#: Retraso del último respecto al primero a partir del cual se menciona, en minutos.
CIERRE_TARDE = 120

#: Cuánto tiene que mejorar la media del día el último en publicar para que la mención cambie de tono. Es el
#: mismo margen que usaba el detector que esto sustituye (`comentarios.VENTAJA_SOSPECHOSA`), y por la misma
#: razón: es la diferencia a partir de la cual «ha llegado tarde» pasa a «ha llegado tarde y mira qué bien».
VENTAJA_DEL_REZAGADO = 1.0


def _y(nombres: list[str]) -> str:
    """Los nombres unidos como se leen: «Ana», «Ana y Bea», «Ana, Bea y Cris».

    Una coma final —«Claire, Dani Sanchez, con 3»— se lee como una enumeración cortada. Lo delató el mensaje
    compuesto, no un test.
    """
    if len(nombres) <= 1:
        return nombres[0] if nombres else ""
    return f"{', '.join(nombres[:-1])} y {nombres[-1]}"


def _media_de_dificultades(resultados: list[dict], temporada: str) -> float | None:
    """La dificultad media de las jornadas de la temporada, para comparar la de hoy contra algo comparable.

    **No vale la media imputada del marcador**, que es lo que esto usaba: incluye la penalización de los días
    que cada uno no juega, así que está inflada y achata la diferencia. Con los datos del día en que se
    corrigió, hoy salía a +0,20 de la media imputada (4,62) y a **+0,49** de la media real de las jornadas
    (4,33) — la primera decía «jornada de las de siempre» y la segunda «más difícil de lo habitual», que es lo
    que era. Lo cazó el dueño leyendo el mensaje.
    
    Y es también la referencia con la que se calibraron los cortes sobre 166 jornadas, así que ahora el umbral
    y la medida hablan de lo mismo. Se incluye la jornada de hoy en la media, igual que en la calibración.

    Hereda de `resultados_de_temporada` qué jornadas cuentan, en lugar de tener su propia definición.
    """
    from comentarios import dificultad
    from seasons import resultados_de_temporada

    por_jornada: dict[int, list[dict]] = {}
    for fila in resultados_de_temporada(resultados, temporada):
        por_jornada.setdefault(fila["wordle_id"], []).append(fila)

    medidas = [d for d in (dificultad(fs) for fs in por_jornada.values()) if d is not None]
    return sum(medidas) / len(medidas) if medidas else None


def _linea_de_dificultad(hoy: float, media: float, jornada: int) -> str:
    from refranero import (
        DIFICULTAD_MAS_DURA,
        DIFICULTAD_MAS_FACIL,
        DIFICULTAD_MUCHO_MAS_DURA,
        DIFICULTAD_MUCHO_MAS_FACIL,
        DIFICULTAD_NORMAL,
    )
    from voz import _del_ciclo

    delta = hoy - media
    if delta >= DELTA_MUCHO:
        registro = DIFICULTAD_MUCHO_MAS_DURA
    elif delta >= DELTA_NOTABLE:
        registro = DIFICULTAD_MAS_DURA
    elif delta <= -DELTA_MUCHO:
        registro = DIFICULTAD_MUCHO_MAS_FACIL
    elif delta <= -DELTA_NOTABLE:
        registro = DIFICULTAD_MAS_FACIL
    else:
        registro = DIFICULTAD_NORMAL
    return _del_ciclo(registro, jornada).format(cifra=_cifra(hoy), media=_cifra(media))


def _linea_de_horarios(
    senales,
    nombres: dict[str, str],
    jornada: int,
    del_dia: list[dict] | None = None,
    media: float | None = None,
) -> list[str]:
    """Quién abrió la jornada —y si lo hace por costumbre— y quién la cerró muy tarde.

    Y si quien cerró **además clavó la nota**, se dice de otra manera: llegar tarde es un chiste y llegar
    tarde habiendo visto lo que hacían los demás es otro, mejor. Ese segundo vivía en `comentarios.py`
    apoyado en `created_at` —la hora en que el cron escribió la fila, por lotes cada hora— y aquí se mide con
    la hora real del canal, que es la única que sostiene la insinuación.
    """
    from refranero import APERTURA_HABITUAL, APERTURA_SUELTA, CIERRE_TARDIO, CIERRE_TARDIO_CON_SUERTE
    from voz import _del_ciclo, con_nombre

    publicacion = getattr(senales, "publicacion", None) or {}
    if len(publicacion) < 2:
        return []

    orden = sorted(publicacion.items(), key=lambda par: par[1])
    primero, cuando_primero = orden[0]
    lineas: list[str] = []

    veces = (getattr(senales, "aperturas", None) or {}).get(primero, 0)
    total = getattr(senales, "jornadas_vistas", 0) or 0
    if total >= 5 and veces >= max(2, total * COSTUMBRE):
        lineas.append(
            _del_ciclo(APERTURA_HABITUAL, jornada).format(
                jugador=nombres.get(primero, primero), veces=veces, total=total
            )
        )
    else:
        lineas.append(con_nombre(_del_ciclo(APERTURA_SUELTA, jornada), nombres.get(primero, primero)))

    ultimo, cuando_ultimo = orden[-1]
    retraso = (cuando_ultimo - cuando_primero) / 60
    if retraso >= CIERRE_TARDE:
        horas = f"{retraso / 60:.0f} horas".replace(".0", "")
        nombre_ultimo = nombres.get(ultimo, ultimo)
        suya = next(
            (f["score"] for f in (del_dia or []) if _nombre(f) == nombre_ultimo),
            None,
        )
        con_suerte = suya is not None and media is not None and suya <= media - VENTAJA_DEL_REZAGADO
        registro = CIERRE_TARDIO_CON_SUERTE if con_suerte else CIERRE_TARDIO
        lineas.append(
            _del_ciclo(registro, jornada).format(jugador=nombre_ultimo, horas=horas, dato=suya or 0)
        )
    return lineas


def _linea_de_ausentes(senales, habituales: list[str], nombres: dict[str, str], jornada: int) -> str:
    """Quién no se ha presentado, con hasta tres nombres y el resto resumido.

    Se deriva de que **no hay mensaje suyo en el canal**, no de la tabla: la tabla no distingue «no jugó» de
    «jugó y aún no se ha ingerido».

    Los nombres salen **por orden de clasificación**, así que los tres que se nombran son los tres mejor
    situados que faltan y el resto queda en la coleta. Antes iban por orden alfabético, que nombraba a quien
    tuviera la inicial más baja.
    """
    from refranero import AUSENTES_DEL_DIA
    from voz import _del_ciclo

    publicacion = getattr(senales, "publicacion", None) or {}
    if not publicacion:
        return ""
    # **En orden de clasificación, no alfabético.** `habituales` llega ya ordenado del mejor al peor —es la
    # clasificación—, así que basta con no destruir ese orden: la ausencia del primero es más noticia que la
    # del duodécimo, y con `sorted()` salían por la inicial del nombre. Decisión del dueño.
    faltan = [nombres.get(j, j) for j in habituales if j not in publicacion]
    if not faltan:
        return ""

    visibles = faltan[:AUSENTES_NOMBRADOS]
    sobran = len(faltan) - len(visibles)
    # Con coleta, los nombres van con comas: `_y` pondría un «y» y saldrían dos seguidas —«Cata y Clara C y
    # uno más»—. Lo delató el mensaje compuesto.
    resto = "" if not sobran else (" y uno más" if sobran == 1 else f" y otros {sobran}")
    listado = ", ".join(visibles) if sobran else _y(visibles)
    return _del_ciclo(AUSENTES_DEL_DIA, jornada).format(jugador=listado, resto=resto)


def bloque_la_jornada(
    resultados: list[dict], temporada: str, jornada: int, senales=None, tono=None
) -> str:
    """La jornada contada, en formato de lista y **con una sola voz**.

    Tres reglas la sostienen, y las tres salieron de leer el mensaje en conjunto:

    **Un estado de ánimo por jornada.** Antes cada pieza elegía su frase de su propio registro sin saber qué
    habían elegido las demás, así que salía una línea sarcástica, otra celebratoria y un cierre resignado: el
    mensaje sonaba a tres personas escribiendo por turnos. Ahora la pulla, el conector y el cierre vienen del
    mismo estado.

    **Lo más notable abre.** El orden era fijo —dificultad, mejores, dibujo, horarios, ausentes— y el titular
    del día podía aparecer en la séptima línea. Manda la misma tabla de notabilidad que ya usan los
    comentarios.

    **La segunda línea se encadena con la primera** si habla de la misma persona, con un conector del estado.
    Es lo que convierte una lista de datos en alguien con una idea en la cabeza.
    """
    from comentarios import dificultad, frase as frase_de_hecho, hechos_elegidos
    from refranero import (
        DIBUJO_DEL_DIA,
        DIBUJO_DEL_DIA_CULO,
        DIBUJO_DEL_DIA_CULO_VARIOS,
        DIBUJO_DEL_DIA_VARIOS,
        MEJORES_DEL_DIA,
        MEJORES_DEL_DIA_VARIOS,
    )
    from voz import _concordado, _del_ciclo, conector, estado_de_animo

    del_dia = _del_dia(resultados, jornada)
    if not del_dia:
        return ""

    tabla = clasificacion(resultados, temporada)
    con_puesto = [fila for fila in tabla if fila.get("posicion")]
    nombres = {fila["slack_user_id"]: _nombre(fila) for fila in resultados}

    hoy = dificultad(del_dia)
    media = _media_de_dificultades(resultados, temporada)
    mejor = min(fila["score"] for fila in del_dia)
    estado = estado_de_animo(hoy, media, mejor)

    quienes = sorted({_nombre(fila) for fila in del_dia if fila["score"] == mejor})
    protagonistas = set(quienes)
    # **Con tope.** Hoy empataron siete de once en 3 y la línea los nombraba a todos: nombrar a siete no
    # distingue a nadie, y la línea crecía con el grupo — lo mismo que ya se limitó en los ausentes y en el
    # empate de aplaudidos. Por encima del tope se nombran unos pocos y se cuenta el resto.
    if len(quienes) > AUSENTES_NOMBRADOS:
        visibles = quienes[:AUSENTES_NOMBRADOS]
        quienes_texto = f"{', '.join(visibles)} y {len(quienes) - len(visibles)} más"
    else:
        quienes_texto = _y(quienes)

    # Las piezas, cada una con su prioridad. La pulla del sospechoso va primera cuando existe: es de lo único
    # que el grupo va a hablar.
    # `(prioridad, texto, protagonistas, reconocimiento)`. El último campo solo lo llevan las piezas que
    # premian a alguien: son las únicas que se pueden fusionar.
    piezas: list[tuple[int, str, set[str], str]] = []

    for hecho in hechos_elegidos(resultados, temporada, jornada):
        # **«Día fino de X» no se dice si X ya tiene la mejor nota**: es el mismo elogio con otras palabras, y
        # el mensaje acabaría felicitando dos veces por lo mismo en dos viñetas seguidas.
        if hecho.clave == "sembrado" and hecho.jugador in protagonistas:
            continue
        prioridad = 0 if hecho.clave in ("sospechoso", "clavada") else 4
        texto = frase_de_hecho(hecho.clave, jornada, hecho.jugador, hecho.dato, hecho.varios)
        piezas.append((prioridad, texto, {hecho.jugador}, ""))

    piezas.append((
        1,
        # Concuerda con cuántos son: el 62% de las jornadas tiene empate en la mejor nota, así que el plural
        # es el caso normal y no la excepción.
        _concordado(MEJORES_DEL_DIA, MEJORES_DEL_DIA_VARIOS, jornada, len(quienes)).format(
            jugador=quienes_texto, intentos=mejor
        ),
        protagonistas,
        "mejores",
    ))

    obra = _obra_del_dia(resultados, temporada, jornada)
    if obra:
        categoria = obra[0][1]
        fila = obra[0][0]
        nombres_de_la_obra = [_nombre(f) for f, _ in obra]
        from figures import emoji

        piezas.append((
            2,
            # El melocotón tiene su propio registro: con el genérico salía «un 🍑 que le costó 5 intentos»,
            # que desperdicia la broma. Los comentarios de dibujo llevan nombre desde siempre, así que este
            # también.
            # Y concuerda con cuántos lo comparten: una jornada de cada cuatro tiene empate en la obra.
            _concordado(
                DIBUJO_DEL_DIA_CULO if categoria == CULO else DIBUJO_DEL_DIA,
                DIBUJO_DEL_DIA_CULO_VARIOS if categoria == CULO else DIBUJO_DEL_DIA_VARIOS,
                jornada,
                len(nombres_de_la_obra),
            ).format(
                jugador=_y(nombres_de_la_obra), emoji=emoji(categoria), intentos=fila["score"]
            ),
            set(nombres_de_la_obra),
            "dibujo",
        ))

    if hoy is not None and media is not None:
        piezas.append((3, _linea_de_dificultad(hoy, media, jornada), set(), ""))

    # `del_dia` y `hoy` **hacen falta**: sin ellos la mención del que cierra tarde no puede distinguir si
    # además clavó la nota. Se quedaron sin pasar en un replace que falló en silencio, y la variante «con
    # suerte» era inalcanzable en producción aunque su test estuviera en verde.
    for texto in _linea_de_horarios(senales, nombres, jornada, del_dia, hoy):
        piezas.append((5, texto, set(), ""))

    ausentes = _linea_de_ausentes(
        senales, [fila["jugador"] for fila in con_puesto], nombres, jornada
    )
    if ausentes:
        piezas.append((6, ausentes, set(), ""))

    for clave, texto, quien in menciones_del_canal(senales, nombres, jornada, tono):
        piezas.append((7, texto, quien, clave))

    # De qué iba el hilo, pegado a la mención que lo nombra. Va sin reconocimiento —el último campo vacío—
    # porque no es un premio: fusionarlo con los elogios de esa misma persona sería volver a celebrarlo.
    autor_del_hilo = _autor_del_hilo(tono, nombres)
    if autor_del_hilo:
        del_hilo = frase_del_hilo(tono, autor_del_hilo, jornada)
        if del_hilo:
            piezas.append((8, f"🤨 {del_hilo}", {autor_del_hilo}, ""))

    piezas.sort(key=lambda pieza: pieza[0])
    piezas = _fusiona_reconocimientos(piezas, jornada, {"mejores": mejor})
    lineas = [texto for _, texto, _, _ in piezas]

    # **El encadenado.** Solo la segunda línea, y solo si habla de quien abre: un conector delante de una
    # línea que cambia de sujeto suena a error, no a narración.
    if len(piezas) > 1 and piezas[1][2] & piezas[0][2]:
        lineas[1] = f"{conector(estado, jornada)} {_en_minuscula(lineas[1], nombres.values())}"

    return "\n".join(f"• {linea}" for linea in lineas)


def _en_minuscula(frase: str, nombres) -> str:
    """La frase con la inicial en minúscula, **salvo que empiece por un nombre propio**.

    Tras un conector la oración continúa, así que «Hoy ha ido rodada» pasa a «y hoy ha ido rodada». Pero
    minusculizar a ciegas publicaba «Faltaba decir que claire se lleva la jornada», y el nombre de una
    compañera en minúscula es justo el detalle que delata que el texto lo escribe una máquina.
    """
    # **Se compara el arranque de la frase, no su primera palabra.** Media liga tiene nombre compuesto
    # —«Andrés R.», «Dani Sanchez», «Juan (Kokuma)»— así que mirar solo la primera palabra dejaba fuera a
    # todos ellos y les bajaba la inicial. Lo cazó el test del caso con punto dentro.
    if any(nombre and frase.startswith(nombre) for nombre in nombres):
        return frase
    return frase[0].lower() + frase[1:]


def menciones_del_canal(
    senales, nombres: dict[str, str], jornada: int, tono=None
) -> list[tuple[str, str, set[str]]]:
    """Las menciones del canal como `(clave, texto, protagonistas)`.

    Devuelve también **de quién habla** cada una porque es lo que permite fusionar en una línea los
    reconocimientos de la misma persona. Antes solo devolvía el texto, así que el mensaje no podía saber que
    la ovación y el mejor dibujo eran del mismo y la nombraba dos veces.
    """
    from voz import menciones, protagonistas_de_menciones

    reacciones = getattr(senales, "reacciones", None) or {}
    respuestas = getattr(senales, "respuestas", None) or {}
    dichas = menciones(
        reacciones=reacciones,
        respuestas=respuestas,
        publicacion={},
        nombres=nombres,
        jornada=jornada,
    )
    quienes = protagonistas_de_menciones(reacciones, respuestas, nombres)
    # **Un recuento alto de respuestas deja de valer por sí mismo.** Medido en la jornada que motivó esto: el
    # resultado más comentado tenía 26 respuestas y cero reacciones mientras el resto del día repartía 46, y
    # el mensaje coronó como triunfador a quien el grupo estaba acusando. Si el hilo fue una acusación, la
    # mención no sale: lo que se dice de esa persona lo dice la frase del hilo, que sí sabe de qué iba.
    publicables = ["aplaudido", "comentado"]
    if tono is not None and getattr(tono, "acusacion", False):
        publicables.remove("comentado")
    return [
        (clave, dichas[clave], quienes.get(clave, set()))
        for clave in publicables
        if clave in dichas
    ]


#: Qué situación del registro le toca a cada clasificación. El orden importa: una acusación con propuesta de
#: norma encima es su propia situación, y no una acusación cualquiera.
def _situacion_del_hilo(tono) -> str | None:
    if tono.acusacion:
        return "acusacion-con-propuesta" if tono.propuesta else "acusacion"
    if tono.tono in ("incredulidad", "pique"):
        return tono.tono
    return None


def _autor_del_hilo(tono, nombres: dict[str, str]) -> str | None:
    """De quién era el hilo que se clasificó, con su nombre. **Lo dice el propio tono.**

    Antes se deducía del recuento de respuestas, y estaba mal de dos maneras seguidas. La primera versión
    elegía al más respondido de cualquier mensaje; la segunda lo acotó a quienes habían jugado ese día, y
    seguía mal: el recuento cuenta también la charla, así que respondiendo cincuenta veces a un mensaje
    intrascendente de otra persona se conseguía que el bot **la señalara a ella** por una conversación que
    no era la suya y que nadie había clasificado.

    Deducirlo no vale: el único que sabe de qué hilo se habla es quien lo mandó a clasificar.
    """
    autor = getattr(tono, "autor", None)
    return nombres.get(autor) if autor else None


def frase_del_hilo(tono, jugador: str, jornada: int) -> str | None:
    """La frase que comenta el hilo, o `None` si no hay nada que comentar.

    Devuelve `None` en los tres casos en que hablar sería peor que callar: sin clasificación —la llamada
    falló, o lo que volvió no encajaba en el esquema—, por debajo de la temperatura mínima, y cuando el tono
    no tiene registro propio. Llamar juicio a tres respuestas de cachondeo quema la credibilidad del mensaje
    tan rápido como celebrar una acusación, que es el fallo que este slice viene a arreglar.

    **La frase sale del registro del repositorio.** Del objeto solo se leen sus casillas: ni se concatena
    nada que venga de fuera, ni se usa ningún campo que no esté declarado en `Tono`.
    """
    from refranero import TONO_DEL_HILO
    from tono import INTENSIDAD_MINIMA
    from voz import _del_ciclo

    if tono is None or tono.intensidad < INTENSIDAD_MINIMA:
        return None
    situacion = _situacion_del_hilo(tono)
    if situacion is None:
        return None
    return _del_ciclo(TONO_DEL_HILO[situacion], jornada).format(jugador=jugador, dudan=tono.dudan)


def _fusiona_reconocimientos(
    piezas: list[tuple[int, str, set[str], str]],
    jornada: int,
    datos: dict[str, object] | None = None,
) -> list[tuple[int, str, set[str], str]]:
    """Junta en una línea los reconocimientos de los que alguien es **protagonista único**.

    Cada bloque elige a su mejor candidato por separado, y cuando coincide la misma persona el mensaje la
    nombra una vez por premio: medido en la jornada 1681, alguien salía siete veces y leído junto parecía un
    monográfico. Cada línea era correcta; el conjunto, no.

    **No se reparten los premios a otra gente.** Ceder el mejor dibujo al segundo para que el mensaje hable de
    más personas sería falsear quién ganó qué. Lo que se hace es decirlo una sola vez.

    Se exige **protagonista único**: si la mejor nota la comparten tres, esa línea no entra en la fusión,
    porque «la mejor nota» dejaría de ser cierto para quien la comparte.
    """
    from refranero import DIA_DE, LOGROS_DEL_DIA
    from voz import _del_ciclo

    datos = datos or {}
    unicos: dict[str, list[int]] = {}
    for indice, (_, _, protagonistas, reconocimiento) in enumerate(piezas):
        if reconocimiento in LOGROS_DEL_DIA and len(protagonistas) == 1:
            unicos.setdefault(next(iter(protagonistas)), []).append(indice)

    fusionables = {quien: indices for quien, indices in unicos.items() if len(indices) > 1}
    if not fusionables:
        return piezas

    # Solo se fusiona a una persona por mensaje: dos líneas «Día de X» y «Día de Y» seguidas serían el mismo
    # problema con otra cara. Se elige quien más acumule, y a igualdad la primera por orden de aparición.
    quien, indices = max(fusionables.items(), key=lambda par: (len(par[1]), -par[1][0]))
    logros = [
        LOGROS_DEL_DIA[piezas[i][3]].replace("{dato}", str(datos.get(piezas[i][3], "")))
        for i in indices
    ]
    linea = _del_ciclo(DIA_DE, jornada).format(jugador=quien, logros=_y(logros))

    resultado = [pieza for i, pieza in enumerate(piezas) if i not in set(indices)]
    resultado.insert(0, (piezas[indices[0]][0], linea, {quien}, ""))
    return resultado


def bloque_relevo(resultados: list[dict], temporada: str, jornada: int) -> str:
    """El relevo en cabeza, **si la jornada de hoy lo ha provocado**.

    Se detecta comparando el marcador con y sin los resultados de hoy, así que **no hace falta guardar
    historia**: es cálculo puro, da lo mismo cuantas veces se repita y no depende de que la instantánea
    anterior siga existiendo. Guardar «quién lideraba ayer» habría sido un estado que mantener, y este
    proyecto ya tuvo un payload sobrescrito por una copia vieja.

    Si el líder cambia se anuncia, y si no, no se publica nada: inventar un relevo donde no lo hubo sería
    contar mal la jornada. La regla de cuándo cuenta vive en `hay_relevo`.
    """
    from refranero import CAMBIO_DE_LIDER
    from voz import _del_ciclo, con_nombre

    if not _del_dia(resultados, jornada):
        return ""

    previos = [r for r in resultados if r["wordle_id"] != jornada]
    relevo = hay_relevo(
        [f for f in clasificacion(previos, temporada) if f.get("posicion")],
        [f for f in clasificacion(resultados, temporada) if f.get("posicion")],
        len({r["wordle_id"] for r in previos}),
    )
    if not relevo:
        return _dominio(resultados, temporada, jornada)

    nuevo, anterior = relevo
    plantilla = _del_ciclo(CAMBIO_DE_LIDER, jornada)
    linea = con_nombre(plantilla.replace("{nuevo}", nuevo).replace("{anterior}", "{jugador}"), anterior)
    return " ".join(x for x in (linea, _tendencia_del_mes(resultados, temporada, jornada, nuevo, anterior)) if x)


def _tendencia_del_mes(resultados, temporada, jornada, nuevo: str, anterior: str) -> str:
    """El contexto del mes que se le añade al relevo: cuántas veces ha cambiado la cabeza y el reparto.

    **Va pegado al relevo y no tiene línea propia.** Simulada como línea diaria salía desde la tercera jornada
    del mes, se repetía casi idéntica varios días y llegó a decir «lleva 7 jornadas mandando» de quien ya no
    mandaba. Pegada al relevo solo aparece cuando de verdad ha cambiado algo.

    El reparto nombra a **los dos del relevo**, no a los dos con más jornadas acumuladas: en una jornada real
    el top-2 acumulado decía «Andrés R. 7 · Dani Sanchez 1» el día que la cabeza se la jugaban Andrés R. y
    Claire, dejando fuera a quien acababa de cogerla.
    """
    from refranero import TENDENCIA_DEL_MES
    from voz import _del_ciclo

    historia = historia_del_liderazgo(resultados, temporada, jornada)
    # Con un solo cambio el relevo ya lo dice todo; «y van 1 cambios» no es una tendencia.
    if historia["cambios"] < 2:
        return ""
    dias = historia["jornadas"]
    reparto = " · ".join(f"{quien} {dias.get(quien, 0)}" for quien in (nuevo, anterior))
    return _del_ciclo(TENDENCIA_DEL_MES, jornada).format(cambios=historia["cambios"], reparto=reparto)


def _dominio(resultados: list[dict], temporada: str, jornada: int) -> str:
    """El caso opuesto al relevo: nadie le quita la cabeza a alguien desde hace jornadas.

    Ocupa **el mismo hueco** que el relevo, así que el mensaje nunca lleva dos líneas de liderazgo: o ha
    cambiado la cabeza, o alguien lleva mucho sin soltarla, pero no las dos cosas.

    Cuenta jornadas **seguidas**, y solo con un líder único: «lleva 6 jornadas sin soltar la cabeza» dicho de
    dos personas empatadas no es dominio de nadie.
    """
    from refranero import DOMINIO
    from voz import _del_ciclo, con_nombre

    historia = historia_del_liderazgo(resultados, temporada, jornada)
    if historia["racha"] < RACHA_PARA_DOMINIO or len(historia["lideres"]) != 1:
        return ""
    plantilla = _del_ciclo(DOMINIO, jornada).replace("{racha}", str(historia["racha"]))
    return con_nombre(plantilla, historia["lideres"][0])


#: A partir de cuántos empates de la misma pareja se insiste, y a partir de cuántos se habla de tensión.
#:
#: Los cortes salen del reparto real: la recurrencia llega a 2, 3 y 4 en las dos temporadas, y 4 es el techo
#: en 195 jornadas. Con estos cortes agosto reparte los cuatro empates de Andrés R. y Claire en neutro,
#: insistente, insistente y tenso, en vez de repetir la misma frase cuatro veces.
EMPATES_PARA_INSISTIR = 2
EMPATES_PARA_TENSION = 4

#: Jornadas seguidas en cabeza a partir de las cuales se comenta el dominio. Cinco: en agosto lo alcanzó una
#: sola vez en catorce jornadas, así que distingue al que se instala arriba sin salir cada dos días.
RACHA_PARA_DOMINIO = 5


def historia_del_liderazgo(resultados: list[dict], temporada: str, jornada: int) -> dict:
    """Cuántas veces ha cambiado la cabeza, quién ha liderado cuántas jornadas y la racha actual.

    Se **deriva** recorriendo las jornadas hasta la de hoy, sin guardar nada: medido, recalcular el marcador en
    cada jornada cuesta 0,02 s para un mes y 0,23 s para las 181 del histórico, así que persistir esta historia
    sería estado que mantener a cambio de nada — y este proyecto ya tuvo un payload sobrescrito por una copia
    vieja.

    `racha` cuenta jornadas **seguidas** con la misma cabeza. La distinción importa: la primera versión de esto
    mezclaba total acumulado con racha y publicaba «lleva 7 jornadas mandando» mientras mandaba otra persona.
    """
    jornadas = sorted({fila["wordle_id"] for fila in resultados_de_temporada(resultados, temporada)
                       if fila["wordle_id"] <= jornada})
    cambios, racha = 0, 0
    jornadas_liderando: dict[str, int] = {}
    # Cuántas jornadas ha tenido exactamente esta cabeza, para saber si el empate de hoy se repite.
    cabezas: dict[tuple[str, ...], int] = {}
    anterior: list[str] | None = None

    for cada in jornadas:
        previos = [fila for fila in resultados if fila["wordle_id"] < cada]
        hasta = [fila for fila in resultados if fila["wordle_id"] <= cada]
        tabla = [f for f in clasificacion(hasta, temporada) if f.get("posicion")]
        if not tabla:
            continue
        lideres = sorted(f["nombre"] for f in tabla if f["posicion"] == tabla[0]["posicion"])
        # **Se cuenta lo que se anuncia**, y por eso pasa por `hay_relevo` en lugar de comparar los dos
        # conjuntos de líderes: comparándolos, agosto daba «3 cambios de cabeza» el día del primer relevo
        # anunciado, porque contaba también el empate alternando entre dos igualados —que a propósito no se
        # anuncia—. El grupo habría leído un número que no corresponde a nada que se le haya contado.
        relevo = hay_relevo(
            [f for f in clasificacion(previos, temporada) if f.get("posicion")],
            tabla,
            len({fila["wordle_id"] for fila in previos}),
        )
        if relevo:
            cambios += 1
            racha = 1
        elif anterior is not None and set(lideres) != set(anterior):
            # Cambió quién está arriba sin que sea un relevo anunciable: la racha se corta igual, porque
            # «lleva N jornadas sin soltar la cabeza» sería falso si la soltó.
            racha = 1
        else:
            racha += 1
        anterior = lideres
        cabezas[tuple(lideres)] = cabezas.get(tuple(lideres), 0) + 1
        for quien in lideres:
            jornadas_liderando[quien] = jornadas_liderando.get(quien, 0) + 1

    return {
        "cambios": cambios,
        "jornadas": jornadas_liderando,
        "racha": racha,
        "lideres": anterior or [],
        "veces_esta_cabeza": cabezas.get(tuple(anterior), 0) if anterior else 0,
    }


def hay_relevo(antes: list[dict], ahora: list[dict], jornadas_previas: int) -> tuple[str, str] | None:
    """`(nuevo, anterior)` si la jornada ha cambiado quién manda, o `None`.

    **Separada de los datos a propósito.** Vivía dentro de `bloque_relevo` y sus dos guardas no había manera
    de probarlas con resultados sintéticos: para llegar a ellas hace falta una combinación muy concreta de
    medias y participaciones, así que los tests pasaban sin ejercitarlas y la prueba de mutación las tumbaba
    las dos. Recibiendo las clasificaciones ya hechas, la regla se comprueba tal cual es.

    **Hacen falta jornadas previas de verdad.** En la primera de una temporada, quitar la de hoy deja un
    marcador que no representa nada y cualquier orden parece un relevo — así se anunciaba uno en la jornada de
    estreno del mes.

    **Y no vale si están empatados.** Con la misma media, quién sale primero lo decide el desempate por
    participación, así que el «relevo» sería el orden alternando por ruido. Medido sobre agosto: con los dos de
    cabeza clavados, se anunciaba en **diez de diez** jornadas. Ese empate lo cuenta `bloque_rivalidad`.
    """
    if jornadas_previas < JORNADAS_PARA_HABLAR_DE_RELEVO or not antes or not ahora:
        return None

    lider_antes, lider_ahora = antes[0], ahora[0]
    if lider_antes["nombre"] == lider_ahora["nombre"]:
        return None

    suya = next((f for f in ahora if f["nombre"] == lider_antes["nombre"]), None)
    if suya and suya["media_temporada"] == lider_ahora["media_temporada"]:
        return None

    return lider_ahora["nombre"], lider_antes["nombre"]


def bloque_rivalidad(resultados: list[dict], temporada: str, jornada: int) -> str:
    """La pelea por el primer puesto, **si la hay**.

    Con ventaja amplia no sale nada: inventar una rivalidad donde alguien va destacado sería contar mal la
    temporada, y el mensaje ya tiene bastantes líneas.

    Se lee de `posicion`, no del orden de la lista. Es el mismo error que la web publicaba en su titular —
    tomar el segundo elemento del array como «el segundo» y restar las medias— y que con un empate en cabeza
    producía «le sigue a 0,00».
    """
    from refranero import (
        RIVALIDAD_EMPATE,
        RIVALIDAD_EMPATE_OTRA_VEZ,
        RIVALIDAD_EMPATE_TENSION,
        RIVALIDAD_MONTON,
        RIVALIDAD_PELEA,
    )
    from voz import _del_ciclo, sin_punto_doble

    filas = [fila for fila in clasificacion(resultados, temporada) if fila["clasificado"]]
    if len(filas) < 2:
        return ""

    lider = filas[0]
    empatados = [fila for fila in filas if fila["posicion"] == lider["posicion"]]
    nota = _cifra(lider["media_temporada"])

    if len(empatados) == 2:
        # **La tensión escala por recurrencia, no por duración.** Medido: los empates consecutivos casi no
        # existen (los cinco de agosto duran una jornada; de las doce rachas del histórico, once duran una).
        # Lo que se repite es la misma pareja empatando en jornadas salteadas, y eso llega a cuatro veces.
        veces = historia_del_liderazgo(resultados, temporada, jornada)["veces_esta_cabeza"]
        registro = (
            RIVALIDAD_EMPATE_TENSION if veces >= EMPATES_PARA_TENSION
            else RIVALIDAD_EMPATE_OTRA_VEZ if veces >= EMPATES_PARA_INSISTIR
            else RIVALIDAD_EMPATE
        )
        return sin_punto_doble(_del_ciclo(registro, jornada).format(
            a=empatados[0]["nombre"], b=empatados[1]["nombre"], cifra=nota, veces=veces
        ))
    if len(empatados) > 2:
        return sin_punto_doble(
            _del_ciclo(RIVALIDAD_MONTON, jornada).format(cuantos=len(empatados), cifra=nota)
        )

    siguiente = next((fila for fila in filas if fila["posicion"] != lider["posicion"]), None)
    if not siguiente:
        return ""
    ventaja = siguiente["media_temporada"] - lider["media_temporada"]
    if ventaja > VENTAJA_MINIMA:
        return ""
    return sin_punto_doble(_del_ciclo(RIVALIDAD_PELEA, jornada).format(
        a=lider["nombre"], b=siguiente["nombre"], cifra=_cifra(ventaja)
    ))


def _cifra(valor: float) -> str:
    """Con coma decimal. La web ya lo hace con `toLocaleString("es-ES")`, y el mensaje va al mismo grupo:
    un 3.20 en Slack y un 3,20 en la web son el mismo número escrito de dos formas."""
    return f"{valor:.2f}".replace(".", ",")


def _etiqueta(resultados: list[dict], temporada: str) -> str:
    from seasons import etiqueta

    return etiqueta(temporada)


def tira(recuento: dict[str, int], categorias: list[dict]) -> str:
    """La tira agrupada, en texto: `🦜8 🌷60 📐3 🌀15`.

    Agrupada y no repitiendo emojis, igual que en la web: con 135 partidas la tira literal no cabe en un
    mensaje de Slack ni se lee.
    """
    return " ".join(
        f"{entrada['emoji']}{recuento.get(entrada['clave'], 0)}"
        for entrada in categorias
        if recuento.get(entrada["clave"], 0)
    )


#: Debutantes que hacen noticia una jornada. Uno se da la bienvenida a sí mismo en el canal; tres son una ola.
DEBUTANTES_NOTICIA = 3

#: Cuánto por encima de lo normal es «mucha más gente»: un cuarto más que la mediana.
AFLUENCIA_NOTICIA = 1.25

#: Las jornadas de temporada anteriores contra las que se mide lo normal: un mes de laborables, más o menos.
JORNADAS_DE_REFERENCIA = 20

#: Debutantes que se nombran antes de resumir el resto con «y N más»: el mensaje no crece con el grupo.
NOMBRES_DE_BIENVENIDA = 3

#: La coletilla del día de mucha gente. **Rota por jornada** (`_del_ciclo`), así que dos días seguidos de
#: récord no repiten. Referencias pop que el grupo reconoce, y ninguna se ríe de nadie: se ríen de la cola.
COLETILLAS_DE_PARTICIPACION = (
    "Primera regla del club del Wordle: no se hace spoiler de la palabra.",
    "Ni el reencuentro de OT juntó a tanta gente.",
    "Esto ya no es un canal, es el Bernabéu en noche de Champions.",
    "Somos legión. La media del grupo lo va a notar.",
    "La mesa del Wordle es como la de Nochebuena: siempre cabe uno más.",
    "This is fine 🔥: el canal a reventar y el bot aguantando.",
)


def bloque_participacion(resultados: list[dict], jornada: int) -> str:
    """Cuántos han jugado, **solo si es noticia**: récord del canal, una ola de debutantes o mucha más gente
    de lo normal (decisión del dueño, 2026-10-02). Un día como los demás no lo menciona.

    Lo normal es la mediana de las últimas `JORNADAS_DE_REFERENCIA` jornadas que cuentan para una temporada
    —laborables con muestra—, para que un sábado de tres no lo rebaje. Sin jornadas anteriores no hay
    con qué comparar, y el bloque no sale: el primer día del canal todos serían debutantes y récord.
    """
    jugadores_de: dict[int, dict[str, str]] = {}
    fecha_de: dict[int, str] = {}
    debut: dict[str, int] = {}
    for fila in resultados:
        jugadores_de.setdefault(fila["wordle_id"], {})[fila["slack_user_id"]] = fila.get("player_name") or fila["slack_user_id"]
        fecha_de[fila["wordle_id"]] = fila["date"]
        debut[fila["slack_user_id"]] = min(debut.get(fila["slack_user_id"], fila["wordle_id"]), fila["wordle_id"])

    hoy = jugadores_de.get(jornada, {})
    anteriores = sorted(j for j in jugadores_de if j < jornada)
    referencia = [
        len(jugadores_de[j]) for j in anteriores
        if es_laborable(fecha_de[j]) and len(jugadores_de[j]) >= MUESTRA_MINIMA_DEL_DIA
    ][-JORNADAS_DE_REFERENCIA:]
    if not hoy or not referencia:
        return ""

    cuantos = len(hoy)
    record = cuantos > max(len(jugadores_de[j]) for j in anteriores)
    # La mediana de verdad: con un número par de jornadas, la superior hacía el umbral más alto de la cuenta.
    normal = statistics.median(referencia)
    debutantes = sorted((nombre for jugador, nombre in hoy.items() if debut[jugador] == jornada), key=str.casefold)
    if not (record or len(debutantes) >= DEBUTANTES_NOTICIA or cuantos >= AFLUENCIA_NOTICIA * normal):
        return ""

    lineas = [f"👥 *{cuantos} jugadores hoy*{', récord del canal' if record else ''} (lo normal: {int(normal + 0.5)})."]
    if debutantes:
        nombrados = debutantes[:NOMBRES_DE_BIENVENIDA]
        resto = len(debutantes) - len(nombrados)
        nombres = f"{', '.join(nombrados)} y {resto} más" if resto else nombres_unidos(nombrados)
        verbo = "Debuta" if len(debutantes) == 1 else f"Debutan {len(debutantes)}"
        bienvenida = concuerda(f"¡Bienvenid{HUECO}{'' if len(debutantes) == 1 else 's'}!", debutantes)
        lineas.append(f"{verbo}: {nombres}. {bienvenida}")
    lineas.append(f"_{COLETILLAS_DE_PARTICIPACION[jornada % len(COLETILLAS_DE_PARTICIPACION)]}_")
    return "\n".join(lineas)


def bloque_album(resultados: list[dict], temporada: str) -> str:
    """Los tres primeros del ranking de belleza con su puntuación media.

    Vacío si nadie está clasificado. Va en lista, como el juego: el dibujo es del marcador general.
    """
    datos = album(resultados, temporada)
    puestos = [
        {"posicion": fila["posicion"], "nombre": fila["nombre"], "cifra": f"{_cifra(fila['media'])} pts"}
        for fila in datos["jugadores"]
        if fila["clasificado"] and fila["posicion"] <= CABEZA_DEL_ALBUM
    ]
    return lista_de_texto("🎨 *Ranking de figuras*", puestos)


#: Jornadas del principio del mes en las que el resumen dice que el mes arranca.
JORNADAS_DE_ARRANQUE = 3

#: Laborables que tienen que quedar en el mes, como mucho, para que empiece la recta final: las cinco últimas
#: jornadas son la de hoy y las cuatro que quedan.
LABORABLES_DE_RECTA_FINAL = 4


def _fecha_de(resultados: list[dict], jornada: int) -> datetime.date | None:
    fecha = next((fila["date"] for fila in resultados if fila["wordle_id"] == jornada), None)
    return datetime.date.fromisoformat(str(fecha)[:10]) if fecha else None


def _laborables_del_mes(desde: datetime.date, incluido: bool) -> int:
    """Los laborables que quedan en el mes de `desde`, contándolo o no. Con el calendario, no con el reloj:
    los festivos no se conocen y cuentan como laborables."""
    ultimo = calendar.monthrange(desde.year, desde.month)[1]
    primero = desde.day if incluido else desde.day + 1
    return sum(1 for dia in range(primero, ultimo + 1) if desde.replace(day=dia).weekday() < 5)


#: Nombres que se escriben en una línea del momento del mes antes de resumir el resto con «y N más». Un empate
#: de muchos en cabeza no puede alargar el mensaje con el grupo.
NOMBRES_EN_UNA_LINEA = 3


def _nombres(filas: list[dict]) -> str:
    nombres = [fila["nombre"] for fila in filas]
    if len(nombres) > NOMBRES_EN_UNA_LINEA:
        return ", ".join(nombres[:NOMBRES_EN_UNA_LINEA]) + f" y {len(nombres) - NOMBRES_EN_UNA_LINEA} más"
    return _y(nombres)


def _cabeza_y_siguientes(tabla: list[dict]) -> tuple[list[dict], list[dict]]:
    """Todos los del primer puesto y **todos** los del siguiente: con un empate en el 2º, nombrar solo al primero
    de la lista era contar la mitad."""
    if not tabla:
        return [], []
    cabeza = [fila for fila in tabla if fila["posicion"] == tabla[0]["posicion"]]
    resto = [fila for fila in tabla if fila["posicion"] > tabla[0]["posicion"]]
    siguientes = [fila for fila in resto if fila["posicion"] == resto[0]["posicion"]] if resto else []
    return cabeza, siguientes


def _tension_del_juego(resultados, temporada, jornada, fecha, niveles, marcas) -> str:
    """La línea del SuperWordleBros en la recta final: cuántos puntos quedan en juego y si el segundo llega.

    **Aquí sí se puede calcular**, y se calcula como cota exacta. Cada nivel por jugar da hasta 10 al segundo y
    nada al líder. El nivel **abierto** es distinto: ya tiene marcas contadas y sigue admitiéndolas, así que el
    segundo puede subir hasta 10 desde lo que tenga en él y el líder, si ya tiene marca, caer hasta 1. Contarlo
    como 10 limpios decía «ya no puede» cuando sí podía (lo cazó el Gate 4d).
    """
    tabla = clasificacion_del_juego(resultados, list(niveles), list(marcas), temporada)["clasificacion"]
    if len(tabla) < 2:
        return ""
    abierto = _nivel_del_dia(niveles, jornada)
    abierto_cuenta = abierto in niveles_que_puntuan(resultados, list(niveles), temporada)
    # Uno por laborable desde la jornada incluida, **menos el último del mes**: su nivel puntúa en el mes
    # siguiente, que es cuando se juega.
    por_jugar = max(0, _laborables_del_mes(fecha, incluido=True) - 1)
    en_juego = ESCALA[0] * (int(abierto_cuenta) + por_jugar)
    if not en_juego:
        return ""

    cabeza, siguientes = _cabeza_y_siguientes(tabla)
    if len(cabeza) > 1:
        return (
            f"🎮 En el SuperWordleBros quedan {en_juego} puntos en juego y la cabeza está empatada entre "
            f"{_nombres(cabeza)}, a {cabeza[0]['puntos']}."
        )
    primero, segundo = cabeza[0], siguientes[0]
    ventaja = primero["puntos"] - segundo["puntos"]

    vuelco = ESCALA[0] * por_jugar
    if abierto_cuenta:
        del_abierto = puestos_de_nivel([m for m in marcas if m["jornada"] == abierto])
        del_lider = del_abierto.get(primero["jugador"], (None, 0))[1]
        del_segundo = del_abierto.get(segundo["jugador"], (None, 0))[1]
        suelo_del_lider = PUNTOS_DESDE_EL_OCTAVO if primero["jugador"] in del_abierto else 0
        vuelco += (ESCALA[0] - del_segundo) + (del_lider - suelo_del_lider)

    quienes = _nombres(siguientes)
    varios = len(siguientes) > 1
    if ventaja <= vuelco:
        return (
            f"🎮 En el SuperWordleBros quedan {en_juego} puntos en juego: {quienes} todavía "
            f"{'pueden' if varios else 'puede'} alcanzar a {primero['nombre']}, que "
            f"{'les' if varios else 'le'} saca {ventaja}."
        )
    return (
        f"🎮 En el SuperWordleBros quedan {en_juego} puntos en juego y {quienes} ya no "
        f"{'pueden' if varios else 'puede'} alcanzar a {primero['nombre']}, que {'les' if varios else 'le'} saca "
        f"{ventaja}."
    )


def bloque_momento_del_mes(resultados: list[dict], temporada: str, jornada: int, niveles=(), marcas=()) -> str:
    """En qué momento del mes está el resumen: arranque, recta final o última jornada. Vacío a mitad de mes.

    Se decide con **la fecha de la jornada y el calendario** (§10): el mismo resumen sale igual lo ejecute quien
    lo ejecute y cuando lo ejecute.
    """
    from refranero import ARRANQUE_DEL_MES, RECTA_FINAL, ULTIMA_JORNADA
    from voz import _del_ciclo

    fecha = _fecha_de(resultados, jornada)
    if fecha is None or temporada == TEMPORADA_CERO:
        return ""
    quedan = _laborables_del_mes(fecha, incluido=False)

    if quedan > LABORABLES_DE_RECTA_FINAL:
        dias = dias_de_temporada(resultados, temporada)
        if jornada in dias and dias.index(jornada) < JORNADAS_DE_ARRANQUE:
            return "🏁 " + _del_ciclo(ARRANQUE_DEL_MES, jornada)
        return ""

    if quedan == 0:
        lineas = [f"⏳ *Última jornada del mes* — {_del_ciclo(ULTIMA_JORNADA, jornada)}"]
    else:
        cuantas = "queda 1 jornada" if quedan == 1 else f"quedan {quedan} jornadas"
        lineas = [f"⏳ *Recta final* — {cuantas}. {_del_ciclo(RECTA_FINAL, jornada)}"]

    clasificados = [fila for fila in clasificacion(resultados, temporada) if fila["clasificado"]]
    if clasificados:
        cabeza, siguientes = _cabeza_y_siguientes(clasificados)
        media = _cifra(cabeza[0]["media_temporada"])
        if len(cabeza) > 1:
            lineas.append(f"{_nombres(cabeza)} van empatados en cabeza con {media}.")
        elif siguientes:
            # Sobre la media **publicada**: si a la vista van 3,00 y 3,05, la distancia es 0,05 y no 0,0526.
            distancia = _cifra(round(siguientes[0]["media_temporada"], 2) - round(cabeza[0]["media_temporada"], 2))
            verbo = "están" if len(siguientes) > 1 else "está"
            lineas.append(f"{cabeza[0]['nombre']} manda con {media}; {_nombres(siguientes)} {verbo} a {distancia}.")
        lineas.append("Si acaban igualados, comparten el primer puesto.")

    juego = _tension_del_juego(resultados, temporada, jornada, fecha, niveles or (), marcas or ())
    if juego:
        lineas.append(juego)
    return "\n".join(lineas)


def _voz(resultados: list[dict], temporada: str, jornada: int, senales) -> list[str]:
    """La voz de la jornada: menciones del canal, meme y frase, con el tope de añadidos.

    Slice: `voz-de-la-jornada`. Vive aquí y no en `voz.py` porque es el punto donde se cruzan las señales del
    canal con lo que ya sabe la tabla; `voz.py` no conoce ni la tabla ni la temporada.

    `senales` puede ser `None` —canal caído o lectura desactivada— y entonces solo salen el meme y la frase,
    que no dependen del canal. Un canal que no responde no puede impedir que se publique el marcador.
    """
    from comentarios import dificultad
    from voz import anadidos, cierre, estado_de_animo, meme_del_dia

    del_dia = _del_dia(resultados, jornada)
    if not del_dia:
        return []

    filas = [
        {"jugador": fila["slack_user_id"], "nombre": _nombre(fila), "intentos": fila["score"]}
        for fila in del_dia
    ]

    con_puesto = [fila for fila in clasificacion(resultados, temporada) if fila.get("posicion")]
    lider = con_puesto[0]["nombre"] if con_puesto else None
    ultimo = con_puesto[-1]["nombre"] if len(con_puesto) > 1 else None
    mejor = min(fila["score"] for fila in del_dia)
    mejores = sorted({_nombre(fila) for fila in del_dia if fila["score"] == mejor})

    # Las menciones del canal **no salen aquí**: ya son viñetas de `bloque_la_jornada`. Estuvieron un rato en
    # los dos sitios y «Ovación para Claire» se publicaba dos veces en el mismo mensaje.
    return [
        *anadidos(
            meme=meme_del_dia(
                filas,
                jornada,
                lider=lider,
                ultimo=ultimo,
                # Los dibujos de hoy, el tamaño del empate en cabeza y cuánta gente juega la temporada:
                # cuatro formas de meme los necesitan y no se pueden derivar de la jornada sola.
                figuras=_figuras_reconocibles_del_dia(resultados, jornada),
                cuadriculas=sum(1 for f in del_dia if f.get("pattern")),
                empatados_arriba=sum(
                    1 for f in con_puesto if f["posicion"] == con_puesto[0]["posicion"]
                ),
                plantilla=len(con_puesto),
                # Cuántos melocotones hay hoy. Se cuenta aquí porque `voz.py` no conoce el clasificador.
                culos=sum(
                    1
                    for fila in del_dia
                    if fila.get("pattern") and figura(fila["pattern"], jornada) == CULO
                ),
            ),
            menciones={},
            # **Del estado de ánimo**, no del registro de dificultad: es la última pieza con tono del mensaje
            # y tiene que sonar a lo mismo que la pulla y el conector de arriba.
            frase=cierre(
                estado_de_animo(
                    dificultad(del_dia), _media_de_dificultades(resultados, temporada), mejor
                ),
                jornada,
                dato=mejor,
                # A quién nombra el cierre cuando la frase lo pide: quien firmó la mejor nota del día, y
                # **solo si fue una persona**. Con siete empatados la frase cede el turno a la siguiente del
                # registro en lugar de nombrar a una lista.
                jugador=mejores[0] if len(mejores) == 1 else "",
            ),
        ),
    ]


def _manda_en_solitario(filas: list[dict]) -> str:
    """Quien encabeza sin compartir el puesto, o cadena vacía si el primer puesto está empatado.

    **Mira `posicion`, no el orden de la lista.** Es el mismo error que la web publicaba en su titular: tomar
    el primer elemento del array como el líder. Con un empate en cabeza, la pulla coronaba a uno de los dos
    —«X arriba, y los demás mirando el escaparate»— justo al lado del bloque que dice que van clavados. Dos
    líneas del mismo mensaje contradiciéndose.

    Con empate no se dice nada: la pelea ya la cuenta `bloque_rivalidad`, que es su sitio.
    """
    con_puesto = [fila for fila in filas if fila.get("posicion")]
    if not con_puesto:
        return ""
    primeros = [fila for fila in con_puesto if fila["posicion"] == con_puesto[0]["posicion"]]
    return primeros[0]["nombre"] if len(primeros) == 1 else ""


def _pulla_del_marcador(resultados: list[dict], temporada: str, jornada: int) -> str:
    from voz import pullas_de_lideres

    quien = _manda_en_solitario(clasificacion(resultados, temporada))
    return pullas_de_lideres(quien, None, jornada).get("marcador", "") if quien else ""


def _pulla_del_album(resultados: list[dict], temporada: str, jornada: int) -> str:
    from voz import pullas_de_lideres

    quien = _manda_en_solitario(album(resultados, temporada)["jugadores"])
    return pullas_de_lideres(None, quien, jornada).get("album", "") if quien else ""


def bloque_ultima_jornada(resultados: list[dict], temporada: str, jornada: int, palabra=None) -> str:
    """La última jornada del mes en corto, para ir debajo de la victoria: la palabra, el mejor del día y la obra
    del día. La noche del último día la victoria sustituye al resumen, y la jornada que decidió el mes no se
    pierde.
    """
    partes = [
        bloque_palabra(palabra),
        bloque_jugador_del_dia(_del_dia(resultados, jornada)),
        bloque_obra_del_dia(resultados, temporada, jornada),
    ]
    cuerpo = "\n".join(parte for parte in partes if parte)
    return f"📅 *La última jornada*\n{cuerpo}" if cuerpo else ""


def resumen_del_dia(
    resultados: list[dict],
    temporada: str,
    jornada: int,
    senales=None,
    palabra=None,
    tono=None,
    niveles=None,
    marcas=None,
) -> str:
    """El resumen completo. **Una sección sin datos no se imprime**, no se imprime vacía.

    `palabra` es `(palabra, acepcion)` de la jornada, o `None`. Entra por parámetro porque averiguarla es red
    y la red vive en el borde: así el mensaje sigue fijándose en un test. `niveles` y `marcas` son los del
    SuperWordleBros, por lo mismo; sin ellos no sale su podio.

    **Los podios van en orden** —marcador, juego, figuras—, decisión del dueño, y el momento del mes justo
    antes de ellos: es lo que explica cuánto pesa cada ventaja.
    """
    del_dia = _del_dia(resultados, jornada)
    secciones = [
        # **Abre el mensaje.** Es lo único que el grupo no sabe ya: cada uno tiene su resultado, pero la
        # palabra escrita y su significado no los ha visto nadie.
        bloque_palabra(palabra),
        bloque_la_jornada(resultados, temporada, jornada, senales, tono),
        # Cuántos han jugado, solo los días que es noticia: va con la jornada, que es de lo que habla.
        bloque_participacion(resultados, jornada),
        # **Una** línea de cierre —el meme si la jornada tiene forma, y si no el proverbio— entre la jornada y
        # los rankings. Tres frases seguidas era un tercer bloque de comentarios y el mensaje ya tiene dos.
        *_voz(resultados, temporada, jornada, senales),
        bloque_momento_del_mes(resultados, temporada, jornada, niveles or (), marcas or ()),
        bloque_top(resultados, temporada, jornada),
        # El relevo va justo tras el marcador: es lo que explica por qué el orden ha cambiado.
        bloque_relevo(resultados, temporada, jornada),
        # Las pullas van **pegadas a su ranking**, que es lo que comentan. Sueltas al final del comentario
        # nadie sabía a qué se referían.
        _pulla_del_marcador(resultados, temporada, jornada),
        bloque_rivalidad(resultados, temporada, jornada),
        bloque_juego(resultados, temporada, jornada, niveles or (), marcas or ()),
        bloque_album(resultados, temporada),
        _pulla_del_album(resultados, temporada, jornada),
    ]
    return "\n\n".join(seccion for seccion in secciones if seccion)
