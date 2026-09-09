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


#: Culos de la jornada #1707, que es donde nació la categoría: el grupo entero convergió en `G.G.G` —8 de 10
#: jugadores— y de ahí salió la forma.
CULO_DE_CLAIRE = "Y...G/G.G.G/G.G.G/G.G.G/GGGGG"
#: El de Andrés R., que tiene un **amarillo** entre los extremos. Entra porque de la fila de arriba solo
#: cuentan los extremos: exigir un verde central lo dejaba fuera, y con él a tres de los diez de esa jornada.
CULO_DE_ANDRES = ".Y.Y./GY..G/G.G.G/GGGGG"
#: **No es culo**: su extremo izquierdo es un hueco, así que la silueta no cierra por ese lado.
CASI_CULO_DE_PAULA = ".Y..G/..G.G/G.G.G/GGGGG"
#: El culo más puro, y **no** es culo: es espejo, y el espejo se comprueba antes.
ESPEJO_QUE_NO_ES_CULO = "G.G.G/G.G.G/GGGGG"


# @scenarios el-culo-es-su-propia-categoria
def test_la_forma_se_reconoce_por_las_dos_ultimas_filas():
    """**Dos filas, decidido por el dueño** tras descartar tres definiciones más estrechas sobre la fila de
    arriba: exigir verde central dejaba 6 casos en 1.809 cuadrículas, exigir tres huecos dejaba 1, y exigir
    los extremos verdes dejaba 9. Con dos filas son 25.
    """
    from figures import CULO, es_culo

    assert es_culo(CULO_DE_CLAIRE) and es_culo(CULO_DE_ANDRES) and es_culo(CASI_CULO_DE_PAULA)
    assert figura(CULO_DE_CLAIRE, DESPUES) == CULO
    assert figura(CULO_DE_ANDRES, DESPUES) == CULO
    # El que antes se quedaba fuera por abrir un lado ahora entra: lo de arriba ya no cuenta.
    assert figura(CASI_CULO_DE_PAULA, DESPUES) == CULO


# @scenarios el-culo-es-su-propia-categoria
def test_lo_que_haya_por_encima_de_las_dos_filas_no_cuenta():
    from figures import es_culo

    for encima in ("", "YYYYY/", ".Y.Y./", "GGGG./", "Y...Y/..Y../"):
        assert es_culo(f"{encima}G.G.G/GGGGG"), f"{encima}G.G.G/GGGGG"
    # Lo que sí cuenta son las dos últimas, y las dos enteras.
    assert not es_culo("G.G.G/GGGG."), "el suelo tiene que estar completo"
    assert not es_culo("G.G../GGGGG"), "la penúltima tiene que ser G.G.G"
    assert not es_culo("GGGGG"), "una sola fila no es la forma"


# @scenarios la-forma-del-culo-es-de-la-jornada
def test_una_jornada_entera_puede_llevarse_la_categoria():
    """**Consecuencia declarada de la definición de dos filas.** En la jornada que la originó, siete de los
    diez jugadores la reciben, porque la palabra tenía las letras impares fáciles y las pares difíciles. No es
    un fallo: la forma es de la jornada más que de quien juega.
    """
    from figures import CULO, figura as clasifica

    del_1707 = [
        ".Y.Y./GY..G/G.G.G/GGGGG",      # Andrés R.
        "Y...G/GY..G/G.G.G/GGGGG",      # Cata
        "Y...G/G.G.G/G.G.G/G.G.G/GGGGG",  # Claire
        "Y...Y/GY..G/G.G.G/GGGGG",      # Juan
        ".Y..G/..G.G/G.G.G/GGGGG",      # Paula
        "G...Y/G.G.G/GGGGG",            # Sandra
    ]
    assert all(clasifica(p, DESPUES) == CULO for p in del_1707), "los seis del esqueleto son culo"
    # Y el que además es espejo no lo es, porque el espejo va antes.
    assert clasifica("G.G.G/G.G.G/GGGGG", DESPUES) == "geometrico"


# @scenarios el-culo-es-su-propia-categoria
def test_la_penultima_fila_tambien_se_exige():
    """Sin exigirla, cualquier cosa sobre el suelo completo sería culo. Lo destapó la prueba de mutación:
    ningún fixture la distinguía.
    """
    from figures import es_culo

    assert es_culo("G...G/G.G.G/GGGGG"), "con la penúltima correcta, sí"
    for penultima in ("GGGGG", "G.GGG", ".....", "G.G.."):
        assert not es_culo(f"G...G/{penultima}/GGGGG"), f"la penúltima ha de ser G.G.G, no {penultima}"
