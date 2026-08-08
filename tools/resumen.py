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
from figures import FIGURAS, figura
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
    plural = "" if len(quienes) == 1 else "n"
    return f"🏆 *Jugador del día:* {', '.join(quienes)} — resolvió{plural} en {mejor}."


def rareza(resultados: list[dict], temporada: str) -> dict[str, int]:
    """Cuántas veces ha salido cada categoría en la temporada. Menos veces, más rara.

    Se deriva **del reparto de la propia temporada** y no de una tabla escrita a mano: recalibrar el
    clasificador cambia qué figura es rara, y una lista fija se quedaría atrás en silencio.
    """
    return album(resultados, temporada)["reparto"]


def bloque_obra_del_dia(resultados: list[dict], temporada: str, jornada: int) -> str:
    """La figura más rara dibujada hoy, con su autor.

    Empates: primero la categoría menos frecuente de la temporada; luego **más intentos**, porque la figura
    sale del lienzo y el lienzo lo deja quien tarda (2,9 intentos de media en las partidas sin figura frente
    a 4,7 en las que la tienen); y por último el nombre, para que el resultado no dependa del orden de las
    filas.
    """
    candidatas = [
        (fila, figura(fila["pattern"]))
        for fila in _del_dia(resultados, jornada)
        if fila.get("pattern")
    ]
    reconocibles = [(fila, cat) for fila, cat in candidatas if cat in FIGURAS]
    if not reconocibles:
        return "🖼️ *Obra del día:* desierta — hoy no ha salido ninguna figura reconocible."

    frecuencia = rareza(resultados, temporada)
    fila, categoria = min(
        reconocibles,
        key=lambda par: (frecuencia.get(par[1], 0), -par[0]["score"], _nombre(par[0]).lower()),
    )
    from figures import emoji

    return f"🖼️ *Obra del día:* {emoji(categoria)} de {_nombre(fila)} ({fila['score']} intentos)."


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
            f"{marca} {fila['nombre']} — {round(fila['tasa'] * 100)} % "
            f"{tira(fila['recuento'], datos['categorias'])}"
        )
    return "🎨 *Ranking de figuras*\n" + "\n".join(lineas)


def resumen_del_dia(resultados: list[dict], temporada: str, jornada: int) -> str:
    """El resumen completo. **Una sección sin datos no se imprime**, no se imprime vacía."""
    del_dia = _del_dia(resultados, jornada)
    secciones = [
        bloque_jugador_del_dia(del_dia),
        bloque_obra_del_dia(resultados, temporada, jornada) if del_dia else "",
        bloque_top(resultados, temporada, jornada),
        bloque_album(resultados, temporada),
        seccion_de_comentarios(resultados, temporada, jornada),
    ]
    return "\n\n".join(seccion for seccion in secciones if seccion)
