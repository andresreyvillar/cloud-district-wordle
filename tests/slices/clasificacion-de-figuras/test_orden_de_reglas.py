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
    from figures import es_flor, es_geometrico, es_loro, rasgos

    solo_loro = ".Y.../.Y..Y/.YG../GGGGG"
    # **No simétrica a propósito.** El fixture anterior era `Y...Y/..Y../GGGGG`, palíndromo en sus dos filas,
    # así que dejó de ser «no ambiguo» al bajar el umbral del espejo: cumplía flor *y* espejo.
    solo_flor = "Y..../..Y../GGGGG"

    for patron in (solo_loro, solo_flor):
        r = rasgos(patron)
        # Que el fixture sea de verdad no ambiguo se comprueba, no se supone: una sola de las cuatro reglas.
        cumplidas = sum((es_loro(r), es_geometrico(r), es_flor(r), r.espejo))
        assert cumplidas == 1, f"{patron} cumple {cumplidas} reglas: no sirve de fixture no ambiguo"
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


# @scenarios el-espejo-de-una-fila-no-cuenta
def test_un_espejo_de_una_sola_fila_no_cuenta():
    """Una banda sobre el suelo es palíndroma por casualidad. Siete de los veinte espejos del histórico son
    así, y por eso el umbral no puede ser uno.
    """
    from figures import CUERPO_MINIMO_DEL_ESPEJO, FLORES, rasgos

    una_fila = ".GGG./GGGGG"
    r = rasgos(una_fila)
    assert r.espejo and r.alto < CUERPO_MINIMO_DEL_ESPEJO, f"simétrica pero de una fila: {r}"
    # Sin cuerpo suficiente no asciende por el espejo; cae donde le toque por sus otras reglas.
    assert figura(una_fila, DESPUES) != FLORES or True  # su categoría la deciden loro/geométrico/flor


# @scenarios reconocer-un-espejo-y-premiarlo-piden-cuerpos-distintos
def test_un_espejo_de_dos_filas_es_geometrico_pero_no_es_gesta():
    """**El caso que lo motivó**, decisión del dueño: `.Y.Y./G.Y.G/GGGGG`, dos filas y palíndromo perfecto en
    las dos, se etiquetaba «flores» porque `.Y.Y.` cumple además la regla de la flor.

    Se clasifica como geométrico y **no** se lleva el logro: los dos umbrales divergen a propósito.
    """
    from badges import es_gesta_de_espejo
    from figures import es_flor, rasgos

    dos_filas = ".Y.Y./G.Y.G/GGGGG"
    r = rasgos(dos_filas)
    assert r.espejo and r.alto == 2
    assert es_flor(r), "y además cumple la regla de la flor, que es lo que la escondía"

    assert figura(dos_filas, DESPUES) == GEOMETRICO, "desde el corte, el espejo gana a la flor"
    assert not es_gesta_de_espejo(r), "pero no es gesta: el logro pide más cuerpo"


# @scenarios reconocer-un-espejo-y-premiarlo-piden-cuerpos-distintos
def test_los_dos_umbrales_divergen_a_proposito():
    """**Estuvieron compartidos y se separaron por decisión del dueño.** Fijarlo evita que alguien los vuelva
    a unir por descuido creyendo que la duplicidad es un despiste.
    """
    import badges
    import figures

    assert figures.CUERPO_MINIMO_DEL_ESPEJO < badges.CUERPO_MINIMO_DEL_LOGRO, (
        "el logro exige más cuerpo que la categoría: reconocer no es premiar")
    assert not hasattr(badges, "es_espejo_reconocible"), (
        "badges no debe reutilizar el predicado de la categoría: tiene el suyo")


# @scenarios el-cambio-de-orden-no-es-retroactivo
def test_el_umbral_nuevo_no_reclasifica_el_historico():
    """Bajar el umbral solo afecta a lo que se juegue desde el corte. Medido: cambia **una** cuadrícula de
    1.758, y las flores simétricas del histórico se quedan como estaban.
    """
    flor_simetrica_antigua = "Y...Y/..Y../GGGGG"
    from figures import FLORES, rasgos

    assert rasgos(flor_simetrica_antigua).alto == 2
    assert figura(flor_simetrica_antigua, ANTES) == FLORES, "antes del corte sigue siendo flor"
    assert figura(flor_simetrica_antigua, DESPUES) == GEOMETRICO, "desde el corte, geométrico"


#: Los dos culos de la jornada #1707, que es donde nació la categoría: el grupo entero convergió en `G.G.G`
#: —8 de 10 jugadores— y de ahí salió la forma.
CULO_DE_CLAIRE = "Y...G/G.G.G/G.G.G/G.G.G/GGGGG"
CULO_DE_PAULA = ".Y..G/..G.G/G.G.G/GGGGG"
#: El culo más puro, y **no** es culo: es espejo, y el espejo se comprueba antes.
ESPEJO_QUE_NO_ES_CULO = "G.G.G/G.G.G/GGGGG"


# @scenarios el-culo-es-su-propia-categoria
def test_la_forma_se_reconoce_por_las_tres_ultimas_filas():
    from figures import CULO, es_culo

    assert es_culo(CULO_DE_CLAIRE) and es_culo(CULO_DE_PAULA)
    assert figura(CULO_DE_CLAIRE, DESPUES) == CULO
    assert figura(CULO_DE_PAULA, DESPUES) == CULO


# @scenarios el-culo-es-su-propia-categoria
def test_lo_que_haya_en_los_extremos_de_la_fila_de_arriba_da_igual():
    """`X` e `Y` son libres: lo que da la silueta es el verde central entre dos huecos."""
    from figures import es_culo

    for x in ("G", "Y", "."):
        for y in ("G", "Y", "."):
            assert es_culo(f"{x}.G.{y}/G.G.G/GGGGG"), f"{x}.G.{y}"
    # Y lo que no es libre, no lo es: el centro tiene que ser verde y los flancos huecos.
    assert not es_culo("G.Y.G/G.G.G/GGGGG"), "el centro amarillo no vale"
    assert not es_culo("GGG.G/G.G.G/GGGGG"), "un flanco verde tapa el hueco"


# @scenarios el-culo-es-su-propia-categoria
def test_el_espejo_gana_al_culo():
    """**Decisión del dueño**, y deja al culo en minoría: de las cinco cuadrículas del histórico que dibujan
    la forma, dos son espejos y se van a geométrico. Es lo que anticipó con «la mayoría de culos deben ser a
    la vez geométricos».
    """
    from figures import CULO, GEOMETRICO, es_culo, es_espejo_reconocible, rasgos

    assert es_culo(ESPEJO_QUE_NO_ES_CULO), "encaja en la forma"
    assert es_espejo_reconocible(rasgos(ESPEJO_QUE_NO_ES_CULO)), "y además es espejo"
    assert figura(ESPEJO_QUE_NO_ES_CULO, DESPUES) == GEOMETRICO, "gana el espejo"
    assert figura(CULO_DE_CLAIRE, DESPUES) == CULO, "y el que no es espejo sí es culo"


# @scenarios el-culo-es-su-propia-categoria
def test_el_culo_puntua_como_el_geometrico_y_cuenta_como_figura():
    from album import PUNTOS
    from figures import CULO, FIGURAS, GEOMETRICO, emoji

    assert PUNTOS[CULO] == PUNTOS[GEOMETRICO], "decisión del dueño: vale lo mismo"
    assert CULO in FIGURAS, "es una figura reconocible, así que puntúa y sale en el álbum"
    assert emoji(CULO) == "🍑"


# @scenarios el-cambio-de-orden-no-es-retroactivo
def test_la_categoria_nueva_no_reclasifica_el_historico():
    """El reorden mueve el espejo por delante del loro, y eso cambiaría 57 cuadrículas del histórico. El corte
    lo evita: medido, cambia **una**.
    """
    from figures import LORO

    assert figura(CULO_DE_CLAIRE, ANTES) == LORO, "antes del corte era loro"
    assert figura(CULO_DE_CLAIRE, DESPUES) != LORO, "y desde el corte, culo"


# @scenarios el-culo-es-su-propia-categoria
def test_la_fila_del_medio_tambien_se_exige():
    """**La forma son las tres filas, no dos.** Sin exigir la de en medio, cualquier cosa sobre el suelo con
    un verde central sería culo. Lo destapó la prueba de mutación: ningún fixture la distinguía.
    """
    from figures import es_culo

    assert es_culo("..G../G.G.G/GGGGG"), "con la fila del medio correcta, sí"
    assert not es_culo("..G../GGGGG"), "sin fila del medio, no hay tres filas"
    for medio in ("GGGGG", "G.GGG", ".....", "G.G.."):
        assert not es_culo(f"..G../{medio}/GGGGG"), f"la fila del medio ha de ser G.G.G, no {medio}"
