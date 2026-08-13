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

from album import album
from comentarios import seccion_de_comentarios
from figures import FIGURAS, figura, rasgos
from standings import clasificacion

#: Cuántos entran en el top del mensaje. Cinco es lo que pide el diseño del resumen.
TOP = 5

#: Cuántos del álbum. Tres: la cabeza, no la tabla — la tabla está en la web.
CABEZA_DEL_ALBUM = 3

#: Límite de `initial_comment` en Slack, para dejar constancia de contra qué se mide.
#:
#: **No hay recorte, y a propósito**: el mensaje está acotado por construcción —dos líneas, cinco del top y
#: tres del álbum— así que no crece con el grupo por muchos jugadores que haya. Se escribió un recorte antes
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
    elegida = _obra_del_dia(resultados, temporada, jornada)
    if not elegida:
        return "🖼️ *Obra del día:* desierta — hoy no ha salido ninguna figura reconocible."
    fila, categoria = elegida
    from figures import emoji

    return f"🖼️ *Obra del día:* {emoji(categoria)} de {_nombre(fila)} ({fila['score']} intentos)."


def _obra_del_dia(resultados: list[dict], temporada: str, jornada: int):
    """La figura premiada del día como `(fila, categoria)`, o `None` si no hay ninguna reconocible.

    Separada del texto para que la use también `bloque_la_jornada` **sin reimplementar el desempate**: la
    regla de qué dibujo gana vive en un solo sitio, y una segunda copia habría divergido en la primera
    recalibración.
    """
    candidatas = [
        (fila, figura(fila["pattern"]))
        for fila in _del_dia(resultados, jornada)
        if fila.get("pattern")
    ]
    reconocibles = [(fila, cat) for fila, cat in candidatas if cat in FIGURAS]
    if not reconocibles:
        return None

    frecuencia = rareza(resultados, temporada)
    return min(
        reconocibles,
        key=lambda par: (
            frecuencia.get(par[1], 0),
            not rasgos(par[0]["pattern"]).espejo,  # el espejo primero
            -par[0]["score"],
            _nombre(par[0]).lower(),
        ),
    )


def _figura_del_dia_por_jugador(resultados: list[dict], jornada: int) -> dict[str, str]:
    from figures import emoji

    dibujos = {}
    for fila in _del_dia(resultados, jornada):
        if fila.get("pattern"):
            dibujos[fila["slack_user_id"]] = emoji(figura(fila["pattern"]))
    return dibujos


def bloque_top(resultados: list[dict], temporada: str, jornada: int) -> str:
    """Los cinco primeros del marcador, con el emoji de lo que dibujó cada uno **hoy**.

    Quien no jugó hoy no lleva emoji: poner el de otro día haría que el resumen contase una jornada que no
    es la de hoy.
    """
    clasificados = [fila for fila in clasificacion(resultados, temporada) if fila["clasificado"]]
    if not clasificados:
        return ""

    # **Se corta por puesto, no por número de filas.** Con puestos compartidos, quedarse con los cinco
    # primeros de la lista puede partir un empate por la mitad y dejar fuera a alguien que va igual que el
    # quinto. Empatar es lo normal: el 62% de las jornadas tiene empate en la mejor nota del día.
    tabla = [fila for fila in clasificados if fila["posicion"] <= TOP]

    dibujos = _figura_del_dia_por_jugador(resultados, jornada)
    lineas = []
    anterior = None
    for fila in tabla:
        # El número solo se escribe cuando cambia: repetir "2º" en dos líneas seguidas se lee como un error
        # de copia; una línea sangrada se lee como lo que es, un empate.
        marca = f"{fila['posicion']}º" if fila["posicion"] != anterior else "  ·"
        anterior = fila["posicion"]
        emoji = f" {dibujos[fila['jugador']]}" if fila["jugador"] in dibujos else ""
        lineas.append(f"{marca} {fila['nombre']} — {_cifra(fila['media_temporada'])}{emoji}")
    return f"📊 *Marcador · {_etiqueta(resultados, temporada)}*\n" + "\n".join(lineas)


#: Ventaja que deja de ser ventaja, en media de intentos por día. Con siete jornadas, 0,15 es un solo intento
#: en todo el mes: quien va segundo lo remonta con una jornada buena. Es el mismo umbral que usa el titular
#: de la web (`v2/js/ui/temporada.js`), y por la misma razón.
VENTAJA_MINIMA = 0.15



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
    """
    from refranero import AUSENTES_DEL_DIA
    from voz import _del_ciclo

    publicacion = getattr(senales, "publicacion", None) or {}
    if not publicacion:
        return ""
    faltan = sorted(nombres.get(j, j) for j in set(habituales) - set(publicacion))
    if not faltan:
        return ""

    visibles = faltan[:AUSENTES_NOMBRADOS]
    sobran = len(faltan) - len(visibles)
    # Con coleta, los nombres van con comas: `_y` pondría un «y» y saldrían dos seguidas —«Cata y Clara C y
    # uno más»—. Lo delató el mensaje compuesto.
    resto = "" if not sobran else (" y uno más" if sobran == 1 else f" y otros {sobran}")
    listado = ", ".join(visibles) if sobran else _y(visibles)
    return _del_ciclo(AUSENTES_DEL_DIA, jornada).format(jugador=listado, resto=resto)


def bloque_la_jornada(resultados: list[dict], temporada: str, jornada: int, senales=None) -> str:
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
    from refranero import DIBUJO_DEL_DIA, MEJORES_DEL_DIA
    from voz import _del_ciclo, conector, estado_de_animo

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
    piezas: list[tuple[int, str, set[str]]] = []

    for hecho in hechos_elegidos(resultados, temporada, jornada):
        prioridad = 0 if hecho.clave in ("sospechoso", "clavada") else 4
        texto = frase_de_hecho(hecho.clave, jornada, hecho.jugador, hecho.dato, hecho.varios)
        piezas.append((prioridad, texto, {hecho.jugador}))

    piezas.append((
        1,
        _del_ciclo(MEJORES_DEL_DIA, jornada).format(jugador=quienes_texto, intentos=mejor),
        protagonistas,
    ))

    obra = _obra_del_dia(resultados, temporada, jornada)
    if obra:
        fila, categoria = obra
        from figures import emoji

        piezas.append((
            2,
            _del_ciclo(DIBUJO_DEL_DIA, jornada).format(
                jugador=_nombre(fila), emoji=emoji(categoria), intentos=fila["score"]
            ),
            {_nombre(fila)},
        ))

    if hoy is not None and media is not None:
        piezas.append((3, _linea_de_dificultad(hoy, media, jornada), set()))

    for texto in _linea_de_horarios(senales, nombres, jornada):
        piezas.append((5, texto, set()))

    ausentes = _linea_de_ausentes(
        senales, [fila["jugador"] for fila in con_puesto], nombres, jornada
    )
    if ausentes:
        piezas.append((6, ausentes, set()))

    dichas = menciones_del_canal(senales, nombres, jornada)
    for texto in dichas:
        piezas.append((7, texto, set()))

    piezas.sort(key=lambda pieza: pieza[0])
    lineas = [texto for _, texto, _ in piezas]

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


def menciones_del_canal(senales, nombres: dict[str, str], jornada: int) -> list[str]:
    """Las menciones que salen del canal: aplausos y conversación. Los horarios tienen su propia línea."""
    from voz import menciones

    dichas = menciones(
        reacciones=getattr(senales, "reacciones", None) or {},
        respuestas=getattr(senales, "respuestas", None) or {},
        publicacion={},
        nombres=nombres,
        jornada=jornada,
    )
    return [dichas[clave] for clave in ("aplaudido", "comentado") if clave in dichas]


def bloque_rivalidad(resultados: list[dict], temporada: str, jornada: int) -> str:
    """La pelea por el primer puesto, **si la hay**.

    Con ventaja amplia no sale nada: inventar una rivalidad donde alguien va destacado sería contar mal la
    temporada, y el mensaje ya tiene bastantes líneas.

    Se lee de `posicion`, no del orden de la lista. Es el mismo error que la web publicaba en su titular —
    tomar el segundo elemento del array como «el segundo» y restar las medias— y que con un empate en cabeza
    producía «le sigue a 0,00».
    """
    from refranero import RIVALIDAD_EMPATE, RIVALIDAD_MONTON, RIVALIDAD_PELEA
    from voz import _del_ciclo

    filas = [fila for fila in clasificacion(resultados, temporada) if fila["clasificado"]]
    if len(filas) < 2:
        return ""

    lider = filas[0]
    empatados = [fila for fila in filas if fila["posicion"] == lider["posicion"]]
    nota = _cifra(lider["media_temporada"])

    if len(empatados) == 2:
        return _del_ciclo(RIVALIDAD_EMPATE, jornada).format(
            a=empatados[0]["nombre"], b=empatados[1]["nombre"], cifra=nota
        )
    if len(empatados) > 2:
        return _del_ciclo(RIVALIDAD_MONTON, jornada).format(cuantos=len(empatados), cifra=nota)

    siguiente = next((fila for fila in filas if fila["posicion"] != lider["posicion"]), None)
    if not siguiente:
        return ""
    ventaja = siguiente["media_temporada"] - lider["media_temporada"]
    if ventaja > VENTAJA_MINIMA:
        return ""
    return _del_ciclo(RIVALIDAD_PELEA, jornada).format(
        a=lider["nombre"], b=siguiente["nombre"], cifra=_cifra(ventaja)
    )


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


def bloque_album(resultados: list[dict], temporada: str) -> str:
    """La cabeza del ranking de belleza. Vacío si nadie está clasificado."""
    datos = album(resultados, temporada)
    clasificados = [fila for fila in datos["jugadores"] if fila["clasificado"]][:CABEZA_DEL_ALBUM]
    if not clasificados:
        return ""

    lineas, anterior = [], None
    for fila in clasificados:
        marca = f"{fila['posicion']}º" if fila["posicion"] != anterior else "  ·"
        anterior = fila["posicion"]
        lineas.append(
            f"{marca} {fila['nombre']} — {_cifra(fila['media'])} pts "
            f"{tira(fila['recuento'], datos['categorias'])}"
        )
    return "🎨 *Ranking de figuras*\n" + "\n".join(lineas)


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
            meme=meme_del_dia(filas, jornada, lider=lider, ultimo=ultimo),
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


def _pulla_del_marcador(resultados: list[dict], temporada: str, jornada: int) -> str:
    from voz import pullas_de_lideres

    con_puesto = [fila for fila in clasificacion(resultados, temporada) if fila.get("posicion")]
    if not con_puesto:
        return ""
    return pullas_de_lideres(con_puesto[0]["nombre"], None, jornada).get("marcador", "")


def _pulla_del_album(resultados: list[dict], temporada: str, jornada: int) -> str:
    from voz import pullas_de_lideres

    clasificados = [f for f in album(resultados, temporada)["jugadores"] if f.get("posicion")]
    if not clasificados:
        return ""
    return pullas_de_lideres(None, clasificados[0]["nombre"], jornada).get("album", "")


def resumen_del_dia(resultados: list[dict], temporada: str, jornada: int, senales=None) -> str:
    """El resumen completo. **Una sección sin datos no se imprime**, no se imprime vacía."""
    del_dia = _del_dia(resultados, jornada)
    secciones = [
        bloque_la_jornada(resultados, temporada, jornada, senales),
        # **Una** línea de cierre —el meme si la jornada tiene forma, y si no el proverbio— entre la jornada y
        # los rankings. Tres frases seguidas era un tercer bloque de comentarios y el mensaje ya tiene dos.
        *_voz(resultados, temporada, jornada, senales),
        bloque_top(resultados, temporada, jornada),
        # Las pullas van **pegadas a su ranking**, que es lo que comentan. Sueltas al final del comentario
        # nadie sabía a qué se referían.
        _pulla_del_marcador(resultados, temporada, jornada),
        bloque_rivalidad(resultados, temporada, jornada),
        bloque_album(resultados, temporada),
        _pulla_del_album(resultados, temporada, jornada),
    ]
    return "\n\n".join(seccion for seccion in secciones if seccion)
