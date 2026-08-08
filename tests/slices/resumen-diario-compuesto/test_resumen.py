"""Escenarios de `resumen-diario-compuesto` (Fase 2 — TDD rojo).

El resumen es una **función pura**: entran los resultados, la temporada y la jornada, y sale texto. Ni
reloj, ni Slack, ni navegador — por eso el mensaje que el grupo verá se puede fijar en un test.

Las cuadrículas son las mismas que verifica el slice del clasificador, y aquí se vuelven a comprobar antes
de usarse.
"""

from __future__ import annotations

import pytest

LORO = ".G.../.G..G/.GY../GGGGG"
GEOMETRICO = "..G../..G../GGGGG"
FLOR = "Y...Y/..Y../GGGGG"
ABSTRACTO = "GG.GG/GGYGG/GG.GG/GGGGG"

HISTORICO = "2026-03-02"
HOY = 1600


def resultado(nombre, jornada, score, patron=None, fecha=HISTORICO):
    return {
        "slack_user_id": f"U_{nombre}",
        "player_name": nombre,
        "wordle_id": jornada,
        "score": score,
        "date": fecha,
        "pattern": patron,
    }


def historia(nombre, cuantas, score=4, patron=FLOR):
    """Partidas anteriores, para que la temporada tenga marcador y álbum."""
    return [resultado(nombre, 1500 + i, score, patron) for i in range(cuantas)]


def test_los_fixtures_dibujan_lo_que_dicen_dibujar():
    from figures import figura

    assert (figura(LORO), figura(GEOMETRICO), figura(FLOR), figura(ABSTRACTO)) == (
        "loro",
        "geometrico",
        "flores",
        "abstracto",
    )


# @scenarios jugador-del-dia
def test_el_jugador_del_dia_es_la_mejor_puntuacion():
    from resumen import resumen_del_dia

    filas = historia("Ana", 6) + historia("Bea", 6) + [
        resultado("Ana", HOY, 2, FLOR),
        resultado("Bea", HOY, 5, ABSTRACTO),
    ]

    texto = resumen_del_dia(filas, "0", HOY)

    # Sobre SU línea, no sobre el mensaje entero: Ana aparece también en el top y en el álbum, así que
    # `"Ana" in texto` pasaba aunque el premio se lo llevara Bea. Lo cazó un mutante.
    linea = next(l for l in texto.splitlines() if "Jugador del día" in l)
    assert "Ana" in linea and "Bea" not in linea
    assert "en 2" in linea, "y con la puntuación que lo gana"


# @scenarios jugador-del-dia
def test_el_empate_en_la_mejor_puntuacion_nombra_a_todos():
    """Con diez jugadores y notas de 1 a 7, el empate es lo normal. Elegir uno sería arbitrario."""
    from resumen import bloque_jugador_del_dia

    hoy = [
        resultado("Ana", HOY, 2, FLOR),
        resultado("Bea", HOY, 2, LORO),
        resultado("Cris", HOY, 5, ABSTRACTO),
    ]

    linea = bloque_jugador_del_dia(hoy)

    assert "Ana" in linea and "Bea" in linea
    assert "Cris" not in linea


# @scenarios obra-del-dia
def test_la_obra_del_dia_es_la_figura_mas_rara_de_la_temporada():
    """La rareza sale del reparto de la propia temporada, no de una tabla escrita a mano."""
    from resumen import bloque_obra_del_dia

    # En la temporada hay muchas flores y pocos geométricos: el geométrico es lo raro.
    temporada = historia("Ana", 12, patron=FLOR) + historia("Bea", 12, patron=FLOR)
    hoy = [resultado("Ana", HOY, 4, FLOR), resultado("Bea", HOY, 5, GEOMETRICO)]

    linea = bloque_obra_del_dia(temporada + hoy, "0", HOY)

    assert "Bea" in linea, "gana la categoría menos frecuente, no la mejor puntuación"
    assert "📐" in linea


# @scenarios obra-del-dia
def test_sin_figuras_el_premio_queda_desierto():
    from resumen import bloque_obra_del_dia

    filas = historia("Ana", 6) + [resultado("Ana", HOY, 6, ABSTRACTO)]

    linea = bloque_obra_del_dia(filas, "0", HOY)

    assert "🌀" not in linea, "un abstracto no es una obra"
    assert "desiert" in linea.lower()


# @scenarios top-cinco-con-su-dibujo
def test_el_top_cinco_lleva_el_emoji_de_lo_que_cada_uno_dibujo_hoy():
    from resumen import bloque_top

    temporada = historia("Ana", 10, score=3) + historia("Bea", 10, score=5)
    hoy = [resultado("Ana", HOY, 3, LORO)]  # Bea no jugó hoy

    bloque = bloque_top(temporada + hoy, "0", HOY)

    lineas = {linea.split()[1].rstrip(".") if linea.split() else "": linea for linea in bloque.splitlines()}
    ana = next(l for l in bloque.splitlines() if "Ana" in l)
    bea = next(l for l in bloque.splitlines() if "Bea" in l)
    assert "🦜" in ana
    assert "🦜" not in bea and "🌷" not in bea, "quien no jugó hoy no lleva dibujo del día"


# @scenarios top-cinco-con-su-dibujo
def test_el_top_no_pasa_de_cinco():
    from resumen import bloque_top

    muchos = []
    for indice in range(9):
        muchos += historia(f"J{indice}", 6, score=1 + indice % 6)

    bloque = bloque_top(muchos, "0", 1505)

    # Se corta por PUESTO, no por número de filas: con empates puede haber más de cinco líneas, y lo que
    # no puede pasar es que aparezca un sexto puesto.
    puestos = [int(l.split("º")[0]) for l in bloque.splitlines()[1:] if "º" in l.split(" ")[0]]
    assert puestos and max(puestos) <= 5


# @scenarios cabeza-del-album
def test_la_cabeza_del_album_sale_con_su_tasa_y_su_tira():
    from resumen import bloque_album

    limpia = historia("Ana", 8, patron=LORO)
    sucia = historia("Bea", 8, patron=ABSTRACTO)

    bloque = bloque_album(limpia + sucia, "0")

    assert "Ana" in bloque
    assert "100" in bloque, "su tasa"
    assert "🦜8" in bloque, "su tira agrupada"


# @scenarios sin-jornada-no-hay-resumen
def test_sin_resultados_no_se_inventa_ninguna_seccion():
    from resumen import resumen_del_dia

    texto = resumen_del_dia([], "0", HOY)

    assert "Jugador del día" not in texto
    assert "Obra del día" not in texto
    assert texto.strip() == "" or "ranking" in texto.lower()


# @scenarios sin-jornada-no-hay-resumen
def test_una_temporada_sin_album_no_imprime_la_seccion_del_album():
    """Es el estado real de agosto de 2026: 61 de 80 partidas sin cuadrícula guardada."""
    from resumen import resumen_del_dia

    filas = historia("Ana", 8, patron=None) + [resultado("Ana", HOY, 3, None)]

    texto = resumen_del_dia(filas, "0", HOY)

    assert "Álbum" not in texto
    assert "Jugador del día" in texto, "las secciones con datos sí salen"


# @scenarios el-resumen-no-recalcula
def test_el_marcador_del_resumen_es_el_mismo_que_publica_la_web():
    """Una segunda versión de las reglas dentro del publicador diría cosas distintas que la web."""
    from resumen import bloque_top
    from standings import clasificacion

    filas = historia("Ana", 10, score=3) + historia("Bea", 10, score=5) + historia("Cris", 10, score=4)

    lider = clasificacion(filas, "0")[0]
    bloque = bloque_top(filas, "0", 1509)

    primera = next(l for l in bloque.splitlines() if l.strip().startswith("1º"))
    assert lider["nombre"] in primera


# @scenarios el-mensaje-no-crece-con-el-grupo
def test_el_mensaje_no_crece_con_el_numero_de_jugadores():
    """La propiedad que hace que quepa en Slack no es un recorte, es que está acotado por construcción.

    El primer test de esto comparaba con el límite de 3000 y pasaba con 499 caracteres: no ejercitaba nada.
    Aquí se compara **el mensaje de un grupo pequeño con el de uno seis veces mayor**, que es lo que de
    verdad podría desbordarlo.
    """
    from resumen import LIMITE_DE_SLACK, TOP, resumen_del_dia

    def grupo(cuantos):
        filas = []
        for indice in range(cuantos):
            filas += historia(f"Jugador con nombre largo {indice}", 20, score=1 + indice % 6)
        return filas + [resultado("Jugador con nombre largo 0", HOY, 2, LORO)]

    pequeno = resumen_del_dia(grupo(5), "0", HOY)
    grande = resumen_del_dia(grupo(30), "0", HOY)

    assert len(grande) < len(pequeno) * 1.5, "seis veces más gente no puede dar un mensaje mucho mayor"
    assert len(grande) <= LIMITE_DE_SLACK
    # Se cuentan las LÍNEAS del bloque del top, no los prefijos "1.": con puestos compartidos varios
    # jugadores llevan el mismo número y ese proxy dejó de medir lo que decía medir.
    def filas_del_top(texto):
        bloque = texto.split("📊 *Marcador")[1].split("\n\n")[0]
        return len(bloque.splitlines())

    assert "Marcador" in grande
    # La propiedad: el bloque del marcador NO crece con el grupo. Se comparan los dos entre sí en lugar de
    # contra un número fijo, porque con empates el recuento depende de cuántos comparten puesto y lo que
    # importa es que seis veces más gente no produzca un bloque mayor.
    assert filas_del_top(grande) == filas_del_top(pequeno)
    assert filas_del_top(grande) <= TOP + 1, "el encabezado más como mucho cinco puestos"


# @scenarios el-resumen-se-enciende-con-una-variable
def test_el_resumen_va_apagado_por_defecto():
    """Mergear a `main` cambia lo que el cron ejecuta esa tarde: el mensaje no puede cambiar solo."""
    import os

    from post_ranking import OBJETIVOS, comentario, resumen_activo

    filas = historia("Ana", 6) + [resultado("Ana", HOY, 2, LORO)]
    previo = os.environ.pop("RESUMEN_COMPUESTO", None)
    try:
        assert resumen_activo() is False
        apagado = comentario("", OBJETIVOS["v1"], filas)
        assert "Jugador del día" not in apagado
        assert "ranking actualizado" in apagado, "el mensaje de siempre sigue saliendo"

        os.environ["RESUMEN_COMPUESTO"] = "1"
        assert resumen_activo() is True
        assert "Jugador del día" in comentario("", OBJETIVOS["v1"], filas)
    finally:
        os.environ.pop("RESUMEN_COMPUESTO", None)
        if previo is not None:
            os.environ["RESUMEN_COMPUESTO"] = previo
