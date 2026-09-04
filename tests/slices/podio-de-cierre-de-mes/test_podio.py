"""El podio del mes que cierra. Fixtures locales; ni red ni producción."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from podio import campeones, medallas_del_campeon, podio_de, temporada_que_cierra, texto

#: Laborables reales, que es lo que el filtro de temporada exige.
AGOSTO = ["2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06", "2026-08-07"]
SEPTIEMBRE = ["2026-09-01", "2026-09-02"]

#: Una temporada numerada solo cuenta los días con al menos cinco jugadores.
RELLENO = {"Dani": 5, "Eva": 5, "Fran": 5}


def _fila(jornada, nombre, score, dia):
    return {
        "wordle_id": jornada,
        "player_name": nombre,
        "slack_user_id": nombre,
        "score": score,
        "date": dia,
        "pattern": None,
    }


def _mes(dias, notas_por_jornada, desde=1):
    return [
        _fila(desde + i, quien, score, dias[i])
        for i, notas in enumerate(notas_por_jornada)
        for quien, score in {**notas, **RELLENO}.items()
    ]


#: Ana gana agosto, Bea segunda, Cris tercera.
AGOSTO_JUGADO = _mes(AGOSTO, [{"Ana": 2, "Bea": 3, "Cris": 4}] * 5)
#: Un solo día de septiembre: basta para saber que agosto cerró.
SEPTIEMBRE_JUGADO = _mes(SEPTIEMBRE, [{"Ana": 4, "Bea": 4, "Cris": 4}], desde=6)


# @scenarios el-mes-que-cierra-sale-de-los-datos
def test_el_mes_que_cierra_es_el_anterior_al_del_ultimo_resultado():
    assert temporada_que_cierra(AGOSTO_JUGADO + SEPTIEMBRE_JUGADO) == "2026-08"


# @scenarios sin-mes-nuevo-no-se-celebra-nada
def test_sin_resultados_del_mes_nuevo_no_se_celebra():
    """A primera hora del día 1 puede no haber jugado nadie: celebrar «el anterior» felicitaría otra vez a
    quien ganó un mes ya celebrado.
    """
    assert temporada_que_cierra(AGOSTO_JUGADO) is None
    assert temporada_que_cierra([]) is None


# @scenarios la-temporada-cero-no-se-celebra
def test_la_temporada_cero_no_se_celebra():
    """No cerró un mes: es el bloque anterior a que existieran las temporadas."""
    historico = _mes(["2026-07-06", "2026-07-07", "2026-07-08", "2026-07-09", "2026-07-10"],
                     [{"Ana": 3, "Bea": 3, "Cris": 3}] * 5, desde=100)
    from seasons import temporada_de

    assert temporada_de(historico[0]["date"]) == "0", "julio cae en la temporada 0"
    assert temporada_que_cierra(historico + AGOSTO_JUGADO) is None


# @scenarios el-mes-que-cierra-sale-de-los-datos
def test_un_salto_de_meses_no_celebra_un_cierre_viejo():
    """El mes en curso ha de ser **consecutivo** al cerrado."""
    octubre = _mes(["2026-10-01", "2026-10-02"], [{"Ana": 4, "Bea": 4, "Cris": 4}], desde=200)
    assert temporada_que_cierra(AGOSTO_JUGADO + octubre) is None


# @scenarios el-podio-lleva-los-empates-enteros
def test_el_podio_lleva_los_empates_enteros():
    """Cortar por número de filas partiría un empate por la mitad."""
    from podio import DEL_PODIO
    from standings import clasificacion

    empatados = _mes(AGOSTO, [{"Ana": 2, "Bea": 3, "Cris": 3, "Gus": 3}] * 5)
    tabla = podio_de(empatados, "2026-08")

    # **Todos los que tienen puesto de podio están.** «Al menos dos empatados» no valía: con tres empatados
    # en el segundo, cortar por filas deja justo dos y la aserción pasaba. Lo cazó la prueba de mutación.
    esperados = {
        fila["nombre"] for fila in clasificacion(empatados, "2026-08")
        if fila["clasificado"] and fila["posicion"] and fila["posicion"] <= DEL_PODIO
    }
    assert {fila["nombre"] for fila in tabla} == esperados, f"faltan o sobran: {esperados}"
    assert len(tabla) > DEL_PODIO, "el fixture debe tener más de tres en puesto de podio"


# @scenarios se-felicita-al-campeon-con-sus-medallas
def test_se_felicita_al_campeon_y_se_enseñan_sus_medallas():
    filas = AGOSTO_JUGADO + SEPTIEMBRE_JUGADO
    mensaje = texto(filas, "2026-08", 6)
    assert "Ana" in mensaje
    assert "🥇" in mensaje and "🥈" in mensaje
    insignias = medallas_del_campeon(filas, "2026-08", "Ana")
    assert insignias, "Ana gana algo en el mes"
    from badges import POR_CLAVE

    assert POR_CLAVE[insignias[0]].emoji in mensaje


# @scenarios con-empate-en-el-primer-puesto-se-felicita-a-todos
def test_con_empate_arriba_se_felicita_a_todos():
    empatados = _mes(AGOSTO, [{"Ana": 2, "Bea": 2, "Cris": 5}] * 5)
    tabla = podio_de(empatados, "2026-08")
    quienes = campeones(tabla)
    assert set(quienes) == {"Ana", "Bea"}, quienes
    mensaje = texto(empatados + SEPTIEMBRE_JUGADO, "2026-08", 6)
    assert "Ana" in mensaje and "Bea" in mensaje
    assert "Se lleva además" not in mensaje, "con empate no se atribuyen medallas a uno solo"


# @scenarios se-felicita-al-campeon-con-sus-medallas
def test_el_nombre_no_pierde_su_punto():
    """**El fallo que salió al probarlo.** Pasar `replace(".", ",")` a la línea entera convertía «Andrés R.»
    en «Andrés R,»: varios nombres del grupo acaban en punto, y la coma decimal solo va en el número.
    """
    con_punto = _mes(AGOSTO, [{"Andrés R.": 2, "Bea": 3, "Cris": 4}] * 5)
    mensaje = texto(con_punto + SEPTIEMBRE_JUGADO, "2026-08", 6)
    assert "Andrés R." in mensaje, mensaje
    assert "Andrés R," not in mensaje, mensaje
    assert "2,00" in mensaje, "y la media sí lleva coma"


# @scenarios el-cierre-no-se-publica-dos-veces
def test_el_cierre_no_se_publica_dos_veces():
    import post_podium

    marca = {"bot_id": "B1", "files": [{"title": "Podio del mes :trophy: · 2026-08"}]}
    assert post_podium.ya_celebrado([marca], "2026-08"), "con el emoji convertido tiene que detectarlo"
    assert not post_podium.ya_celebrado([marca], "2026-09")
    assert not post_podium.ya_celebrado([{"files": [{"title": "Podio del mes 🏆 · 2026-08"}]}], "2026-08"), (
        "un mensaje de una persona no cuenta")


# @scenarios el-cierre-no-se-publica-dos-veces, sin-mes-nuevo-no-se-celebra-nada
def test_el_flujo_no_publica_cuando_no_toca():
    import post_podium

    subidas = []

    async def captura(objetivo):
        subidas.append(("captura", objetivo.nombre))
        return "/tmp/no-existe.png"

    def subida(ruta, texto_, titulo, canal=None):
        subidas.append(("subida", titulo))
        return True

    # Sin mes nuevo: no se celebra y **no se saca la captura**, que es el paso caro.
    codigo = asyncio.run(post_podium.celebrar(
        capturar=captura, subir=subida, resultados=AGOSTO_JUGADO, leer_mensajes=lambda **_: []))
    assert codigo == 0 and not subidas

    # Ya celebrado: tampoco.
    marca = {"bot_id": "B1", "files": [{"title": "Podio del mes :trophy: · 2026-08"}]}
    codigo = asyncio.run(post_podium.celebrar(
        capturar=captura, subir=subida, resultados=AGOSTO_JUGADO + SEPTIEMBRE_JUGADO,
        leer_mensajes=lambda **_: [marca]))
    assert codigo == 0 and not subidas


# @scenarios la-imagen-es-la-de-la-web
def test_la_imagen_es_la_del_podio_de_esa_temporada():
    import post_podium

    capturado = []

    async def captura(objetivo):
        capturado.append(objetivo)
        return "/tmp/no-existe.png"

    codigo = asyncio.run(post_podium.celebrar(
        capturar=captura, subir=lambda r, t, ti, canal=None: True,
        resultados=AGOSTO_JUGADO + SEPTIEMBRE_JUGADO, leer_mensajes=lambda **_: []))
    assert codigo == 0
    assert len(capturado) == 1
    objetivo = capturado[0]
    assert objetivo.url.endswith("/t/2026-08"), objetivo.url
    assert objetivo.espera == ".podio-card" and objetivo.captura == ".podio"


# @scenarios el-mensaje-abre-presentando-el-juego-y-el-mes
def test_el_mensaje_abre_presentando_el_juego_y_el_mes():
    """El cierre sale una vez al mes y no tiene el contexto del mensaje diario: quien lo lee puede llevar
    semanas sin mirar la tabla, así que la primera línea dice qué es y de qué mes. Decisión del dueño.
    """
    from podio import mes_y_año

    mensaje = texto(AGOSTO_JUGADO + SEPTIEMBRE_JUGADO, "2026-08", 6)
    primera = mensaje.splitlines()[0]
    assert primera.startswith("Ya tenemos los resultados de *Cloud District Wordle*"), primera
    assert mes_y_año("2026-08") == "agosto de 2026"
    assert "agosto de 2026" in primera, primera
    # Y el mes no se repite en el encabezado del podio, que iba justo debajo.
    assert mensaje.count("agosto de 2026") == 1, mensaje


# @scenarios la-comprobacion-alcanza-los-dias-que-el-cron-corre
def test_la_comprobacion_alcanza_mas_alla_de_una_pagina():
    """**El fallo real: el podio de agosto se publicó dos veces.**

    El original quedó en la posición 44 del historial y la guarda leía 30 mensajes, así que no lo encontró y
    republicó tres días después. El cron corre del 1 al 7 y el canal mueve hasta 17 mensajes al día: la
    comprobación tiene que alcanzar unos 120, no 30.
    """
    import post_podium

    marca = {"bot_id": "B1", "files": [{"title": "Podio del mes :trophy: · 2026-08"}]}
    relleno = [{"user": "U1", "text": "La palabra del día #1700 4/6"} for _ in range(43)]

    paginas_pedidas = []

    def historial(**kwargs):
        paginas_pedidas.append(kwargs.get("paginas", 1))
        # Solo devuelve la marca si se piden páginas suficientes para llegar a la posición 44.
        cuantos = 30 * kwargs.get("paginas", 1)
        return (relleno + [marca])[:cuantos]

    subidas = []

    async def captura(objetivo):
        return "/tmp/no-existe.png"

    codigo = asyncio.run(
        post_podium.celebrar(
            capturar=captura,
            subir=lambda r, t, ti, canal=None: subidas.append(ti) or True,
            resultados=AGOSTO_JUGADO + SEPTIEMBRE_JUGADO,
            leer_mensajes=historial,
        )
    )
    assert codigo == 0
    assert paginas_pedidas and paginas_pedidas[0] > 1, (
        f"el podio tiene que pedir más de una página: pidió {paginas_pedidas}")
    assert not subidas, "con el original a 44 mensajes de distancia, no debe republicar"


# @scenarios la-comprobacion-alcanza-los-dias-que-el-cron-corre
def test_el_lector_del_canal_pagina_de_verdad():
    """La paginación se comprueba sobre el lector real, no sobre el doble: es donde estaba el fallo."""
    from post_ranking import mensajes_recientes

    class CanalConDosPaginas:
        def __init__(self):
            self.llamadas = []

        def conversations_history(self, **kwargs):
            self.llamadas.append(kwargs)
            if "cursor" not in kwargs:
                return {"messages": [{"ts": "1"}], "response_metadata": {"next_cursor": "abc"}}
            return {"messages": [{"ts": "2"}]}

    canal = CanalConDosPaginas()
    assert len(mensajes_recientes(cliente=canal, paginas=3)) == 2, "junta las dos páginas"
    assert len(canal.llamadas) == 2, "para y no pide una tercera cuando se acaba el historial"
    assert canal.llamadas[1].get("cursor") == "abc", "usa el cursor que le dio la primera"

    # Con una sola página no pagina, que es lo que quiere el resumen diario.
    canal2 = CanalConDosPaginas()
    assert len(mensajes_recientes(cliente=canal2, paginas=1)) == 1
    assert len(canal2.llamadas) == 1
