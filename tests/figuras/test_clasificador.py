"""El examen del clasificador de figuras: las 30 etiquetas humanas.

Pack: `feat-calibracion-de-figuras` (Slice: N/A — el paso 5.0 del roadmap).

**El conjunto dorado no se copia aquí.** Se parsea del source
(`docs/context/sources/2026-08-05-etiquetado-de-patrones.md`), que es la autoridad declarada. Copiarlo
crearía dos verdades y la copia se quedaría atrás en cuanto alguien reetiquetara una ficha.

El test que importa es `test_el_acuerdo_con_las_etiquetas_humanas_no_baja`: convierte el acierto medido en
un **gate**. Cualquier cambio de umbral que baje del acuerdo actual pone la suite en rojo, que es lo
contrario de lo que pasó con la heurística anterior —nadie la midió hasta que ya estaba escrita en un brief.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
FUENTE = RAIZ / "docs/context/sources/2026-08-05-etiquetado-de-patrones.md"

#: Fichas que el clasificador tiene que acertar de las 30. **Es el gate.**
#:
#: 24 es lo medido, no una aspiración: subirlo sin volver a calibrar rompe la suite, y bajarlo requiere
#: explicar por qué se acepta un clasificador peor. Con 30 fichas el margen es de ±9 puntos
#: (ver «Límite honesto» en el brief), así que este número distingue «80% o 60%», no «80% u 84%».
ACUERDO_MINIMO = 24

#: Las cuatro categorías del vocabulario fijado el 2026-08-05.
VOCABULARIO = ("loro", "flores", "geometrico", "abstracto")

#: Las que cuentan como figura reconocible. `abstracto` no es una figura: es la ausencia de figura.
FIGURAS = ("loro", "flores", "geometrico")


def conjunto_dorado() -> list[dict]:
    """Las 30 fichas etiquetadas a mano, parseadas del source.

    `loto` se pliega en `flores`: apareció una sola vez y con un ejemplo no se calibra nada, se acierta
    por azar (decisión registrada en el brief).
    """
    fichas = []
    for bloque in re.finditer(
        r"^## (\d+) · #(\d+) · (\d+) intentos\n```\n(.*?)```\netiqueta: (\w+)",
        FUENTE.read_text(encoding="utf-8"),
        re.M | re.S,
    ):
        ficha, puzzle, intentos, rejilla, etiqueta = bloque.groups()
        fichas.append(
            {
                "ficha": ficha,
                "puzzle": int(puzzle),
                "intentos": int(intentos),
                "patron": "/".join(linea for linea in rejilla.strip().split("\n") if linea.strip()),
                "etiqueta": "flores" if etiqueta == "loto" else etiqueta,
            }
        )
    return fichas


def test_el_conjunto_dorado_se_lee_completo():
    """Si el parseo se rompe, el examen se aprueba con cero preguntas: eso hay que cazarlo aquí."""
    fichas = conjunto_dorado()

    assert len(fichas) == 30, "el conjunto dorado son 30 fichas"
    assert all(f["etiqueta"] in VOCABULARIO for f in fichas), "hay una etiqueta fuera del vocabulario"
    reparto = {e: sum(1 for f in fichas if f["etiqueta"] == e) for e in VOCABULARIO}
    assert reparto == {"loro": 5, "flores": 11, "geometrico": 4, "abstracto": 10}, reparto


def test_el_acuerdo_con_las_etiquetas_humanas_no_baja():
    """EL test del pack: el acierto medido, convertido en gate."""
    from tools.figures import figura

    fichas = conjunto_dorado()
    fallos = [
        f"{f['ficha']}: humano {f['etiqueta']} → {figura(f['patron'])}"
        for f in fichas
        if figura(f["patron"]) != f["etiqueta"]
    ]
    aciertos = len(fichas) - len(fallos)

    assert aciertos >= ACUERDO_MINIMO, (
        f"acuerdo {aciertos}/30, por debajo del gate ({ACUERDO_MINIMO}). Fallos:\n" + "\n".join(fallos)
    )


def test_ninguna_categoria_se_come_el_conjunto():
    """El fallo de la heurística anterior: el 69% de abstractos.

    No mide acierto sino **reparto**, que es un criterio independiente: un clasificador puede acertar
    fichas sueltas y seguir mandando media liga a la papelera.
    """
    from tools.figures import figura

    fichas = conjunto_dorado()
    reparto = {e: sum(1 for f in fichas if figura(f["patron"]) == e) for e in VOCABULARIO}

    for categoria, cuantas in reparto.items():
        assert cuantas <= 15, f"{categoria} se lleva {cuantas} de 30: una categoría domina el reparto"
    assert reparto["abstracto"] <= 13, (
        f"abstracto se lleva {reparto['abstracto']} de 30; el humano etiquetó 10"
    )


def test_una_cuadricula_sin_resolver_no_tiene_figura():
    """Sin banda verde final no hay suelo, y sin suelo no hay flor. Las 3 falladas del conjunto lo son."""
    from tools.figures import figura

    assert figura("YG.Y./.GGGG/.GGGG/.GGGG/.GGGG/.GGGG") == "abstracto"


def test_una_cuadricula_sin_dibujo_no_tiene_figura():
    """Un 1/6 acierta a la primera y no deja lienzo: no es geométrico, es que no hay nada."""
    from tools.figures import figura

    assert figura("GGGGG") == "abstracto"


def test_el_amarillo_del_loro_toca_el_cuerpo():
    """El rasgo que decidió la calibración.

    Las dos cuadrículas son la misma columna verde con la misma cantidad de amarillo. La diferencia es
    dónde está el amarillo: pegado al cuerpo es un pico; flotando en negro son pétalos. Sin esta
    distinción el loro se comía dos flores del conjunto.
    """
    from tools.figures import figura

    assert figura("....G/.G..G/YG..G/GGGGG") == "loro", "amarillo pegado al cuerpo: es el pico"
    assert figura("Y..../.G.Y./.GG.G/.GG.G/.GGGG/GGGGG") == "flores", "amarillos flotando: son pétalos"


def test_dos_amarillos_perdidos_no_hacen_una_flor():
    """La ficha 11 del conjunto: columna verde al borde y dos amarillos sueltos. El humano dijo abstracto.

    Este test existe porque un mutante sobrevivió al gate de acuerdo. Bajar el mínimo de pétalos libres de
    tres a uno **sube** el acierto a 25/30 —rescata las fichas 01 y 26— y sin embargo es peor: lo que
    justifica el tres es el reparto sobre producción, y ese criterio no cabe en la suite porque necesita
    red. Sin este caso, el umbral quedaba sin proteger por ningún test.
    """
    from tools.figures import figura

    assert figura("....G/..Y.G/.Y..G/GGGGG") == "abstracto"


def test_alargar_la_cuadricula_no_convierte_el_ruido_en_flor():
    """El fallo que descartó al primer candidato, convertido en propiedad.

    Aquel clasificador sacaba 83% de acuerdo y marcaba flor el 55% de producción, porque su regla se
    cumplía más según crecía la cuadrícula: en seis intentos casi siempre hay una fila verde ancha y algún
    amarillo. Una regla de figura **no puede volverse más probable solo porque la partida sea larga**.
    """
    from tools.figures import figura

    corta = ".G..G/.GG.G/GGGGG"
    larga = ".G..G/.GG.G/.GG.G/.GG.G/.GG.G/GGGGG"

    assert figura(corta) != "flores"
    assert figura(larga) != "flores", "la misma forma, más larga, no puede pasar a ser una flor"


def test_las_dos_formas_del_patron_dan_lo_mismo():
    """La ingesta guarda `G/Y/.` separado por barras; el conjunto dorado está en emoji.

    Las dos entran, y tienen que salir por el mismo sitio: si divergieran, el examen mediría una cosa y
    producción haría otra.
    """
    from tools.figures import figura

    assert figura("⬛🟩⬛⬛⬛\n⬛🟩⬛⬛⬛\n🟩🟩🟩🟩🟩") == figura(".G.../.G.../GGGGG")


def test_el_clasificador_es_puro():
    """Dos llamadas con el mismo patrón dan lo mismo, y clasificar no muta la entrada (§10)."""
    from tools.figures import figura

    patron = "..Y../...Y./.GGG./GGGGG"
    assert figura(patron) == figura(patron)
    assert patron == "..Y../...Y./.GGG./GGGGG"


@pytest.mark.parametrize(
    "patron,esperado",
    [
        (".G.../.G.../GGGGG", "geometrico"),      # ficha 02: el tallo
        ("Y..../.GGG./GGGGG", "geometrico"),      # ficha 05: la pirámide
        ("Y..../.Y..Y/GGGGG", "flores"),          # ficha 03: pétalos sobre el suelo, sin verde
        (".G.../.G.../.GY../.G.GG/GGGGG", "loro"),  # ficha 22: columna, segundo elemento y pico
    ],
)
def test_las_figuras_del_vocabulario_salen_donde_el_humano_las_ve(patron, esperado):
    """Cuatro fichas del conjunto, una por categoría reconocible, fijadas de una en una.

    El test de acuerdo mide el conjunto entero; estas cuatro dicen *cuál* se rompió cuando baje.
    """
    from tools.figures import figura

    assert figura(patron) == esperado
