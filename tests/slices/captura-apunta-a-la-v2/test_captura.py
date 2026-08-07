"""Escenarios de `captura-apunta-a-la-v2` (Fase 2 — TDD rojo).

**Nada de esto publica.** El cliente de Slack y el navegador son dobles; el módulo se importa, pero su
`main()` nunca se ejecuta de verdad contra el canal. El bot tiene `files:write`: un descuido aquí escribe
delante de todo el grupo.
"""

from __future__ import annotations

import pytest


# @scenarios el-objetivo-de-la-captura-es-configurable
def test_el_objetivo_sale_del_entorno_y_no_de_una_constante(monkeypatch):
    from tools.post_ranking import objetivo_de_captura

    monkeypatch.setenv("CAPTURA_OBJETIVO", "v2")
    assert objetivo_de_captura().nombre == "v2"

    monkeypatch.setenv("CAPTURA_OBJETIVO", "v1")
    assert objetivo_de_captura().nombre == "v1"


# @scenarios el-objetivo-por-defecto-es-el-que-esta-publicado
def test_sin_configuracion_se_usa_la_v1_que_es_lo_desplegado(monkeypatch):
    from tools.post_ranking import objetivo_de_captura

    monkeypatch.delenv("CAPTURA_OBJETIVO", raising=False)
    objetivo = objetivo_de_captura()

    assert objetivo.nombre == "v1"
    assert "cloud-district-wordle" in objetivo.url


# @scenarios cada-objetivo-trae-sus-selectores
def test_cada_objetivo_trae_su_url_y_sus_dos_selectores():
    """Cambiar solo la URL dejaba el workflow esperando un `.summary-cards` que la v2 no tiene."""
    from tools.post_ranking import OBJETIVOS

    assert set(OBJETIVOS) == {"v1", "v2"}
    for nombre, objetivo in OBJETIVOS.items():
        assert objetivo.url.startswith("https://"), nombre
        assert objetivo.espera and objetivo.captura, f"{nombre} sin selectores"

    # y son distintos: es justo el motivo de que la URL no viaje sola
    assert OBJETIVOS["v1"].espera != OBJETIVOS["v2"].espera
    assert OBJETIVOS["v1"].url != OBJETIVOS["v2"].url


# @scenarios el-enlace-del-mensaje-apunta-a-donde-la-captura
def test_el_enlace_del_mensaje_es_el_del_objetivo_capturado():
    from tools.post_ranking import OBJETIVOS, comentario

    texto = comentario("", OBJETIVOS["v2"])

    assert OBJETIVOS["v2"].url in texto
    assert OBJETIVOS["v1"].url not in texto, "una foto de una web y un enlace a otra"


# @scenarios el-enlace-del-mensaje-apunta-a-donde-la-captura
def test_el_comentario_sigue_llevando_las_medallas():
    from tools.post_ranking import OBJETIVOS, comentario

    texto = comentario("🏅 Fondista: Ana", OBJETIVOS["v1"])

    assert "🏅 Fondista: Ana" in texto
    assert "ranking actualizado" in texto


# @scenarios un-objetivo-desconocido-falla-en-lugar-de-usar-el-viejo
def test_un_objetivo_desconocido_revienta(monkeypatch):
    """Caer en el objetivo por defecto dejaría una errata publicando la web vieja indefinidamente."""
    from tools.post_ranking import objetivo_de_captura

    monkeypatch.setenv("CAPTURA_OBJETIVO", "v3")

    with pytest.raises(SystemExit):
        objetivo_de_captura()


# @scenarios una-publicacion-fallida-no-termina-en-exito
def test_una_captura_fallida_termina_con_error():
    """Hoy imprime el fallo y termina bien: el grupo deja de recibir el resumen y Actions está verde."""
    import asyncio

    from tools import post_ranking

    async def captura_que_falla(objetivo):
        raise TimeoutError("no aparece el selector")

    codigo = asyncio.run(
        post_ranking.publicar(
            capturar=captura_que_falla,
            subir=lambda ruta, texto: True,
            resultados=[],
        )
    )

    assert codigo != 0, "un fallo tiene que salir en rojo en el workflow"


# @scenarios una-publicacion-fallida-no-termina-en-exito
def test_una_subida_fallida_termina_con_error():
    import asyncio

    from tools import post_ranking

    async def captura_ok(objetivo):
        return "captura.png"

    def subida_que_falla(ruta, texto):
        return False

    codigo = asyncio.run(
        post_ranking.publicar(capturar=captura_ok, subir=subida_que_falla, resultados=[])
    )

    assert codigo != 0


# @scenarios una-publicacion-fallida-no-termina-en-exito
def test_una_publicacion_correcta_termina_bien():
    import asyncio

    from tools import post_ranking

    visto = {}

    async def captura_ok(objetivo):
        visto["objetivo"] = objetivo
        return "captura.png"

    def subida_ok(ruta, texto):
        visto["texto"] = texto
        return True

    codigo = asyncio.run(post_ranking.publicar(capturar=captura_ok, subir=subida_ok, resultados=[]))

    assert codigo == 0
    assert visto["objetivo"].url in visto["texto"], "el enlace del texto es el del objetivo capturado"
