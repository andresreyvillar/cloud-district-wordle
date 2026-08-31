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

    def subida(ruta, texto_, titulo):
        subidas.append(("subida", titulo))
        return True

    # Sin mes nuevo: no se celebra y **no se saca la captura**, que es el paso caro.
    codigo = asyncio.run(post_podium.celebrar(
        capturar=captura, subir=subida, resultados=AGOSTO_JUGADO, leer_mensajes=lambda: []))
    assert codigo == 0 and not subidas

    # Ya celebrado: tampoco.
    marca = {"bot_id": "B1", "files": [{"title": "Podio del mes :trophy: · 2026-08"}]}
    codigo = asyncio.run(post_podium.celebrar(
        capturar=captura, subir=subida, resultados=AGOSTO_JUGADO + SEPTIEMBRE_JUGADO,
        leer_mensajes=lambda: [marca]))
    assert codigo == 0 and not subidas


# @scenarios la-imagen-es-la-de-la-web
def test_la_imagen_es_la_del_podio_de_esa_temporada():
    import post_podium

    capturado = []

    async def captura(objetivo):
        capturado.append(objetivo)
        return "/tmp/no-existe.png"

    codigo = asyncio.run(post_podium.celebrar(
        capturar=captura, subir=lambda r, t, ti: True,
        resultados=AGOSTO_JUGADO + SEPTIEMBRE_JUGADO, leer_mensajes=lambda: []))
    assert codigo == 0
    assert len(capturado) == 1
    objetivo = capturado[0]
    assert objetivo.url.endswith("/t/2026-08"), objetivo.url
    assert objetivo.espera == ".podio-card" and objetivo.captura == ".podio"
