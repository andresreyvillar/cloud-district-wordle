"""Escenarios de las menciones, de `voz-de-la-jornada` (Fase 2 — TDD rojo).

Pack: `feat-voz-de-la-jornada`. Fixtures sintéticos: ver la nota de `test_senales.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

MOTIVO = "TDD rojo — tools/voz.py no existe todavía"


# @scenarios el-mas-aplaudido-se-nombra, sin-reacciones-no-hay-premio
def test_sin_reacciones_no_hay_mas_aplaudido():
    """La mención sin evidencia no se concede: coronar a alguien con cero reacciones es inventarse el premio."""
    from voz import menciones

    assert "aplaudido" not in menciones(reacciones={}, respuestas={}, publicacion={}, nombres={})


# @scenarios el-mas-aplaudido-se-nombra
def test_el_empate_en_reacciones_nombra_a_todos():
    from voz import menciones

    m = menciones(
        reacciones={"U1": 5, "U2": 5, "U3": 1},
        respuestas={},
        publicacion={},
        nombres={"U1": "Ana", "U2": "Bea", "U3": "Cris"},
    )

    assert "Ana" in m["aplaudido"] and "Bea" in m["aplaudido"]
    assert "Cris" not in m["aplaudido"]


# @scenarios el-que-madruga-se-nombra, el-que-lo-deja-para-el-final-se-nombra
def test_con_una_sola_persona_no_hay_madrugador():
    from voz import menciones

    m = menciones(reacciones={}, respuestas={}, publicacion={"U1": 1788249600.0}, nombres={"U1": "Ana"})

    assert "madrugador" not in m and "rezagado" not in m, "sin nadie con quien comparar no hay comparación"


#: Marcas de tiempo fijas, en segundos. Sin reloj: el determinismo es contrato (§10).
BASE = 1788249600.0


def _en_minutos(*minutos: float) -> dict[str, float]:
    return {f"U{i}": BASE + m * 60 for i, m in enumerate(minutos, 1)}


NOMBRES = {f"U{i}": n for i, n in enumerate(("Ana", "Bea", "Cris", "Dani"), 1)}


# @scenarios el-que-madruga-se-nombra
def test_el_madrugador_necesita_su_hora_de_ventaja():
    """**El umbral está medido, así que hay que protegerlo.**

    60 minutos salen en el 24% de las 187 jornadas del canal; 30 en el 41%. La prueba de mutación cazó que
    ningún test cubría esto: bajar el número habría convertido la mención en una columna sin que nadie lo
    notara.
    """
    from voz import HUECO_DEL_MADRUGADOR, menciones

    assert HUECO_DEL_MADRUGADOR == 60

    justo = menciones(reacciones={}, respuestas={}, publicacion=_en_minutos(0, 60, 70), nombres=NOMBRES)
    assert "Ana" in justo["madrugador"]

    corto = menciones(reacciones={}, respuestas={}, publicacion=_en_minutos(0, 59, 70), nombres=NOMBRES)
    assert "madrugador" not in corto, "con 59 minutos no madruga: el umbral es una hora"


# @scenarios el-que-lo-deja-para-el-final-se-nombra
def test_el_rezagado_necesita_cuatro_horas():
    """Medido: 240 minutos salen en el 24% de las jornadas, 30 en el 65%.

    La tarde está dispersa, así que un hueco corto le pasa a dos de cada tres jornadas. Lo cazó la mutación.
    """
    from voz import HUECO_DEL_REZAGADO, menciones

    assert HUECO_DEL_REZAGADO == 240

    justo = menciones(reacciones={}, respuestas={}, publicacion=_en_minutos(0, 10, 250), nombres=NOMBRES)
    assert "Cris" in justo["rezagado"]

    corto = menciones(reacciones={}, respuestas={}, publicacion=_en_minutos(0, 10, 249), nombres=NOMBRES)
    assert "rezagado" not in corto, "con 239 minutos de hueco no es un rezagado: el umbral son cuatro horas"


# @scenarios el-mas-aplaudido-se-nombra
def test_un_empate_multitudinario_no_premia_a_nadie():
    """Señalar a doce personas no señala a nadie, y encima hace crecer el mensaje con el grupo."""
    from voz import MAXIMO_NOMBRADOS, menciones

    muchos = {f"U{i}": 4 for i in range(1, MAXIMO_NOMBRADOS + 2)}

    assert "aplaudido" not in menciones(
        reacciones=muchos, respuestas={}, publicacion={}, nombres=NOMBRES
    )
