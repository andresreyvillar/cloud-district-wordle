"""Escenarios de `reglas-explicadas` (Fase 2 — TDD rojo).

El test que sostiene todo el slice es `test_cada_parametro_publicado_es_el_que_usa_el_calculo`: sin él, la
página de reglas miente en cuanto alguien recalibre un umbral, y una explicación falsa en la que el grupo
confía es peor que no tener página.
"""

from __future__ import annotations

import pytest

MOTIVO = "TDD rojo — tools/rules.py no existe todavía"

ESTADOS = {"aplicada", "acordada-sin-aplicar", "sin-decidir"}


# @scenarios las-reglas-se-agrupan-por-eje
def test_las_reglas_llegan_agrupadas_por_eje():
    from tools.rules import EJES, catalogo, por_eje

    agrupadas = por_eje(catalogo())

    assert set(agrupadas) <= set(EJES), "un eje que no está declarado"
    assert len(agrupadas) >= 3, "al menos temporada, medallas y figuras"
    for eje, reglas in agrupadas.items():
        assert reglas, f"el eje {eje} no puede estar vacío"


# @scenarios una-regla-explica-por-que-existe
def test_toda_regla_dice_que_hace_y_por_que_existe():
    """Una regla sin motivo se lee como arbitrariedad, así que el motivo es parte del requisito."""
    from tools.rules import catalogo

    for regla in catalogo():
        assert regla.titulo.strip(), regla.id
        assert regla.que_hace.strip(), f"{regla.id} no dice qué hace"
        assert regla.por_que.strip(), f"{regla.id} no dice por qué existe"


# @scenarios las-propuestas-siguen-en-el-catalogo
def test_el_estado_de_cada_regla_es_uno_de_los_tres_declarados():
    from tools.rules import catalogo

    for regla in catalogo():
        assert regla.estado in ESTADOS, f"{regla.id} tiene estado {regla.estado!r}"


# @scenarios los-parametros-son-los-que-el-calculo-usa
def test_el_modelo_de_imputacion_consta_como_aplicado_y_lo_esta_de_verdad():
    """El estado de una regla no se cree: se comprueba contra el cálculo.

    Este test decía lo contrario —que la imputación estaba acordada sin aplicar— y era cierto cuando se
    escribió. Se implementó el 2026-08-05 y el catálogo se quedó atrás durante dos días diciendo que la
    tabla no imputaba mientras imputaba. Por eso ahora no basta con afirmar el estado: hay que demostrarlo.
    """
    from tools.rules import busca
    from tools.standings import MARGEN, clasificacion, imputar

    assert busca("imputacion-por-dificultad").estado == "aplicada"

    # Y el cálculo la usa de verdad: faltar un día deja una jornada imputada en la tabla.
    #
    # SEIS jugadores, no cinco: al quitar a uno, el día tiene que seguir llegando a la muestra mínima. Con
    # cinco, quitar a uno dejaba la jornada en cuatro, el día salía de la temporada y no se imputaba nada
    # — el test habría fallado por el motivo equivocado.
    dias = ["2026-09-01", "2026-09-02"]  # martes y miércoles: los dos laborables
    filas = [
        {"slack_user_id": f"U{n}", "player_name": n, "wordle_id": 1700 + i, "score": 4, "date": dias[i]}
        for i in range(2)
        for n in ("a", "b", "c", "d", "e", "f")
    ]
    filas = [f for f in filas if not (f["player_name"] == "f" and f["wordle_id"] == 1701)]

    tabla = {f["nombre"]: f for f in clasificacion(filas, "2026-09")}
    ausente = tabla["f"]
    assert ausente["dias"] == 2 and ausente["jugados"] == 1, "el fixture no produce una ausencia"

    assert any(dia["imputado"] for dia in ausente["por_dia"]), "la tabla dice que imputa y no imputa"
    assert imputar(4.0, 4.0) == 4.0 + MARGEN


# @scenarios las-propuestas-siguen-en-el-catalogo
def test_una_regla_sin_decidir_dice_que_falta_decidir():
    from tools.rules import catalogo

    sin_decidir = [r for r in catalogo() if r.estado == "sin-decidir"]

    assert sin_decidir, "el grupo tiene cosas sobre la mesa; no puede salir vacío"
    for regla in sin_decidir:
        assert regla.falta_decidir.strip(), f"{regla.id} no dice qué falta"


# @scenarios las-propuestas-siguen-en-el-catalogo
def test_hay_reglas_aplicadas_que_el_grupo_no_ha_votado_y_se_declara():
    """La información más incómoda de la página, y la más útil.

    El grupo ratificó las trece reglas del reglamento el 2026-08-07. Las **dos del modelo de participación**
    siguen sin votar y el cálculo ya las usa: son justo las que cambian quién gana el mes.

    Y desde el 2026-08-12 son cinco: **las tres del álbum tampoco están votadas**. El álbum se construyó y la
    escala de figuras la decidió el dueño; el grupo nunca las ratificó. Son menos graves que las de
    participación porque el álbum no toca el marcador, pero la página no las va a esconder.

    **Este test es un cable trampa a propósito.** Si el grupo vota esas dos, se pone rojo y alguien tiene
    que venir a actualizarlo, que es exactamente lo que debe pasar cuando cambia lo que la página afirma.
    """
    from tools.rules import busca, catalogo

    for votada in ("temporada-mensual", "solo-dias-laborables", "temporada-cero", "fallo-cuenta-como-siete"):
        assert busca(votada).votada is True, f"{votada} consta como no votada"

    aplicadas_sin_votar = {r.id for r in catalogo() if r.estado == "aplicada" and not r.votada}

    assert aplicadas_sin_votar == {
        "imputacion-por-dificultad",
        "sin-minimo-para-clasificar",
        "album-de-figuras",
        "figuras-ponderadas",
        "figuras-no-puntuan",
        # Las del SuperWordleBros, desde el 2026-10-02: las decidió el dueño mientras se construía el juego, y
        # el grupo no las ha votado.
        "juego-puntos-por-puesto",
        "juego-estrellas-antes-que-tiempo",
        "juego-nivel-diario",
        "juego-nivel-cerrado",
        "juego-ultimo-dia-mes-siguiente",
    }, (
        f"lo aplicado sin votar ha cambiado: {aplicadas_sin_votar}. Si el grupo las ha votado, actualiza "
        "el catálogo y este test; si no, es que alguien ha marcado como votada una regla que no lo está."
    )


# @scenarios los-parametros-son-los-que-el-calculo-usa
def test_cada_parametro_publicado_es_el_que_usa_el_calculo():
    """EL test del slice: lo publicado tiene que ser lo aplicado.

    Cada parámetro declara de qué constante sale (`fuente`) y su valor se lee de ahí en tiempo de ejecución.
    Este test comprueba que no hay ningún literal escrito a mano que pueda desincronizarse.
    """
    import importlib

    from tools.rules import catalogo

    for regla in catalogo():
        for parametro in regla.parametros:
            modulo, nombre = parametro.fuente.rsplit(".", 1)
            real = getattr(importlib.import_module(modulo), nombre)
            assert parametro.valor == real, (
                f"{regla.id}/{parametro.nombre}: la página publicaría {parametro.valor!r} "
                f"y el cálculo usa {real!r} ({parametro.fuente})"
            )


# @scenarios los-parametros-son-los-que-el-calculo-usa
def test_las_reglas_con_umbral_declaran_al_menos_un_parametro():
    """Una regla que menciona un número en su texto y no declara parámetro es un literal escondido."""
    from tools.rules import busca

    for identificador in ("dia-con-muestra-minima", "fondista", "imputacion-por-dificultad"):
        assert busca(identificador).parametros, f"{identificador} no declara parámetros"


# @scenarios los-parametros-son-los-que-el-calculo-usa
def test_la_instantanea_de_una_temporada_lleva_sus_reglas():
    from tools.seasons import instantanea

    filas = [
        {
            "player_name": f"j{i}",
            "slack_user_id": f"U_J{i}",
            "wordle_id": 1700,
            "score": 4,
            "date": "2026-08-03",
        }
        for i in range(6)
    ]
    carga = instantanea(filas, "2026-08")

    assert carga["reglas"], "la instantánea tiene que llevar las reglas con las que se calculó"
    ids = {r["id"] for r in carga["reglas"]}
    assert {"temporada-mensual", "solo-dias-laborables", "dia-con-muestra-minima"} <= ids


# @scenarios los-parametros-son-los-que-el-calculo-usa
def test_las_reglas_de_la_instantanea_son_serializables():
    """Van a JSONB, así que no puede haber dataclasses ni tuplas dentro."""
    import json

    from tools.seasons import instantanea

    filas = [
        {
            "player_name": f"j{i}",
            "slack_user_id": f"U_J{i}",
            "wordle_id": 1700,
            "score": 4,
            "date": "2026-08-03",
        }
        for i in range(6)
    ]
    json.dumps(instantanea(filas, "2026-08"))


# @scenarios sin-instantanea-la-pagina-lo-dice
def test_el_catalogo_es_util_sin_instantanea():
    """La página tiene un plan B: si no hay instantánea, las reglas se pueden leer del catálogo."""
    from tools.rules import catalogo, como_json

    datos = como_json(catalogo())

    assert isinstance(datos, list) and datos
    assert all({"id", "eje", "titulo", "que_hace", "por_que", "estado"} <= set(r) for r in datos)


# @scenarios una-regla-explica-por-que-existe
def test_la_prosa_del_catalogo_no_lleva_markdown():
    """La vista escapa el texto, no lo renderiza: un `**` sale como asterisco en la cara del lector.

    Lo cazó mirar la página, no un test — y por eso ahora hay test.
    """
    from tools.rules import catalogo

    for regla in catalogo():
        for campo in ("titulo", "que_hace", "por_que", "falta_decidir"):
            texto = getattr(regla, campo)
            assert "**" not in texto, f"{regla.id}/{campo} lleva markdown"
            assert "`" not in texto, f"{regla.id}/{campo} lleva markdown"


# @scenarios el-superwordlebros-tiene-sus-reglas
def test_el_juego_tiene_sus_cinco_reglas_aplicadas_con_parametros():
    from rules import APLICADA, catalogo

    del_juego = [r for r in catalogo() if r.eje == "juego"]

    assert {r.id for r in del_juego} == {
        "juego-puntos-por-puesto", "juego-estrellas-antes-que-tiempo", "juego-nivel-diario",
        "juego-nivel-cerrado", "juego-ultimo-dia-mes-siguiente",
    }
    assert all(r.estado == APLICADA for r in del_juego)
    fuentes = {p.fuente for r in del_juego for p in r.parametros}
    assert {"juego.ESCALA", "juego.PUNTOS_DESDE_EL_OCTAVO", "juego.HORA_DE_CONGELAR",
            "seasons.MUESTRA_MINIMA_DEL_DIA"} <= fuentes


# @scenarios el-superwordlebros-tiene-sus-reglas
def test_la_hora_de_congelar_es_la_misma_que_usa_el_cron():
    import re
    from pathlib import Path

    from juego import HORA_DE_CONGELAR

    js = (Path(__file__).resolve().parents[3] / "v2/js/domain/superbros.js").read_text(encoding="utf-8")
    [del_cron] = re.findall(r"export const HORA_DE_CONGELAR = '([0-9:]+)'", js)

    assert HORA_DE_CONGELAR == del_cron


# @scenarios solo-se-ensenan-las-reglas-vigentes
def test_solo_las_de_la_temporada_cero_son_historicas():
    from rules import catalogo

    historicas = {r.id for r in catalogo() if r.historica}

    assert historicas == {"temporada-cero", "minimo-en-la-temporada-cero"}
    assert all("historica" in r for r in __import__("rules").como_json(catalogo()))
