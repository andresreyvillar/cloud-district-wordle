"""Escenarios de `captura-del-patron` (Fase 2 — TDD rojo).

Los siete escenarios del slice sobre fixtures de texto: ni Slack ni Supabase. Eso obliga a que la
implementación viva en funciones puras (`tools/patterns.py`), que es justo lo que se quiere.

Los fixtures reproducen el formato real del canal, verificado contra los mensajes publicados:
la primera línea declara el resultado y las filas de cuadrícula llegan después, con la celda de
letra ausente en dos variantes (`:black_large_square:` y `:white_large_square:`) según el tema
de quien publica.
"""

from __future__ import annotations

VERDE = ":large_green_square:"
AMARILLO = ":large_yellow_square:"
NEGRO = ":black_large_square:"
BLANCO = ":white_large_square:"


def fila(*celdas: str) -> str:
    return "".join(celdas)


MENSAJE_TRES_INTENTOS = "\n".join(
    [
        "La palabra del día #1671 3/6",
        "",
        fila(NEGRO, NEGRO, NEGRO, AMARILLO, AMARILLO),
        fila(NEGRO, VERDE, NEGRO, AMARILLO, AMARILLO),
        fila(VERDE, VERDE, VERDE, VERDE, VERDE),
    ]
)

MENSAJE_TEMA_CLARO = "\n".join(
    [
        "La palabra del día #1671 3/6",
        "",
        fila(BLANCO, BLANCO, BLANCO, AMARILLO, AMARILLO),
        fila(BLANCO, VERDE, BLANCO, AMARILLO, AMARILLO),
        fila(VERDE, VERDE, VERDE, VERDE, VERDE),
    ]
)


# @scenarios patron-se-persiste
def test_el_patron_conserva_una_fila_por_intento():
    from tools.patterns import filas_de_cuadricula, normalizar_patron

    filas = filas_de_cuadricula(MENSAJE_TRES_INTENTOS)
    assert filas == ["...YY", ".G.YY", "GGGGG"]
    assert normalizar_patron(filas) == "...YY/.G.YY/GGGGG"


# @scenarios ausentes-se-normalizan
def test_los_dos_temas_producen_el_mismo_patron():
    from tools.patterns import filas_de_cuadricula, normalizar_patron

    oscuro = normalizar_patron(filas_de_cuadricula(MENSAJE_TRES_INTENTOS))
    claro = normalizar_patron(filas_de_cuadricula(MENSAJE_TEMA_CLARO))
    assert oscuro == claro


# @scenarios sin-cuadricula-el-resultado-se-registra
def test_mensaje_sin_cuadricula_no_produce_patron_pero_si_resultado():
    from tools.patterns import normalizar_patron, patrones_por_resultado

    lote = ["USER_START|Jugador|09:00|La palabra del día #1671 4/6"]
    resultados = patrones_por_resultado(lote)
    assert len(resultados) == 1
    numero, patron = resultados[0]
    assert numero == 1671
    assert patron is None
    assert normalizar_patron([]) is None


# @scenarios filas-de-otro-mensaje-no-contaminan
def test_dos_resultados_seguidos_no_mezclan_sus_cuadriculas():
    from tools.patterns import patrones_por_resultado

    lote = [
        "USER_START|Uno|09:00|La palabra del día #1671 3/6",
        "",
        fila(NEGRO, NEGRO, NEGRO, AMARILLO, AMARILLO),
        fila(NEGRO, VERDE, NEGRO, AMARILLO, AMARILLO),
        fila(VERDE, VERDE, VERDE, VERDE, VERDE),
        "USER_START|Dos|09:05|La palabra del día #1671 2/6",
        "",
        fila(AMARILLO, AMARILLO, NEGRO, NEGRO, NEGRO),
        fila(VERDE, VERDE, VERDE, VERDE, VERDE),
    ]
    resultados = patrones_por_resultado(lote)
    assert [p for _, p in resultados] == ["...YY/.G.YY/GGGGG", "YY.../GGGGG"]


# @scenarios filas-de-otro-mensaje-no-contaminan
def test_un_mensaje_de_conversacion_no_contamina_el_resultado_anterior():
    """Un mensaje nuevo cierra el bloque: aunque lleve celdas, no se pegan al resultado previo."""
    from tools.patterns import patrones_por_resultado

    lote = [
        "USER_START|Uno|09:00|La palabra del día #1671 2/6",
        "",
        fila(AMARILLO, AMARILLO, NEGRO, NEGRO, NEGRO),
        fila(VERDE, VERDE, VERDE, VERDE, VERDE),
        f"USER_START|Dos|09:03|mirad qué cuadrícula tan bonita",
        fila(NEGRO, NEGRO, NEGRO, NEGRO, NEGRO),
    ]
    resultados = patrones_por_resultado(lote)
    assert resultados == [(1671, "YY.../GGGGG")]


# @scenarios filas-de-otro-mensaje-no-contaminan
def test_las_celdas_sin_resultado_previo_no_producen_patron():
    from tools.patterns import patrones_por_resultado

    lote = [
        "USER_START|Alguien|09:00|vaya día llevo",
        fila(NEGRO, NEGRO, NEGRO, NEGRO, NEGRO),
    ]
    assert patrones_por_resultado(lote) == []


# @scenarios linea-que-no-es-fila-se-ignora
def test_una_linea_que_no_son_cinco_celdas_no_es_fila():
    from tools.patterns import filas_de_cuadricula

    mensaje = "\n".join(
        [
            "La palabra del día #1671 2/6",
            "",
            fila(AMARILLO, AMARILLO, NEGRO, NEGRO),  # cuatro celdas: no es fila
            f"vaya día {VERDE} qué duro",  # celda dentro de una frase
            fila(VERDE, VERDE, VERDE, VERDE, VERDE),
        ]
    )
    assert filas_de_cuadricula(mensaje) == ["GGGGG"]


# @scenarios reejecucion-mantiene-un-solo-patron
def test_reprocesar_el_mismo_mensaje_produce_el_mismo_patron():
    from tools.patterns import filas_de_cuadricula, normalizar_patron

    primera = normalizar_patron(filas_de_cuadricula(MENSAJE_TRES_INTENTOS))
    segunda = normalizar_patron(filas_de_cuadricula(MENSAJE_TRES_INTENTOS))
    assert primera == segunda
    assert primera.count("/") == 2  # no se concatena consigo mismo


# @scenarios patron-de-fallo-se-guarda
def test_un_fallo_conserva_las_seis_filas_sin_terminar_en_aciertos():
    from tools.patterns import filas_de_cuadricula, normalizar_patron

    mensaje = "\n".join(
        ["La palabra del día #1671 X/6", ""]
        + [fila(NEGRO, AMARILLO, NEGRO, NEGRO, AMARILLO)] * 6
    )
    filas = filas_de_cuadricula(mensaje)
    assert len(filas) == 6
    assert normalizar_patron(filas).split("/")[-1] != "GGGGG"
