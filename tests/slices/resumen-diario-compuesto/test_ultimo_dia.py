"""El último día laborable del mes no sale el resumen sino la victoria, de `resumen-diario-compuesto`.

Pack: `feat-victoria-el-ultimo-dia`. Sin red: captura, subida y canal doblados.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from fixtures_mes import mes  # noqa: E402


@pytest.fixture
def subidas(monkeypatch):
    import post_ranking

    monkeypatch.setenv("RESUMEN_COMPUESTO", "1")
    monkeypatch.setattr(post_ranking, "leer_el_canal", lambda jornada=None, cliente=None: None)
    monkeypatch.setattr(post_ranking, "leer_la_palabra", lambda jornada, filas: None)
    monkeypatch.setattr(post_ranking, "leer_juego", lambda: ([], []))
    registro: list[str] = []

    async def captura(objetivo):
        return "/tmp/captura-de-prueba.png"

    def publicar(filas):
        asyncio.run(post_ranking.publicar(
            capturar=captura,
            subir=lambda ruta, texto, titulo, canal=None: registro.append(titulo) or True,
            resultados=filas,
            leer_mensajes=lambda paginas=1: [],
        ))
        return registro

    return publicar


# @scenarios el-ultimo-dia-sale-la-victoria
def test_el_30_de_septiembre_sale_la_victoria(subidas):
    assert subidas(mes("2026-09-30")) == ["Podio del mes 🏆 · 2026-09"]


# @scenarios el-ultimo-dia-sale-la-victoria
def test_el_29_sale_el_resumen_de_siempre(subidas):
    [titulo] = subidas(mes("2026-09-29"))

    assert "Podio del mes" not in titulo


# @scenarios el-ultimo-dia-sale-la-victoria
def test_con_el_resumen_apagado_el_ultimo_dia_sale_lo_de_siempre(subidas, monkeypatch):
    monkeypatch.setenv("RESUMEN_COMPUESTO", "0")

    [titulo] = subidas(mes("2026-09-30"))

    assert "Podio del mes" not in titulo
