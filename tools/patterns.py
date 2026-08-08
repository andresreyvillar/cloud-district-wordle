"""Extracción del patrón de la cuadrícula de un resultado de Wordle.

Funciones puras: texto → texto. Sin Slack, sin Supabase y sin reloj, para que los escenarios
del slice `captura-del-patron` se puedan verificar sin red ni base de datos (§10 del protocolo).

Formato de almacenamiento: filas separadas por `/`, cada fila de cinco caracteres.
    `G` acierto en posición · `Y` letra presente en otra posición · `.` letra ausente
Un resultado en tres intentos queda como `...YY/.G.YY/GGGGG`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

#: nombres de celda tal como llegan en el texto del canal. La celda de letra ausente tiene DOS
#: nombres según el tema claro u oscuro de quien publica, y los dos se normalizan igual.
CELDAS = {
    ":large_green_square:": "G",
    ":large_yellow_square:": "Y",
    ":black_large_square:": ".",
    ":white_large_square:": ".",
}

ANCHO_FILA = 5
PATTERN_ROW_SEPARATOR = "/"

CELDA_RE = re.compile(r":[a-z_]+square:")
#: `USER_START|<identificador>|<nombre>|<hora>|<texto>`. El identificador va primero porque es lo que
#: identifica; el nombre solo se muestra. El último grupo llega hasta el final de la línea, así que un
#: mensaje que contenga `|` no descuadra los campos.
HEADER_RE = re.compile(r"^USER_START\|(.*?)\|(.*?)\|(.*?)\|(.*)$")
RESULTADO_RE = re.compile(r"La palabra del día #(\d+) (X|\d)/6", re.IGNORECASE)


def fila_normalizada(linea: str) -> str | None:
    """La fila normalizada de una línea, o None si la línea no es una fila de cuadrícula.

    Una fila es una línea con **exactamente** cinco celdas reconocidas y nada más: cuatro celdas,
    seis, o una celda dentro de una frase no son filas.
    """
    celdas = CELDA_RE.findall(linea)
    if len(celdas) != ANCHO_FILA:
        return None
    if any(celda not in CELDAS for celda in celdas):
        return None
    if CELDA_RE.sub("", linea).strip():
        return None
    return "".join(CELDAS[celda] for celda in celdas)


def filas_de_cuadricula(texto: str) -> list[str]:
    """Todas las filas de cuadrícula de un texto, en el orden en que aparecen."""
    filas = [fila_normalizada(linea) for linea in texto.splitlines()]
    return [fila for fila in filas if fila is not None]


def normalizar_patron(filas: list[str]) -> str | None:
    """El patrón almacenable de una lista de filas, o None si no hay filas."""
    return PATTERN_ROW_SEPARATOR.join(filas) if filas else None


def puntuacion(marcador: str) -> int:
    """El número de intentos del marcador del mensaje; un fallo (`X`) cuenta como 7."""
    return 7 if marcador.upper() == "X" else int(marcador)


@dataclass
class BloqueResultado:
    """Un resultado con las filas de cuadrícula que lo acompañan.

    `usuario` es **el identificador de Slack** de quien lo publicó y `nombre` lo que muestra. La identidad
    no puede depender del nombre: cambia, y un renombre partía al jugador en dos.
    """

    usuario: str | None
    numero: int
    score: int
    texto_resultado: str
    nombre: str | None = None
    filas: list[str] = field(default_factory=list)

    @property
    def patron(self) -> str | None:
        return normalizar_patron(self.filas)


def bloques_de_resultado(lineas: list[str]):
    """Agrupa el lote de líneas en bloques: cada resultado con sus filas.

    Las filas llegan como líneas independientes después de la línea que declara el resultado, así
    que se asocian al último resultado reconocido. Un mensaje nuevo —haya o no resultado en él—
    cierra el bloque anterior: las filas de un mensaje distinto no pertenecen al resultado previo.
    """
    usuario_actual: str | None = None
    nombre_actual: str | None = None
    pendiente: BloqueResultado | None = None

    for linea in lineas:
        encabezado = HEADER_RE.match(linea)
        contenido = encabezado.group(4) if encabezado else linea
        if encabezado:
            usuario_actual = encabezado.group(1).strip()
            nombre_actual = encabezado.group(2).strip() or None

        resultado = RESULTADO_RE.search(contenido)
        if resultado:
            if pendiente is not None:
                yield pendiente
            pendiente = BloqueResultado(
                usuario=usuario_actual,
                numero=int(resultado.group(1)),
                score=puntuacion(resultado.group(2)),
                texto_resultado=contenido,
                nombre=nombre_actual,
            )
            continue

        if encabezado and pendiente is not None:
            # mensaje nuevo sin resultado: cierra el bloque anterior
            yield pendiente
            pendiente = None

        if pendiente is not None:
            fila = fila_normalizada(contenido)
            if fila is not None:
                pendiente.filas.append(fila)

    if pendiente is not None:
        yield pendiente


def patrones_por_resultado(lineas: list[str]) -> list[tuple[int, str | None]]:
    """El patrón de cada resultado del lote, en orden: `(número de puzzle, patrón)`."""
    return [(bloque.numero, bloque.patron) for bloque in bloques_de_resultado(lineas)]
