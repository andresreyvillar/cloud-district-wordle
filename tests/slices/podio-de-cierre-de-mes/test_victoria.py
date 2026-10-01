"""La victoria del mes la noche del último día, de `podio-de-cierre-de-mes` y `resumen-diario-compuesto`.

Pack: `feat-victoria-el-ultimo-dia`. Sin red ni Slack: captura, subida y lectura del canal entran como dobles, y
el juego se pasa por parámetro. Los jugadores son sintéticos: el repositorio es público.
"""

from __future__ import annotations

import asyncio
import datetime
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

#: Cinco jugadores todos los laborables: así cada día cuenta para la temporada.
NOTAS = {"Ana": 3, "Bea": 4, "Cris": 4, "Dani": 5, "Eva": 5}
DIBUJOS = {"Ana": ".G.../.G..G/.GY../GGGGG", "Bea": "..G../..G../GGGGG"}


def jornada_de(fecha: str) -> int:
    return 1700 + (datetime.date.fromisoformat(fecha) - datetime.date(2026, 9, 1)).days


def laborables(desde: str, hasta: str) -> list[str]:
    dia, fin, fechas = datetime.date.fromisoformat(desde), datetime.date.fromisoformat(hasta), []
    while dia <= fin:
        if dia.weekday() < 5:
            fechas.append(dia.isoformat())
        dia += datetime.timedelta(days=1)
    return fechas


def mes(desde: str, hasta: str) -> list[dict]:
    return [
        {"slack_user_id": f"U_{n}", "player_name": n, "wordle_id": jornada_de(f), "score": s, "date": f,
         "pattern": DIBUJOS.get(n, "Y..../..Y../GGGGG")}
        for f in laborables(desde, hasta) for n, s in NOTAS.items()
    ]


def nivel(fecha):
    return {"jornada": jornada_de(fecha), "fecha": fecha}


def marca(fecha, nombre, segundos, estrellas=1):
    return {"jornada": jornada_de(fecha), "jugador": f"U_{nombre}", "segundos": segundos, "estrellas": estrellas}


# ── El mensaje: tres campeones desde octubre ──────────────────────────────────────────────────────────

OCTUBRE = mes("2026-10-01", "2026-10-30")
NIVELES_DE_OCTUBRE = [nivel(f) for f in ("2026-10-05", "2026-10-06")]
MARCAS_DE_OCTUBRE = [marca("2026-10-05", "Cris", 30), marca("2026-10-06", "Cris", 31), marca("2026-10-06", "Ana", 40)]


def felicitaciones(texto: str) -> list[str]:
    return [linea for linea in texto.splitlines() if linea.startswith(("👑", "🎮", "🎨"))]


# @scenarios los-tres-campeones-desde-octubre
def test_octubre_corona_tambien_al_campeon_del_juego_y_al_de_figuras():
    from podio import texto

    lineas = felicitaciones(texto(OCTUBRE, "2026-10", jornada_de("2026-10-30"), NIVELES_DE_OCTUBRE, MARCAS_DE_OCTUBRE))

    juego = next(l for l in lineas if l.startswith("🎮"))
    figuras = next(l for l in lineas if l.startswith("🎨"))
    assert "Cris" in juego and "20" in juego, juego
    from album import album

    lider = next(f for f in album(OCTUBRE, "2026-10")["jugadores"] if f["clasificado"] and f["posicion"] == 1)
    assert lider["nombre"] in figuras, figuras
    assert any(l.startswith("👑") and "Ana" in l for l in lineas), "el marcador sigue coronando a su campeón"


# @scenarios los-tres-campeones-desde-octubre
def test_un_empate_en_el_juego_se_comparte_y_una_competicion_vacia_no_corona():
    from podio import texto

    empate = [marca("2026-10-05", "Cris", 30), marca("2026-10-06", "Dani", 30)]
    con_empate = felicitaciones(texto(OCTUBRE, "2026-10", jornada_de("2026-10-30"), NIVELES_DE_OCTUBRE, empate))
    sin_juego = felicitaciones(texto(OCTUBRE, "2026-10", jornada_de("2026-10-30"), NIVELES_DE_OCTUBRE, []))

    juego = next(l for l in con_empate if l.startswith("🎮"))
    assert "Cris" in juego and "Dani" in juego and "comparten" in juego, juego
    assert not any(l.startswith("🎮") for l in sin_juego)


# @scenarios los-tres-campeones-desde-octubre
def test_septiembre_corona_solo_el_marcador():
    from podio import texto

    septiembre = mes("2026-09-01", "2026-09-30")
    niveles = [nivel("2026-09-25")]
    lineas = felicitaciones(texto(septiembre, "2026-09", jornada_de("2026-09-30"), niveles, [marca("2026-09-25", "Cris", 30)]))

    assert lineas and all(l.startswith("👑") for l in lineas), lineas


# ── La publicación: la última noche sale la victoria ─────────────────────────────────────────────────

class Canal:
    """El canal de Slack doblado: lo que ya hay y lo que se sube."""

    def __init__(self, mensajes=()):
        self.mensajes = list(mensajes)
        self.subidas: list[tuple[str, str]] = []

    def leer(self, paginas=1):
        return self.mensajes

    def subir(self, ruta, texto, titulo, canal=None):
        self.subidas.append((titulo, texto))
        self.mensajes.insert(0, {"bot_id": "B1", "files": [{"title": titulo}]})
        return True


async def _captura(objetivo):
    return "/tmp/captura-de-prueba.png"


@pytest.fixture
def publicador(monkeypatch):
    import post_ranking

    monkeypatch.setenv("RESUMEN_COMPUESTO", "1")
    monkeypatch.setattr(post_ranking, "leer_el_canal", lambda jornada=None, cliente=None: None)
    monkeypatch.setattr(post_ranking, "leer_la_palabra", lambda jornada, filas: ("tenaz", "firme en un propósito"))
    monkeypatch.setattr(post_ranking, "leer_juego", lambda: ([], []))
    return post_ranking


def publicar(post_ranking, resultados, canal):
    return asyncio.run(post_ranking.publicar(
        capturar=_captura, subir=canal.subir, resultados=resultados, leer_mensajes=canal.leer,
    ))


# @scenarios la-victoria-sale-la-noche-del-ultimo-dia, el-ultimo-dia-sale-la-victoria
def test_la_noche_del_ultimo_laborable_sale_la_victoria_y_no_el_resumen(publicador):
    canal = Canal()

    assert publicar(publicador, mes("2026-09-01", "2026-09-30"), canal) == 0

    assert len(canal.subidas) == 1
    titulo, texto = canal.subidas[0]
    assert "2026-09" in titulo and "Podio del mes" in titulo
    assert "🏆" in texto and "👑" in texto, "el podio y la felicitación"
    assert "Ranking Wordle" not in titulo


# @scenarios la-victoria-cuenta-la-ultima-jornada
def test_la_victoria_lleva_debajo_la_ultima_jornada(publicador):
    canal = Canal()
    publicar(publicador, mes("2026-09-01", "2026-09-30"), canal)

    _, texto = canal.subidas[0]
    victoria, jornada, despedida = texto.index("👑"), texto.index("TENAZ"), texto.index("🔄")
    assert victoria < jornada < despedida, "la última jornada va tras la victoria y antes de despedir el mes"
    assert "Ana" in texto[jornada:despedida], "con el mejor del día"


# @scenarios la-victoria-sale-la-noche-del-ultimo-dia, el-cierre-no-se-publica-dos-veces
def test_la_victoria_no_se_repite_ni_esa_noche_ni_el_dia_1(publicador):
    import post_podium

    canal = Canal()
    septiembre = mes("2026-09-01", "2026-09-30")
    publicar(publicador, septiembre, canal)

    publicar(publicador, septiembre, canal)  # la reintentona de esa misma noche
    asyncio.run(post_podium.celebrar(
        capturar=_captura, subir=canal.subir, resultados=septiembre + mes("2026-10-01", "2026-10-01"),
        leer_mensajes=canal.leer,
    ))

    assert len(canal.subidas) == 1, [t for t, _ in canal.subidas]


# @scenarios la-victoria-sale-la-noche-del-ultimo-dia
def test_si_esa_noche_no_salio_el_dia_1_la_publica(publicador):
    import post_podium

    canal = Canal()
    asyncio.run(post_podium.celebrar(
        capturar=_captura, subir=canal.subir,
        resultados=mes("2026-09-01", "2026-09-30") + mes("2026-10-01", "2026-10-01"), leer_mensajes=canal.leer,
    ))

    assert len(canal.subidas) == 1 and "2026-09" in canal.subidas[0][0]


# @scenarios el-ultimo-dia-sale-la-victoria
def test_un_dia_cualquiera_sigue_saliendo_el_resumen(publicador):
    canal = Canal()

    publicar(publicador, mes("2026-09-01", "2026-09-29"), canal)

    titulo, _ = canal.subidas[0]
    assert "Podio del mes" not in titulo


# @scenarios los-tres-campeones-desde-octubre
def test_desde_cuando_se_coronan_los_tres_es_lo_mismo_en_el_mensaje_y_en_la_web():
    import re

    from podio import DESDE_TRES_COMPETICIONES

    archivo = (Path(__file__).resolve().parents[3] / "v2/js/data/archivo.js").read_text(encoding="utf-8")
    [en_la_web] = re.findall(r"DESDE_TRES_COMPETICIONES = '([0-9-]+)'", archivo)

    assert DESDE_TRES_COMPETICIONES == en_la_web
