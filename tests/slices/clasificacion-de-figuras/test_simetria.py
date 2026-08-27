"""Escenarios del espejo, de `clasificacion-de-figuras` (Fase 2 — TDD rojo).

Pack: `feat-figuras-simetricas`.

Los fixtures de este fichero **no se dan por buenos**: cada cuadrícula declara qué pretende dibujar y
`test_los_fixtures_son_lo_que_dicen_ser` lo comprueba contra el clasificador antes de que se use en ningún
otro test. Es la lección que dejó este mismo slice: el fixture `ABSTRACTO` del otro fichero resultó ser
simétrico sin que nadie lo hubiera notado, y por eso el diseño de esta regla estuvo mal una versión entera.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from figures import ABSTRACTO, FIGURAS, FLORES, GEOMETRICO, LORO, figura, rasgos  # noqa: E402

MOTIVO = "TDD rojo — el espejo no existe todavía en tools/figures.py"

#: El arco: simétrico, densidad 0,60 —por encima del techo del geométrico— y sin un solo amarillo.
#: Es el caso que motiva la regla, y hoy sale abstracto.
ARCO = "G...G/GG.GG/GGGGG"

#: El mismo arco con una celda movida: deja de ser espejo y no debe rescatarse.
ARCO_ROTO = "G...G/GG.G./GGGGG"

#: Una flor simétrica. Es la trampa de la regla: unos pétalos son simétricos por naturaleza, así que un
#: espejo evaluado antes de la flor se la comería.
FLOR_SIMETRICA = "Y...Y/..Y../GGGGG"

#: Un loro simétrico, por la misma razón que el anterior.
LORO_SIMETRICO = "..G../.YGY./..G../..G../GGGGG"

#: Un acierto a la primera: la banda verde y nada más. Simétrica, pero sin cuerpo.
SOLO_LA_BANDA = "GGGGG"

#: Una cuadrícula simétrica que no llega a resolver: sin banda final no hay dibujo.
FALLADA_SIMETRICA = "G...G/GG.GG/G...G/GG.GG/G...G/GG.GG"


def test_los_fixtures_son_lo_que_dicen_ser():
    """Antes de probar nada: que los fixtures dibujen lo que su nombre promete."""
    assert figura(FLOR_SIMETRICA) == FLORES
    assert figura(LORO_SIMETRICO) == LORO
    assert figura(SOLO_LA_BANDA) == ABSTRACTO
    assert figura(FALLADA_SIMETRICA) == ABSTRACTO


# @scenarios espejo-exacto-es-geometrico
def test_un_dibujo_simetrico_con_mucha_tinta_es_geometrico():
    assert figura(ARCO) == GEOMETRICO


# @scenarios una-celda-rota-no-es-espejo
def test_una_sola_celda_rota_niega_el_espejo():
    assert figura(ARCO_ROTO) == ABSTRACTO


# @scenarios el-espejo-no-le-quita-figura-a-nadie-en-el-orden-historico
def test_el_espejo_no_le_quita_la_flor_a_unos_petalos_simetricos():
    assert figura(FLOR_SIMETRICA) == FLORES


# @scenarios el-espejo-no-le-quita-figura-a-nadie-en-el-orden-historico
def test_el_espejo_no_le_quita_el_loro_a_un_loro_simetrico():
    assert figura(LORO_SIMETRICO) == LORO


# @scenarios cuerpo-vacio-no-es-espejo
def test_acertar_a_la_primera_no_es_un_espejo():
    assert figura(SOLO_LA_BANDA) == ABSTRACTO


# @scenarios patron-fallado-no-es-espejo
def test_sin_resolver_no_hay_figura_aunque_haya_simetria():
    assert figura(FALLADA_SIMETRICA) == ABSTRACTO


# @scenarios cuerpo-vacio-no-es-espejo, patron-fallado-no-es-espejo
def test_la_simetria_se_mide_sin_contar_el_suelo():
    """La banda final es simétrica siempre, así que no puede ser lo que concede el espejo.

    **Se comprueba sobre el rasgo, no sobre la categoría.** La primera versión de este test miraba
    `figura()` y era vacua: la banda verde es palíndroma, así que incluirla o no da el mismo veredicto en
    toda cuadrícula que tenga cuerpo. El único caso en que las dos versiones difieren es el 1/6 —cuerpo
    vacío—, y ahí `figura()` ya ha devuelto abstracto por la guarda de altura antes de mirar el espejo. La
    prueba de mutación lo cazó: medir el espejo sobre la cuadrícula entera dejaba la suite en verde.

    El rasgo se especifica aparte de la categoría (delta de `resultados`), así que se verifica aparte. Y no
    es celo: la guarda de altura es lo único que hoy tapa el error, y un reordenamiento de `figura()` o un
    consumidor que lea `espejo` directamente lo destaparía.
    """
    assert rasgos("GGGGG").espejo is False, "un 1/6 no tiene cuerpo, así que no puede ser un espejo"

    cuerpo = "GG.GG/G...G"
    assert rasgos(f"{cuerpo}/GGGGG").espejo is True
    assert figura(f"{cuerpo}/GGGGG") == GEOMETRICO
    assert figura(cuerpo) == ABSTRACTO


# @scenarios una-celda-rota-no-es-espejo
def test_una_fila_truncada_no_es_un_espejo():
    """Una fila corta es palíndroma por accidente, y el espejo no se la puede creer.

    Lo encontró la auditoría adversarial del gate 4d. Las 6202 filas de producción miden cinco columnas, así
    que esto no arregla ningún dato de hoy: fija **hacia dónde falla** el clasificador si algún día un
    patrón llega truncado. Sin la condición, `G/GG.GG` pasaba de abstracto —0 puntos— a geométrico, que son
    3, el máximo del álbum. Un fallo de la ingesta no debe premiar a nadie.
    """
    assert rasgos("G/GG.GG/GGGGG").espejo is False
    assert figura("G/GG.GG/GGGGG") == ABSTRACTO
    assert figura("GGGG/GGGG/GGGGG") == ABSTRACTO


# @scenarios el-espejo-no-le-quita-figura-a-nadie-en-el-orden-historico
def test_ninguna_cuadricula_con_figura_pierde_su_figura():
    """El invariante que hace el cambio seguro: el espejo solo asciende abstractos.

    Se comprueba sobre las fichas etiquetadas a mano, que es el único conjunto de cuadrículas reales que
    vive en el repositorio —los patrones de producción no se copian aquí—. Cualquier ficha que hoy tenga
    figura debe conservarla exactamente.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
    from calibrate_figures import conjunto_dorado

    for ficha in conjunto_dorado():
        if ficha["etiqueta"] in FIGURAS and figura(ficha["patron"]) in FIGURAS:
            assert figura(ficha["patron"]) == ficha["etiqueta"], (
                f"la ficha {ficha['ficha']} cambia de figura: el espejo solo puede ascender abstractos"
            )
