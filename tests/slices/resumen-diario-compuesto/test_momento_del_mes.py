"""El resumen sabe en qué momento del mes está, de `resumen-diario-compuesto` (Fase 2 — TDD rojo).

Pack: `feat-resumen-con-podios`. Septiembre de 2026 acaba en miércoles 30: el viernes 25 tiene por delante el
28, el 29 y el 30.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fixtures_mes import TEMPORADA, jornada_de, marca, mes, nivel  # noqa: E402



def momento(hoy: str, filas=None, niveles=(), marcas=()):
    from resumen import bloque_momento_del_mes

    return bloque_momento_del_mes(filas or mes(hoy), TEMPORADA, jornada_de(hoy), niveles=niveles, marcas=marcas)


# @scenarios el-mes-arranca
def test_la_segunda_jornada_del_mes_arranca_sin_recta_final():
    texto = momento("2026-09-02")

    assert texto, "hay línea de arranque"
    assert "quedan" not in texto.lower() and "recta final" not in texto.lower()


# @scenarios la-recta-final-cuenta-lo-que-queda
def test_la_recta_final_dice_cuantas_quedan_quien_manda_la_distancia_y_que_el_empate_se_comparte():
    # Bea hace un 4 un día: 1/19 de media por detrás de Ana, que se publica como 0,05.
    filas = mes("2026-09-25", cambios={("Bea", "2026-09-10"): 4})

    texto = momento("2026-09-25", filas=filas)

    assert "quedan 3 jornadas" in texto.lower()
    assert "Ana" in texto and "Bea" in texto
    assert "0,05" in texto
    assert "comparte" in texto.lower(), "un empate a final de mes comparte el primer puesto"


# @scenarios la-recta-final-dice-si-el-juego-sigue-abierto
def test_con_doce_de_ventaja_y_veinte_en_juego_el_segundo_aun_puede():
    # Ana gana el 28 sola y el 29 por delante de Bea: 20 frente a 8. El 30 queda el nivel del 29 abierto y el
    # del propio 30 por jugar: dos niveles, 20 puntos.
    niveles = [nivel("2026-09-28"), nivel("2026-09-29")]
    marcas = [marca("2026-09-28", "Ana", 30), marca("2026-09-29", "Ana", 30), marca("2026-09-29", "Bea", 35)]

    texto = momento("2026-09-30", niveles=niveles, marcas=marcas)

    assert "20 puntos" in texto
    assert "todavía puede" in texto.lower()


# @scenarios la-recta-final-dice-si-el-juego-sigue-abierto
def test_con_mas_ventaja_que_puntos_en_juego_se_dice_que_ya_no_puede():
    # Ana gana los cuatro niveles (40) y Bea es segunda en el último (8): 32 de ventaja con 20 en juego.
    fechas = ["2026-09-24", "2026-09-25", "2026-09-28", "2026-09-29"]
    niveles = [nivel(f) for f in fechas]
    marcas = [marca(f, "Ana", 30) for f in fechas] + [marca("2026-09-29", "Bea", 35)]

    texto = momento("2026-09-30", niveles=niveles, marcas=marcas)

    assert "ya no puede" in texto.lower()


# @scenarios la-ultima-jornada-se-anuncia
def test_el_ultimo_laborable_se_anuncia_como_ultima_jornada():
    texto = momento("2026-09-30")

    assert "última jornada" in texto.lower()
    assert "quedan 0" not in texto.lower()


# @scenarios a-mitad-de-mes-no-hay-bloque-de-tension
def test_a_mitad_de_mes_no_hay_bloque():
    assert momento("2026-09-16") == ""


# @scenarios el-momento-del-mes-sale-de-la-jornada
def test_el_momento_del_mes_no_lee_el_reloj():
    from resumen import bloque_momento_del_mes

    fuente = inspect.getsource(bloque_momento_del_mes)

    for reloj in ("now(", "today(", "time.time", "utcnow("):
        assert reloj not in fuente, f"el momento del mes no puede leer el reloj ({reloj})"
    assert momento("2026-09-25") == momento("2026-09-25")
