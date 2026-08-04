"""Utilidades para probar el harness sobre workspaces temporales.

Los fixtures se generan en `tmp_path` a propósito: un archivo de test con
anotaciones `@scenarios` dentro del repo contaminaría la cobertura real.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.wslice.workspace import Workspace, load_workspace  # noqa: E402

MANIFEST = """\
slices: openspec/slices
specs: openspec/specs
changes: openspec/changes
e2e_tests: tests/slices
apps:
  - web
  - pipeline
test_roots:
  - tests
"""

SLICE_VALIDO = """\
---
slice: ranking-diario
status: proposed
kind: scheduled
actor: grupo
trigger:
  type: cron
  surface: pipeline
  detail: "0 17 * * * — publicación diaria del ranking"
events:
  emits: []
  consumes: []
specs:
  - ranking
tests_root: tests/slices/ranking-diario/
blocked: null
---

# El grupo recibe el ranking del día

## Comportamiento observable

### publica-captura
**WHEN** el schedule dispara y hay resultados del día
**THEN** se publica una captura del ranking en el canal.

### sin-resultados-no-publica
**WHEN** no hay ningún resultado del día
**THEN** no se publica nada.
"""


@pytest.fixture
def make_workspace(tmp_path: Path):
    """Crea un workspace mínimo en tmp_path y devuelve el Workspace cargado."""

    def factory(
        slices: dict[str, str] | None = None,
        capabilities: tuple[str, ...] = ("ranking", "publicacion", "estadisticas"),
        tests: dict[str, str] | None = None,
        changes: dict[str, str] | None = None,
        specs: dict[str, str] | None = None,
    ) -> Workspace:
        (tmp_path / "openspec.workspace.yaml").write_text(MANIFEST, encoding="utf-8")
        for capability in capabilities:
            (tmp_path / "openspec" / "specs" / capability).mkdir(parents=True, exist_ok=True)
        (tmp_path / "openspec" / "slices").mkdir(parents=True, exist_ok=True)
        (tmp_path / "openspec" / "changes").mkdir(parents=True, exist_ok=True)

        for rel, content in (slices or {}).items():
            target = tmp_path / "openspec" / "slices" / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(textwrap.dedent(content), encoding="utf-8")

        for rel, content in (tests or {}).items():
            target = tmp_path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(textwrap.dedent(content), encoding="utf-8")

        for rel, content in (changes or {}).items():
            target = tmp_path / "openspec" / "changes" / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(textwrap.dedent(content), encoding="utf-8")

        for rel, content in (specs or {}).items():
            target = tmp_path / "openspec" / "specs" / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(textwrap.dedent(content), encoding="utf-8")

        return load_workspace(tmp_path)

    return factory
