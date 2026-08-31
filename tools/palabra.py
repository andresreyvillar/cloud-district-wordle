"""La palabra del día y su significado.

Slice: `palabra-del-dia` (openspec/slices/publicacion/palabra-del-dia.md).

**El grupo juega «La palabra del día», no el Wordle del NYT.** Confirmado por dos vías independientes que
coinciden: la numeración de la tabla sitúa la jornada 1 el 2022-01-07, y el propio cliente del juego declara
`firstDay = DateTime.fromISO("2022-01-07T00:00", {zone: "America/New_York"})`. El identificador que guarda la
tabla **es** el índice del juego, sin desplazamiento.

**Por qué el mensaje sale a medianoche de Madrid.** El índice avanza a medianoche de Nueva York, que son las
06:00 de Madrid. A las 00:00 de Madrid la palabra sigue siendo la que el grupo ha jugado todo el día, así que
coincide con la jornada que resume el mensaje; a cualquier otra hora habría desfase de un día. Y el riesgo de
destripar la partida a alguien es medido: **2 de 1748 resultados** del canal se publicaron entre las 00:00 y
las 06:00 (0,1%).

**Nada se persiste.** Se lee, se usan dos campos y se descarta, igual que la lectura del canal.

El fichero de soluciones está ofuscado —gzip, XOR con una clave que viaja en el propio cliente, y msgpack—, y
esto reimplementa esa lógica de cliente. De ahí `HASTA_LA_JUGADA`: el lector **se niega a devolver una palabra
posterior a la última jugada**, así que el repositorio, tal como se publica, no entrega ninguna palabra futura.
Romper esa propiedad pone la suite en rojo.
"""

from __future__ import annotations

import gzip
import json
import re
import urllib.parse
import urllib.request

#: De dónde sale la lista de soluciones. La sirve el propio juego, pública y sin autenticación.
URL_SOLUCIONES = "https://lapalabradeldia.com/solutions/normal.binz"

#: La clave del XOR, que el cliente del juego trae en texto plano.
CLAVE_DEL_FICHERO = b"marissa-peral-morchito"

#: Identifica al pipeline ante Wikimedia, que limita las peticiones anónimas. En producción es **una al día**;
#: medir la cobertura con veinticinco seguidas dio siete falsos negativos, y con pausa salieron todas.
AGENTE = "wordle-stats/1.0 (+https://github.com/andresreyvillar/cloud-district-wordle)"

#: Hasta dónde se recorta la acepción para que quepa en una línea del mensaje.
LARGO_DE_LA_ACEPCION = 150


def descifra(binz: bytes) -> list[dict]:
    """Las entradas de soluciones a partir del fichero descargado. **Función pura.**

    La cadena es gzip → XOR → msgpack, y es la del cliente del juego. Cada entrada trae `id`, `solution` y
    `extras`; se busca **por `id`** y no por posición, que es más robusto que reproducir su aritmética de
    índices. `extras` viene vacío en todas, así que la definición no está ahí y hay que buscarla aparte.
    """
    import msgpack

    crudo = gzip.decompress(binz)
    claro = bytes(
        byte ^ CLAVE_DEL_FICHERO[i % len(CLAVE_DEL_FICHERO)] for i, byte in enumerate(crudo)
    )
    entradas = msgpack.unpackb(claro, raw=False)
    return entradas if isinstance(entradas, list) else []


def palabra_de(entradas: list[dict], jornada: int, hasta_la_jugada: int) -> str | None:
    """La palabra de una jornada, **y nunca la de una jornada sin jugar**.

    `hasta_la_jugada` es la última jornada que existe en la tabla. Pedir una posterior devuelve `None` aunque
    esté en el fichero: es el guardarraíl que hace que este repositorio no sea una lista de respuestas
    futuras. El fichero trae 2.000 entradas, así que sin esto bastaría cambiar un número para leer meses por
    delante.
    """
    if jornada > hasta_la_jugada:
        return None
    for entrada in entradas:
        if entrada.get("id") == jornada:
            palabra = entrada.get("solution")
            return palabra if isinstance(palabra, str) and palabra else None
    return None


def primera_acepcion(extracto: str) -> str:
    """La primera definición de un extracto del Wikcionario. **Función pura.**

    El extracto viene en texto plano con las acepciones numeradas, y la definición es la línea siguiente a la
    marca «1» —que a veces lleva pegada la etiqueta del campo, como «1 Árboles»—. Se salta lo que no es
    definición: cabeceras, sinónimos, antónimos y notas de uso.
    """
    lineas = [linea.strip() for linea in extracto.splitlines()]
    for i, linea in enumerate(lineas):
        if not re.fullmatch(r"1\s*.{0,40}", linea) or linea.startswith("=="):
            continue
        for siguiente in lineas[i + 1 :]:
            if siguiente and not siguiente.startswith(("=", "Sinónimos", "Antónimos", "Uso:")):
                return _recorta(siguiente)
        break
    return ""


def _recorta(texto: str) -> str:
    """La acepción, cortada por la primera frase si es larga. Nunca a mitad de palabra."""
    if len(texto) <= LARGO_DE_LA_ACEPCION:
        return texto
    punto = texto.find(". ")
    if 0 < punto <= LARGO_DE_LA_ACEPCION:
        return texto[: punto + 1]
    corte = texto.rfind(" ", 0, LARGO_DE_LA_ACEPCION)
    return texto[: corte if corte > 0 else LARGO_DE_LA_ACEPCION].rstrip(" ,;:") + "…"


def _pide(url: str) -> bytes | None:
    peticion = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    try:
        with urllib.request.urlopen(peticion, timeout=20) as respuesta:
            return respuesta.read()
    except Exception as error:  # noqa: BLE001 — cualquier fallo de red es «no hay palabra», no una excepción
        print(f"palabra del día: no se pudo leer {url}: {error}")
        return None


def descarga_soluciones(url: str = URL_SOLUCIONES) -> bytes | None:
    """El fichero de soluciones, o `None` si no se pudo. El borde del sistema."""
    return _pide(url)


def busca_extracto(palabra: str) -> str:
    """El extracto del Wikcionario de una palabra, probando también con mayúscula inicial.

    `troya` no tiene entrada y `Troya` sí: el juego usa minúsculas y el Wikcionario respeta el nombre propio.
    Sin este respaldo se perdía una de cada veinticinco definiciones.
    """
    for candidata in (palabra, palabra.capitalize()):
        crudo = _pide(
            "https://es.wiktionary.org/w/api.php?action=query&prop=extracts&explaintext=1"
            f"&format=json&titles={urllib.parse.quote(candidata)}"
        )
        if not crudo:
            continue
        try:
            paginas = json.loads(crudo)["query"]["pages"]
        except (KeyError, ValueError):
            continue
        extracto = next(iter(paginas.values()), {}).get("extract", "")
        if extracto:
            return extracto
    return ""


def palabra_del_dia(
    jornada: int,
    hasta_la_jugada: int,
    descargar=descarga_soluciones,
    extraer=busca_extracto,
) -> tuple[str, str] | None:
    """`(palabra, acepcion)` de una jornada, o `None` si algo falla.

    La descarga y el diccionario entran por parámetro para poder doblarlos: los tests construyen su propio
    fichero cifrado y no tocan la red.

    **Fallar es no publicar la línea, no romper el mensaje.** Si el juego o el Wikcionario no responden, el
    resumen sale igual sin esta línea, como cualquier otra sección sin datos.
    """
    binz = descargar()
    if not binz:
        return None
    try:
        entradas = descifra(binz)
    except Exception as error:  # noqa: BLE001 — un fichero con otro formato no puede tumbar la publicación
        print(f"palabra del día: no se pudo descifrar el fichero: {error}")
        return None

    palabra = palabra_de(entradas, jornada, hasta_la_jugada)
    if not palabra:
        return None
    return palabra, primera_acepcion(extraer(palabra))
