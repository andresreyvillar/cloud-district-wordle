"""Slack no lleva apodos, de `apodos-en-la-web` (Fase 2). Los apodos son solo de la web (decisión del dueño)."""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ / "tools"))


# @scenarios slack-no-lleva-apodos
def test_el_podio_del_canal_nombra_a_carrillo_por_su_nombre():
    from podios import podio_de_texto

    texto = podio_de_texto("📊 *Marcador*", [{"posicion": 1, "nombre": "Carrillo", "cifra": "3,00"}])

    assert "Carrillo" in texto
    assert "̶" not in texto and "ChatGPT" not in texto


# @scenarios slack-no-lleva-apodos
def test_el_pipeline_no_conoce_los_apodos():
    for fichero in (RAIZ / "tools").glob("*.py"):
        fuente = fichero.read_text(encoding="utf-8")
        assert "apodos" not in fuente.lower() and "̶" not in fuente, fichero.name
