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

    # `in` dejó de servir el 2026-08-07: la v2 se publica en /2/ del mismo host, así que la URL de la v1 es
    # **prefijo** de la de la v2 y "no está contenida" es imposible de exigir. Se comprueba el enlace exacto,
    # que es más fuerte: dice que el enlace ES el del objetivo, no solo que lo menciona.
    de_la_v2 = comentario("", OBJETIVOS["v2"])
    de_la_v1 = comentario("", OBJETIVOS["v1"])

    assert f"👉 {OBJETIVOS['v2'].url}" in de_la_v2
    assert f"👉 {OBJETIVOS['v1'].url}" in de_la_v1
    assert OBJETIVOS["v2"].url not in de_la_v1, "capturando la v1 y enlazando a la v2"


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
            subir=lambda ruta, texto, titulo: True,
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

    def subida_que_falla(ruta, texto, titulo):
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

    def subida_ok(ruta, texto, titulo):
        visto["texto"] = texto
        return True

    codigo = asyncio.run(post_ranking.publicar(capturar=captura_ok, subir=subida_ok, resultados=[]))

    assert codigo == 0
    assert visto["objetivo"].url in visto["texto"], "el enlace del texto es el del objetivo capturado"


# @scenarios cada-objetivo-trae-sus-selectores
def test_los_dos_objetivos_comparten_el_subdominio_de_la_cuenta():
    """El subdominio es de la cuenta, no de cada Worker.

    Si algún día se renombra —y el dueño ya ha dicho que le vale—, tiene que cambiar **en los dos a la vez**.
    Con las URL escritas a mano, renombrar dejaba una apuntando a un host que ya no resuelve, y la v2 es
    justo la que nadie mira hasta que falla.
    """
    from tools.post_ranking import SUBDOMINIO, OBJETIVOS

    for nombre, objetivo in OBJETIVOS.items():
        assert f".{SUBDOMINIO}.workers.dev/" in objetivo.url, f"{nombre} no usa el subdominio de la cuenta"


# @scenarios la-captura-de-la-v2-es-el-titular
def test_la_v2_fotografia_el_titular_y_el_podio_no_la_pagina_entera():
    """El texto del mensaje ya lleva el marcador y el álbum: repetirlos en la imagen es decirlo dos veces.

    Y una captura de `.liga` es la página completa —marcador, logros, álbum y estadísticas—: una tira
    larguísima que en Slack se ve como una miniatura ilegible.
    """
    from tools.post_ranking import OBJETIVOS

    assert OBJETIVOS["v2"].captura == ".hero"


# @scenarios la-captura-de-la-v2-es-el-titular
def test_la_v2_espera_a_lo_que_va_a_fotografiar():
    """Esperar a un selector y fotografiar otro deja la puerta abierta a capturar algo a medio pintar."""
    from tools.post_ranking import OBJETIVOS

    assert OBJETIVOS["v2"].espera == OBJETIVOS["v2"].captura


# @scenarios la-captura-fallida-se-declara
def test_si_el_elemento_no_existe_la_captura_falla_diciendo_cual():
    """Sin esto, un selector que no encaja daba un `AttributeError: 'NoneType'` sin decir qué faltaba."""
    import asyncio

    from tools.post_ranking import Objetivo, capture_ranking

    # Se espera a `body`, que SÍ existe, y se fotografía algo que no. Con `espera` apuntando también a lo
    # inexistente, el que fallaba era `wait_for_selector` —cuyo mensaje ya menciona el selector— y la guarda
    # de la captura no se ejercitaba: el mutante que la quitaba sobrevivía y el test parecía cubrirla.
    objetivo = Objetivo(nombre="falso", url="about:blank", espera="body", captura=".no-existe")
    try:
        asyncio.run(capture_ranking(objetivo))
    except Exception as error:  # noqa: BLE001
        assert ".no-existe" in str(error), f"el error no dice qué selector falló: {error}"
    else:
        raise AssertionError("debería haber fallado")


# ── Idempotencia: la jornada no se publica dos veces ────────────────────────────────────────────────────
#
# Existe porque el 26 de agosto de 2026 el grupo recibió el mismo resumen dos veces: el cron de las 17:00 no
# había corrido por una caída de Actions, se lanzó a mano a las 18:47, y el programado llegó a las 19:13 con
# 2h11m de retraso. La protección tiene que vivir en el código, no en el criterio de quien lo lanza.

CAPTURA_FALSA = "/tmp/no-existe-captura.png"


def _mensaje_del_bot(jornada: int) -> dict:
    from post_ranking import titulo_de

    return {"bot_id": "B123", "files": [{"title": titulo_de(jornada)}]}


# @scenarios la-jornada-no-se-publica-dos-veces
def test_la_jornada_ya_publicada_no_se_republica():
    import asyncio

    import post_ranking

    filas = [{"wordle_id": 1694, "player_name": "Ana", "score": 3, "date": "2026-08-27", "pattern": None}]
    capturas, subidas = [], []

    async def captura(objetivo):
        capturas.append(objetivo)
        return CAPTURA_FALSA

    codigo = asyncio.run(
        post_ranking.publicar(
            capturar=captura,
            subir=lambda ruta, texto, titulo: subidas.append(titulo) or True,
            resultados=filas,
            leer_mensajes=lambda: [_mensaje_del_bot(1694)],
        )
    )
    assert codigo == 0, "no republicar no es un fallo"
    assert not subidas, "no debe volver a publicar"
    assert not capturas, "y no debe ni sacar la captura: es el paso caro"


# @scenarios la-jornada-no-se-publica-dos-veces
def test_una_jornada_distinta_si_se_publica():
    """La guarda mira **la jornada**, no si hay algún mensaje del bot: el de ayer no bloquea el de hoy."""
    import asyncio

    import post_ranking

    filas = [{"wordle_id": 1694, "player_name": "Ana", "score": 3, "date": "2026-08-27", "pattern": None}]
    subidas = []

    async def captura(objetivo):
        return CAPTURA_FALSA

    codigo = asyncio.run(
        post_ranking.publicar(
            capturar=captura,
            subir=lambda ruta, texto, titulo: subidas.append(titulo) or True,
            resultados=filas,
            leer_mensajes=lambda: [_mensaje_del_bot(1693)],
        )
    )
    assert codigo == 0
    assert len(subidas) == 1, "la jornada de hoy sí se publica"
    assert "1694" in subidas[0], f"y su captura lleva la marca de la jornada: {subidas[0]}"


# @scenarios la-jornada-no-se-publica-dos-veces
def test_un_mensaje_de_persona_no_bloquea_la_publicacion():
    """Alguien puede pegar en el canal un fichero con ese título; solo cuenta lo que subió el bot."""
    from post_ranking import titulo_de, ya_publicada

    de_persona = {"files": [{"title": titulo_de(1694)}]}
    assert not ya_publicada([de_persona], 1694)
    assert ya_publicada([_mensaje_del_bot(1694)], 1694)


# @scenarios si-el-canal-no-se-puede-leer-se-publica
def test_sin_poder_leer_el_canal_se_publica():
    import asyncio

    import post_ranking

    filas = [{"wordle_id": 1694, "player_name": "Ana", "score": 3, "date": "2026-08-27", "pattern": None}]
    subidas = []

    async def captura(objetivo):
        return CAPTURA_FALSA

    codigo = asyncio.run(
        post_ranking.publicar(
            capturar=captura,
            subir=lambda ruta, texto, titulo: subidas.append(titulo) or True,
            resultados=filas,
            leer_mensajes=lambda: [],  # lo que devuelve `mensajes_recientes` cuando Slack falla
        )
    )
    assert codigo == 0 and len(subidas) == 1, "un canal ilegible no puede dejar al grupo sin mensaje"


# @scenarios si-el-canal-no-se-puede-leer-se-publica
def test_el_lector_del_canal_se_repliega_a_vacio():
    """**El repliegue del lector real, no del doble.** El test de arriba sustituye `leer_mensajes` entero, así
    que este camino no se ejercitaba: lo destapó la prueba de mutación al no ponerse en rojo.
    """
    from slack_sdk.errors import SlackApiError

    from post_ranking import mensajes_recientes

    class CanalCaido:
        def conversations_history(self, **_):
            raise SlackApiError("boom", {"error": "channel_not_found"})

    assert mensajes_recientes(cliente=CanalCaido()) == [], "un fallo de lectura no bloquea la publicación"

    class CanalOk:
        def conversations_history(self, **_):
            return {"messages": [{"bot_id": "B1", "files": []}]}

    assert len(mensajes_recientes(cliente=CanalOk())) == 1
