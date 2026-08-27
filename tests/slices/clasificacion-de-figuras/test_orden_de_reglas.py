"""El orden de las reglas cambió, y el cambio no es retroactivo.

Fixtures locales, nunca producción. Los `wordle_id` se eligen a los dos lados del corte.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from figures import (
    GEOMETRICO,
    LORO,
    PRIMERA_JORNADA_DEL_ORDEN_NUEVO,
    es_geometrico,
    es_loro,
    figura,
    orden_nuevo,
)

#: Cumple **las dos** reglas a la vez: es el único patrón donde el orden decide.
#: Sale de un fixture real del proyecto, y es uno de los 42 que el reorden mueve.
AMBIGUO = ".G.../.G..G/.GY../GGGGG"

ANTES = PRIMERA_JORNADA_DEL_ORDEN_NUEVO - 1
DESPUES = PRIMERA_JORNADA_DEL_ORDEN_NUEVO


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
    assert not orden_nuevo(None)


# @scenarios el-cambio-de-orden-no-es-retroactivo
def test_el_corte_es_inclusivo():
    """«A partir de hoy» incluye hoy: la jornada del corte ya se clasifica con el orden nuevo."""
    assert orden_nuevo(PRIMERA_JORNADA_DEL_ORDEN_NUEVO)
    assert not orden_nuevo(PRIMERA_JORNADA_DEL_ORDEN_NUEVO - 1)


# @scenarios la-geometria-se-decide-antes-que-el-loro
def test_un_patron_no_ambiguo_no_depende_del_orden():
    """Solo se mueve lo que cumple las dos reglas: el resto del álbum no se entera del cambio."""
    solo_loro = ".Y.../.Y..Y/.YG../GGGGG"
    solo_flor = "Y...Y/..Y../GGGGG"
    for patron in (solo_loro, solo_flor):
        assert figura(patron, ANTES) == figura(patron, DESPUES), patron


#: La cuadrícula que motivó el cambio: cuatro filas de cuerpo, simétrica, y que cumple la regla de la flor.
ESPEJO_QUE_ERA_FLOR = "Y...Y/GG.GG/GG.GG/GG.GG/GGGGG"
#: Simétrica pero de dos filas: simetría por accidente, y una flor de verdad.
FLOR_CASI_SIMETRICA = "Y...Y/..Y../GGGGG"


# @scenarios desde-el-corte-el-espejo-gana-a-la-flor
def test_desde_el_corte_el_espejo_gana_a_la_flor():
    from figures import FLORES, es_flor, rasgos

    r = rasgos(ESPEJO_QUE_ERA_FLOR)
    assert r.espejo and es_flor(r), f"el fixture debe cumplir las dos: {r}"
    assert figura(ESPEJO_QUE_ERA_FLOR, ANTES) == FLORES, "antes del corte era flor"
    assert figura(ESPEJO_QUE_ERA_FLOR, DESPUES) == GEOMETRICO, "desde el corte es geométrico"


# @scenarios el-espejo-de-una-o-dos-filas-no-cuenta
def test_un_espejo_de_dos_filas_sigue_siendo_flor():
    """**La incoherencia que casi se publica.** Con el umbral solo en el logro, este espejo de dos filas
    —que el logro considera un accidente— le quitaba la categoría a una flor legítima. Lo destaparon los
    tests del álbum, cuyo fixture de flor resulta ser simétrico.
    """
    from figures import CUERPO_MINIMO_DEL_ESPEJO, FLORES, rasgos

    r = rasgos(FLOR_CASI_SIMETRICA)
    assert r.espejo and r.alto < CUERPO_MINIMO_DEL_ESPEJO, f"simétrica pero corta: {r}"
    assert figura(FLOR_CASI_SIMETRICA, DESPUES) == FLORES, "sigue siendo flor pasado el corte"


# @scenarios el-espejo-de-una-o-dos-filas-no-cuenta
def test_el_logro_y_la_categoria_usan_el_mismo_umbral():
    """Un solo predicado para las dos reglas: duplicarlo las hacía discrepar sobre qué es un espejo."""
    import badges
    import figures

    assert badges.es_espejo_reconocible is figures.es_espejo_reconocible
    assert badges.CUERPO_MINIMO_DEL_ESPEJO == figures.CUERPO_MINIMO_DEL_ESPEJO
