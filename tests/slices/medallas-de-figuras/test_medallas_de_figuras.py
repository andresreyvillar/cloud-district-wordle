"""Escenarios de `medallas-de-figuras` (Fase 2 — TDD rojo).

Los patrones de los fixtures son los mismos que verifica `tests/slices/clasificacion-de-figuras`, y aquí se
vuelven a comprobar contra el clasificador antes de usarlos: un fixture que creyera dibujar un loro y
dibujara un abstracto haría que estos tests midieran otra cosa.

Las fechas caen en la **temporada 0** salvo donde el escenario necesita otra cosa, porque allí no hay filtro
de muestra mínima y el fixture prueba las medallas, no el modelo de temporada.
"""

from __future__ import annotations

import pytest

LORO = ".G.../.G..G/.GY../GGGGG"
GEOMETRICO = "..G../..G../GGGGG"
FLOR = "Y...Y/..Y../GGGGG"
ABSTRACTO = "GG.GG/GGYGG/GG.GG/GGGGG"

#: Un lunes anterior al inicio de las temporadas numeradas: temporada 0.
HISTORICO = "2026-03-02"


def partidas(nombre: str, patrones: list[str | None], fecha: str = HISTORICO) -> list[dict]:
    return [
        {
            "slack_user_id": f"U_{nombre}",
            "player_name": nombre,
            "wordle_id": 1500 + indice,
            "score": 4,
            "date": fecha,
            "pattern": patron,
        }
        for indice, patron in enumerate(patrones)
    ]


def test_los_fixtures_dibujan_lo_que_dicen_dibujar():
    from figures import figura

    assert (figura(LORO), figura(GEOMETRICO), figura(FLOR), figura(ABSTRACTO)) == (
        "loro",
        "geometrico",
        "flores",
        "abstracto",
    )


# @scenarios cinco-medallas-de-figura
def test_las_cinco_medallas_estan_en_el_catalogo_con_su_nivel():
    from badges import CATALOGO, POR_CLAVE

    claves = {m.clave for m in CATALOGO}
    assert {"ornitologo", "arquitecto", "florista", "abstracto", "coleccionista"} <= claves
    assert len(CATALOGO) == 12, "siete de antes más cinco de figuras"

    # El nivel no es decorativo: ordena la presentación y dice cuánto cuesta conseguirla.
    assert POR_CLAVE["ornitologo"].nivel == "legendario"
    assert POR_CLAVE["arquitecto"].nivel == "legendario"
    assert POR_CLAVE["florista"].nivel == "raro"
    assert POR_CLAVE["abstracto"].nivel == "comun"
    assert POR_CLAVE["coleccionista"].nivel == "comun"
    # Todas son de temporada: se pueden ganar cada mes, como las de constancia.
    assert all(POR_CLAVE[c].alcance == "temporada" for c in ("ornitologo", "florista", "abstracto"))


# @scenarios cinco-medallas-de-figura
def test_alcanzar_el_umbral_de_una_categoria_da_su_medalla():
    from badges import MINIMO_ORNITOLOGO, medallas_de_temporada

    filas = partidas("Ana", [LORO] * MINIMO_ORNITOLOGO)

    assert "ornitologo" in medallas_de_temporada(filas, "0")["Ana"]


# @scenarios el-umbral-sale-de-lo-que-alguien-ha-logrado
def test_quedarse_a_una_partida_del_umbral_no_da_la_medalla():
    from badges import MINIMO_ORNITOLOGO, medallas_de_temporada

    filas = partidas("Ana", [LORO] * (MINIMO_ORNITOLOGO - 1))

    assert "ornitologo" not in medallas_de_temporada(filas, "0").get("Ana", [])


# @scenarios el-umbral-sale-de-lo-que-alguien-ha-logrado
def test_los_umbrales_son_los_remedidos_con_el_clasificador_calibrado():
    """Los del brief se midieron con el clasificador desmentido y el propio brief pedía rehacerlos.

    Van literales: derivarlos de otra cosa haría que el test se ajustara solo y dejara de decir cuáles son.
    Su rareza medida sobre 122 pares jugador-mes está en la spec.
    """
    from badges import MINIMO_ABSTRACTO, MINIMO_ARQUITECTO, MINIMO_FLORISTA, MINIMO_ORNITOLOGO

    assert (MINIMO_ORNITOLOGO, MINIMO_ARQUITECTO, MINIMO_FLORISTA, MINIMO_ABSTRACTO) == (5, 4, 11, 7)


# @scenarios cinco-medallas-de-figura
def test_coleccionista_exige_las_cuatro_categorias():
    from badges import medallas_de_temporada

    tres = partidas("Tres", [LORO] * 6 + [FLOR] * 6 + [GEOMETRICO] * 6)
    cuatro = partidas("Cuatro", [LORO, FLOR, GEOMETRICO, ABSTRACTO])

    palmares = medallas_de_temporada(tres + cuatro, "0")

    assert "coleccionista" not in palmares.get("Tres", []), "muchas partidas no sustituyen a la variedad"
    assert "coleccionista" in palmares["Cuatro"], "una de cada basta"


# @scenarios el-recuento-es-el-del-album
def test_la_medalla_usa_el_mismo_recuento_que_la_tira_del_album():
    """Si la tira dice 🦜5 y la medalla no salta, el logro parece roto. Se comprueba que es el mismo número."""
    from album import album
    from badges import MINIMO_ORNITOLOGO, medallas_de_temporada

    filas = partidas("Ana", [LORO] * MINIMO_ORNITOLOGO + [ABSTRACTO] * 3)

    tira = next(f for f in album(filas, "0")["jugadores"] if f["nombre"] == "Ana")
    assert tira["recuento"]["loro"] == MINIMO_ORNITOLOGO
    assert "ornitologo" in medallas_de_temporada(filas, "0")["Ana"]


# @scenarios sin-patron-no-da-medalla
def test_sin_cuadricula_no_hay_medalla_de_figura_y_los_demas_conservan_las_suyas():
    from badges import MINIMO_ORNITOLOGO, medallas_de_temporada

    sin_dibujo = partidas("Sin", [None] * 20)
    con_dibujo = partidas("Con", [LORO] * MINIMO_ORNITOLOGO)

    palmares = medallas_de_temporada(sin_dibujo + con_dibujo, "0")

    assert not [c for c in palmares.get("Sin", []) if c in ("ornitologo", "abstracto", "coleccionista")]
    assert "ornitologo" in palmares["Con"]


# @scenarios las-figuras-en-el-resumen-diario
def test_una_medalla_de_figura_ganada_hoy_se_anuncia_en_el_resumen():
    from badges import MINIMO_ORNITOLOGO, texto_de_medallas

    # Las cuatro primeras ya estaban; la quinta llega hoy y es la que dispara la medalla.
    filas = partidas("Ana", [LORO] * MINIMO_ORNITOLOGO)
    hoy = max(fila["wordle_id"] for fila in filas)

    texto = texto_de_medallas(filas, "0", hoy)

    assert "Ornitólog@" in texto
    assert "Ana" in texto


# @scenarios la-temporada-del-resumen-sale-del-modelo
def test_el_resumen_deriva_la_temporada_del_modelo_y_no_del_prefijo_de_la_fecha():
    """Recortar la fecha daba `2026-03` para una jornada que pertenece a la temporada 0.

    Es la tercera aparición de la misma causa raíz: `badges._de_la_temporada` y `v2/js/data/temporada.js`
    ya la tuvieron. Con el prefijo, las medallas del día se calculaban sobre una temporada que no existe.
    """
    from post_ranking import temporada_del_resumen

    filas = partidas("Ana", [LORO] * 5)

    assert temporada_del_resumen(filas) == "0"


# @scenarios la-temporada-del-resumen-sale-del-modelo
def test_el_resumen_pide_la_columna_del_patron():
    """Sin ella, ninguna medalla de figura podría anunciarse jamás: el dato no llegaría."""
    from post_ranking import COLUMNAS

    assert "pattern" in COLUMNAS
