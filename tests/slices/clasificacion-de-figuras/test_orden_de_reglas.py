"""El orden de las reglas cambió, y el cambio no es retroactivo.

Fixtures locales, nunca producción. Los `wordle_id` se eligen a los dos lados del corte.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from figures import (
    GEOMETRICO,
    LORO,
    PRIMERA_JORNADA_GEOMETRIA_PRIMERO,
    es_geometrico,
    es_loro,
    figura,
    geometria_primero,
)

#: Cumple **las dos** reglas a la vez: es el único patrón donde el orden decide.
#: Sale de un fixture real del proyecto, y es uno de los 42 que el reorden mueve.
AMBIGUO = ".G.../.G..G/.GY../GGGGG"

ANTES = PRIMERA_JORNADA_GEOMETRIA_PRIMERO - 1
DESPUES = PRIMERA_JORNADA_GEOMETRIA_PRIMERO


def test_el_fixture_es_ambiguo_de_verdad():
    """Sin esto el resto no prueba nada: un patrón que solo cumple una regla da igual en qué orden se mire."""
    from figures import rasgos

    r = rasgos(AMBIGUO)
    assert es_loro(r) and es_geometrico(r), f"el fixture debe cumplir las dos reglas: {r}"


# @scenarios la-geometria-se-decide-antes-que-el-loro
def test_desde_el_corte_la_geometria_gana():
    assert figura(AMBIGUO, DESPUES) == GEOMETRICO


# @scenarios el-cambio-de-orden-no-es-retroactivo
def test_antes_del_corte_sigue_siendo_loro():
    assert figura(AMBIGUO, ANTES) == LORO


# @scenarios el-cambio-de-orden-no-es-retroactivo
def test_sin_jornada_se_usa_el_orden_historico():
    """Las herramientas que clasifican un patrón fuera de contexto —la calibración contra el etiquetado
    humano— se hicieron con las reglas de entonces, así que sin jornada no se aplica el orden nuevo.
    """
    assert figura(AMBIGUO) == LORO
    assert not geometria_primero(None)


# @scenarios el-cambio-de-orden-no-es-retroactivo
def test_el_corte_es_inclusivo():
    """«A partir de hoy» incluye hoy: la jornada del corte ya se clasifica con el orden nuevo."""
    assert geometria_primero(PRIMERA_JORNADA_GEOMETRIA_PRIMERO)
    assert not geometria_primero(PRIMERA_JORNADA_GEOMETRIA_PRIMERO - 1)


# @scenarios la-geometria-se-decide-antes-que-el-loro
def test_un_patron_no_ambiguo_no_depende_del_orden():
    """Solo se mueve lo que cumple las dos reglas: el resto del álbum no se entera del cambio."""
    solo_loro = ".Y.../.Y..Y/.YG../GGGGG"
    solo_flor = "Y...Y/..Y../GGGGG"
    for patron in (solo_loro, solo_flor):
        assert figura(patron, ANTES) == figura(patron, DESPUES), patron
