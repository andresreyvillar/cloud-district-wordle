"""El podio en texto del resumen diario: bloques macizos, el 1º en el centro.

Slice: `resumen-diario-compuesto` (escenarios `podio-del-*`, `el-empate-comparte-escalon`,
`el-podio-cabe-en-el-movil`).

Va dentro de un bloque de código de Slack, que es de ancho fijo: es lo único que deja dibujar escalones
alineados. Por eso **no lleva emojis**: un emoji ocupa dos columnas y descuadra el escalón en el que cae.

    ```
                1º
               Ana
       2º      3,40
       Bea   ████████
       3,45  ████████     3º
    ████████ ████████    Cris
    ████████ ████████    3,60
    ████████ ████████ ████████
    ```
"""

from __future__ import annotations

#: Ancho de cada columna del podio y del escalón dentro de ella. Tres columnas y dos espacios: 32.
COLUMNA = 10
ESCALON = 8

#: Lo que cabe en el móvil sin desplazarse: la línea más larga del podio.
ANCHO_MAXIMO = 3 * COLUMNA + 2

#: Filas de cada escalón, por puesto. El 1º, el más alto.
ALTURA = {1: 4, 2: 2, 3: 1}

#: Nombres que se escriben en un escalón antes de resumir el resto con «y N más».
NOMBRES_POR_ESCALON = 3

#: De izquierda a derecha: el 2º, el 1º y el 3º.
ORDEN_DE_COLUMNAS = (2, 1, 3)

#: Lo más alto que puede salir un podio dentro de su bloque de código: el puesto, tres nombres, «y N más», la
#: cifra y el escalón más alto. **No depende de cuánta gente juegue**: es lo que hace que el mensaje no crezca
#: con el grupo.
LINEAS_MAXIMAS = 1 + NOMBRES_POR_ESCALON + 1 + 1 + max(ALTURA.values())


def acortar(nombre: str, ancho: int = COLUMNA) -> str:
    """Un nombre que quepa en su columna.

    Se acorta por palabras: «Flavia Venturi» → «Flavia V.», que se sigue reconociendo en el canal. Solo si ni
    así cabe se corta con puntos suspensivos.
    """
    # Sin acentos graves: tres seguidos en un nombre cerrarían el bloque de código de Slack en mitad del podio.
    nombre = " ".join(str(nombre).replace("`", "'").split())
    if len(nombre) <= ancho:
        return nombre
    palabras = nombre.split(" ")
    siguiente = next((c for palabra in palabras[1:] for c in palabra if c.isalpha()), "")
    if siguiente and len(palabras[0]) + 3 <= ancho:
        return f"{palabras[0]} {siguiente.upper()}."
    return nombre[: ancho - 1] + "…"


def _centrado(texto: str) -> str:
    return texto.center(COLUMNA)


def _columna(puesto: int, filas: list[dict]) -> list[str]:
    """Las líneas de una columna, de arriba abajo: puesto, nombres, cifra y el escalón."""
    etiquetas: list[str] = []
    if filas:
        etiquetas.append(f"{puesto}º")
        nombres = [acortar(f["nombre"]) for f in filas[:NOMBRES_POR_ESCALON]]
        etiquetas.extend(nombres)
        if len(filas) > NOMBRES_POR_ESCALON:
            etiquetas.append(f"y {len(filas) - NOMBRES_POR_ESCALON} más")
        # La cifra del escalón: si comparten puesto, comparten cifra.
        etiquetas.append(acortar(str(filas[0]["cifra"])))
    escalon = ["█" * ESCALON] * ALTURA[puesto]
    return [_centrado(linea) for linea in etiquetas] + [_centrado(linea) for linea in escalon]


def podio_de_texto(titulo: str, puestos: list[dict]) -> str:
    """El podio con su título: `titulo` y debajo el bloque de código.

    `puestos` son filas `{posicion, nombre, cifra}` de los puestos 1 a 3, ya cortadas por puesto: un empate en
    el 3º trae a todos los empatados, y aquí se nombran tres y se resume el resto. Un puesto sin nadie —dos
    empatados en el 1º dejan vacío el 2º— se dibuja como escalón sin nombre. Sin puestos, cadena vacía.
    """
    por_puesto = {p: [f for f in puestos if f["posicion"] == p] for p in ALTURA}
    if not any(por_puesto.values()):
        return ""

    columnas = [_columna(p, por_puesto[p]) for p in ORDEN_DE_COLUMNAS]
    alto = max(len(c) for c in columnas)
    # Alineadas por abajo: los escalones apoyan en el suelo, y lo que sobra arriba es aire.
    columnas = [[" " * COLUMNA] * (alto - len(c)) + c for c in columnas]
    lineas = [" ".join(fila).rstrip() for fila in zip(*columnas)]
    # Una línea en blanco entre el título y el bloque: da aire por encima del podio (decisión del dueño).
    return f"{titulo}\n\n```\n" + "\n".join(lineas) + "\n```"
