"""El podio del mes que cierra: a quién se felicita y a quién se le desea suerte.

Slice: `podio-de-cierre-de-mes` (openspec/slices/publicacion/podio-de-cierre-de-mes.md).

**Qué mes se celebra sale de los datos, no del reloj** (§10). La temporada en curso es la del último resultado
de la tabla, y la que se celebra es la inmediatamente anterior. Si el mes nuevo todavía no tiene resultados
—a primera hora del día 1 puede no haberlos— no se celebra nada y se vuelve a intentar al día siguiente: el
cron corre del 1 al 7 justo para eso.

**No se recalcula nada.** El podio sale de `standings.clasificacion` y las medallas de `badges`, los mismos
que publica la web ([ADR 0008](../openspec/decisions/0008-donde-vive-el-calculo.md)).
"""

from __future__ import annotations

from badges import ORDEN_NIVEL, POR_CLAVE, medallas_de_temporada
from seasons import MESES, TEMPORADA_CERO, ordinal, temporada_de
from standings import clasificacion

#: Desde qué temporada se corona a los campeones de las tres competiciones —marcador, SuperWordleBros y
#: figuras—. La misma que `v2/js/data/archivo.js::DESDE_TRES_COMPETICIONES`, y un test comprueba que coinciden.
DESDE_TRES_COMPETICIONES = "2026-10"

#: Cuántos suben al podio.
DEL_PODIO = 3


def temporada_que_cierra(resultados: list[dict]) -> str | None:
    """La temporada cerrada que toca celebrar, o `None` si no hay ninguna.

    Es la anterior a la del último resultado. **La temporada 0 no se celebra**: no cerró un mes, es el bloque
    histórico anterior a que existieran las temporadas.

    Devuelve `None` cuando el mes nuevo aún no tiene resultados, porque entonces la «anterior» sería la de
    hace dos meses y se felicitaría a quien ganó algo que ya se celebró.
    """
    if not resultados:
        return None
    meses = sorted({temporada_de(fila["date"]) for fila in resultados} - {TEMPORADA_CERO})
    if len(meses) < 2:
        return None
    en_curso, cerrada = meses[-1], meses[-2]
    # El mes en curso tiene que ser **consecutivo** al cerrado: si hay un salto, es que el mes nuevo todavía
    # no ha empezado a jugarse y lo que se está mirando es un cierre viejo.
    if _siguiente(cerrada) != en_curso:
        return None
    return cerrada


def _siguiente(temporada: str) -> str:
    año, mes = (int(parte) for parte in temporada.split("-"))
    return f"{año + 1}-01" if mes == 12 else f"{año}-{mes + 1:02d}"


def podio_de(resultados: list[dict], temporada: str) -> list[dict]:
    """Los tres primeros de una temporada, **con los empates enteros**.

    Se corta por puesto y no por número de filas: dos personas empatadas en el tercero suben las dos, igual
    que en el marcador diario. Cortar por filas partiría un empate por la mitad.
    """
    clasificados = [fila for fila in clasificacion(resultados, temporada) if fila["clasificado"]]
    return [fila for fila in clasificados if fila["posicion"] and fila["posicion"] <= DEL_PODIO]


def campeones(podio: list[dict]) -> list[str]:
    """Quién ganó el mes. Más de uno si hubo empate en el primer puesto."""
    if not podio:
        return []
    primero = podio[0]["posicion"]
    return [fila["nombre"] for fila in podio if fila["posicion"] == primero]


def medallas_del_campeon(resultados: list[dict], temporada: str, nombre: str) -> list[str]:
    """Las medallas que el campeón ganó **en esa temporada**, de la más difícil a la más común."""
    claves = medallas_de_temporada(resultados, temporada).get(nombre, [])
    return sorted(claves, key=lambda clave: (ORDEN_NIVEL[POR_CLAVE[clave].nivel], clave))


def _juntos(nombres: list[str]) -> str:
    return nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]


def _otros_campeones(resultados: list[dict], temporada: str, niveles, marcas) -> list[str]:
    """Las líneas de los campeones del SuperWordleBros y de figuras, desde octubre de 2026. Un empate se
    comparte en plural, como en el marcador; una competición sin nadie no corona a nadie."""
    from album import album
    from juego import clasificacion_del_juego
    from resumen import _cifra

    if temporada == TEMPORADA_CERO or temporada < DESDE_TRES_COMPETICIONES:
        return []
    lineas = []
    juego = clasificacion_del_juego(resultados, list(niveles), list(marcas), temporada)["clasificacion"]
    cabeza = [f for f in juego if f["posicion"] == 1]
    if cabeza:
        puntos = cabeza[0]["puntos"]
        nombres = _juntos([f["nombre"] for f in cabeza])
        lineas.append(
            f"🎮 Campeón del SuperWordleBros: {nombres}, con {puntos} puntos." if len(cabeza) == 1
            else f"🎮 {nombres} comparten el primer puesto del SuperWordleBros, con {puntos} puntos."
        )
    figuras = [f for f in album(resultados, temporada)["jugadores"] if f["clasificado"] and f["posicion"] == 1]
    if figuras:
        media = _cifra(figuras[0]["media"])
        nombres = _juntos([f["nombre"] for f in figuras])
        lineas.append(
            f"🎨 Campeón de figuras: {nombres}, con {media} puntos por partida." if len(figuras) == 1
            else f"🎨 {nombres} comparten el primer puesto de figuras, con {media} puntos por partida."
        )
    return lineas


def texto(
    resultados: list[dict], temporada: str, jornada: int, niveles=(), marcas=(), ultima_jornada: str = ""
) -> str:
    """El mensaje del cierre de mes. Cadena vacía si no hay podio que enseñar.

    `jornada` solo elige la variante de las frases (§10: sin azar), no entra en el cálculo. `niveles` y
    `marcas` son los del SuperWordleBros, para coronar a su campeón desde octubre. `ultima_jornada` va antes
    de la despedida del mes: la noche del último día, la victoria cuenta también ese día, y despedir el mes
    antes de contarlo se leía al revés.
    """
    from refranero import NUEVA_TEMPORADA, PODIO_CAMPEON, PODIO_CAMPEONES
    from resumen import _cifra
    from podios import podio_de_texto
    from voz import _del_ciclo, con_nombre

    tabla = podio_de(resultados, temporada)
    if not tabla:
        return ""

    # **Abre presentando el juego y el mes.** Sale una vez al mes y no tiene el contexto del mensaje diario:
    # quien lo lee puede llevar semanas sin mirar la tabla. Decisión del dueño.
    lineas = [
        f"Ya tenemos los resultados de *Cloud District Wordle* del mes de {mes_y_año(temporada)} 🎉",
        "",
        # **El mismo podio ASCII que el resumen diario** (decisión del dueño): el 1º en el centro y más alto, y
        # con un empate en cabeza los campeones juntos en ese escalón —la lista de medallas de antes ponía al
        # segundo campeón debajo, con un «·», como si fuera menos—. El mes va **solo en la presentación**: con
        # `etiqueta()` completa aquí, «agosto de 2026» salía dos veces en dos líneas seguidas. La coma decimal
        # la pone `_cifra`, solo en el número: «Andrés R.» no puede acabar en «Andrés R,».
        podio_de_texto(
            f"🏆 *Así queda el podio · Temporada {ordinal(temporada)}*",
            [
                {"posicion": fila["posicion"], "nombre": fila["nombre"], "cifra": _cifra(fila["media_temporada"])}
                for fila in tabla
            ],
        ),
    ]

    quienes = campeones(tabla)
    if quienes:
        nombres = quienes[0] if len(quienes) == 1 else ", ".join(quienes[:-1]) + " y " + quienes[-1]
        # Con el primer puesto compartido, frases escritas para varios: «Cata y Joel se lleva el mes» era la
        # frase de un campeón solo con dos nombres dentro.
        frases = PODIO_CAMPEON if len(quienes) == 1 else PODIO_CAMPEONES
        lineas += ["", con_nombre(_del_ciclo(frases, jornada), nombres)]
        insignias = medallas_del_campeon(resultados, temporada, quienes[0]) if len(quienes) == 1 else []
        if insignias:
            lucidas = " ".join(POR_CLAVE[clave].emoji for clave in insignias)
            lineas.append(f"Se lleva además {lucidas} de la temporada.")

    otros = _otros_campeones(resultados, temporada, niveles or (), marcas or ())
    if otros:
        lineas += ["", *otros]

    if ultima_jornada:
        lineas += ["", ultima_jornada]

    lineas += ["", _del_ciclo(NUEVA_TEMPORADA, jornada)]
    return "\n".join(lineas)


def mes_y_año(temporada: str) -> str:
    """«agosto de 2026», para quien no sabe qué es «Temporada 1»."""
    año, mes = (int(parte) for parte in temporada.split("-"))
    return f"{MESES[mes - 1]} de {año}"
