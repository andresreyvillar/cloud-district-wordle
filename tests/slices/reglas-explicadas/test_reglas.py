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


# @scenarios cada-regla-dice-si-se-aplica
def test_el_estado_de_cada_regla_es_uno_de_los_tres_declarados():
    from tools.rules import catalogo

    for regla in catalogo():
        assert regla.estado in ESTADOS, f"{regla.id} tiene estado {regla.estado!r}"


# @scenarios cada-regla-dice-si-se-aplica
def test_el_modelo_de_imputacion_consta_como_acordado_sin_aplicar():
    """No está implementado, y presentarlo como vigente sería mentir sobre cómo se calcula la tabla."""
    from tools.rules import busca

    assert busca("imputacion-por-dificultad").estado == "acordada-sin-aplicar"


# @scenarios las-reglas-sin-decidir-se-declaran
def test_una_regla_sin_decidir_dice_que_falta_decidir():
    from tools.rules import catalogo

    sin_decidir = [r for r in catalogo() if r.estado == "sin-decidir"]

    assert sin_decidir, "el grupo tiene cosas sobre la mesa; no puede salir vacío"
    for regla in sin_decidir:
        assert regla.falta_decidir.strip(), f"{regla.id} no dice qué falta"


# @scenarios cada-regla-dice-si-se-aplica
def test_hay_reglas_aplicadas_que_el_grupo_no_ha_votado_y_se_declara():
    """La información más incómoda de la página, y la más útil.

    Hoy solo una regla está votada —las temporadas mensuales, 6 a 0— y sin embargo se aplican varias más.
    Esconderlo sería el peor uso posible de una página de reglas.
    """
    from tools.rules import busca, catalogo

    assert busca("temporada-mensual").votada is True

    aplicadas_sin_votar = [r for r in catalogo() if r.estado == "aplicada" and not r.votada]
    assert aplicadas_sin_votar, "si esto sale vacío, o se votó todo o el catálogo está maquillado"
    ids = {r.id for r in aplicadas_sin_votar}
    assert "solo-dias-laborables" in ids


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


# @scenarios la-temporada-cerrada-conserva-sus-reglas
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


# @scenarios la-temporada-cerrada-conserva-sus-reglas
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
