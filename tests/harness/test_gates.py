"""Gate 1b: gates mecánicos (federated-untouched, specs-coverage y test-commands)."""

from __future__ import annotations

import shutil
import subprocess

import pytest

from tests.harness.conftest import SLICE_VALIDO
from tools.wslice.gates import run_gates

SLICE = {"ranking/ranking-diario.md": SLICE_VALIDO}
DELTA = """\
## ADDED Requirements

### Requirement: El ranking del día se publica una sola vez
Una reejecución del schedule el mismo día no publica un segundo mensaje.

verified-by:
  - tests/slices/ranking-diario/test_happy_path.py
"""
TASKS_CON_TEST = "# Tasks\n\n## Tarea 1\n\n```bash\npython3 -m pytest tests/slices/ranking-diario\n```\n"
TASKS_SIN_TEST = "# Tasks\n\n## Tarea 1\n\nHacer las cosas y confiar.\n"


def gate(report, name: str):
    return next(g for g in report.gates if g.name == name)


def test_gates_sin_argumentos_solo_comprueba_federated(make_workspace):
    ws = make_workspace(slices=SLICE)
    report = run_gates(ws)
    assert gate(report, "specs-coverage").status == "skip"
    assert gate(report, "test-commands").status == "skip"


needs_git = pytest.mark.skipif(shutil.which("git") is None, reason="git no disponible")


def _git_init(ws) -> None:
    subprocess.run(["git", "init", "-q"], cwd=ws.root, check=True)


@needs_git
def test_federated_untouched_pasa_sin_specs_tocadas(make_workspace):
    ws = make_workspace(slices=SLICE)
    _git_init(ws)
    assert gate(run_gates(ws), "federated-untouched").status == "pass"


@needs_git
def test_federated_untouched_falla_si_se_toca_una_spec_consolidada(make_workspace):
    """§5: los cambios de spec viven como deltas del change pack, nunca en las consolidadas."""
    ws = make_workspace(slices=SLICE, specs={"ranking/spec.md": "## Requirement: Algo\n"})
    _git_init(ws)
    resultado = gate(run_gates(ws), "federated-untouched")
    assert resultado.status == "fail"
    assert any("openspec/specs/ranking/spec.md" in d for d in resultado.details)


@needs_git
def test_federated_untouched_ignora_lo_que_no_es_markdown(make_workspace):
    """Un .gitkeep en un directorio de capability no es una spec tocada."""
    ws = make_workspace(slices=SLICE, specs={"ranking/.gitkeep": ""})
    _git_init(ws)
    assert gate(run_gates(ws), "federated-untouched").status == "pass"


@needs_git
def test_federated_untouched_detecta_specs_ya_staged(make_workspace):
    ws = make_workspace(slices=SLICE, specs={"ranking/spec.md": "## Requirement: Algo\n"})
    _git_init(ws)
    subprocess.run(["git", "add", "openspec/specs/ranking/spec.md"], cwd=ws.root, check=True)
    assert gate(run_gates(ws), "federated-untouched").status == "fail"


def test_federated_untouched_hace_skip_sin_repo_git(make_workspace):
    ws = make_workspace(slices=SLICE)
    assert gate(run_gates(ws), "federated-untouched").status == "skip"


def test_specs_coverage_pasa_con_delta_y_requirement(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        changes={
            "feat-ranking-diario/specs/ranking/spec.md": DELTA,
            "feat-ranking-diario/tasks.md": TASKS_CON_TEST,
        },
    )
    report = run_gates(ws, slice_name="ranking-diario", change_id="feat-ranking-diario")
    assert gate(report, "specs-coverage").status == "pass"
    assert report.ok


def test_specs_coverage_falla_si_falta_el_delta(make_workspace):
    ws = make_workspace(slices=SLICE, changes={"feat-ranking-diario/tasks.md": TASKS_CON_TEST})
    report = run_gates(ws, slice_name="ranking-diario", change_id="feat-ranking-diario")
    resultado = gate(report, "specs-coverage")
    assert resultado.status == "fail"
    assert any("falta el delta" in d for d in resultado.details)
    assert not report.ok


def test_specs_coverage_falla_si_el_delta_no_tiene_requirements(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        changes={
            "feat-ranking-diario/specs/ranking/spec.md": "## ADDED Requirements\n\nnada todavía\n",
            "feat-ranking-diario/tasks.md": TASKS_CON_TEST,
        },
    )
    resultado = gate(
        run_gates(ws, slice_name="ranking-diario", change_id="feat-ranking-diario"), "specs-coverage"
    )
    assert resultado.status == "fail"
    assert any("no declara ningún" in d for d in resultado.details)


def test_specs_coverage_exige_delta_por_cada_capability(make_workspace):
    multi = SLICE_VALIDO.replace("  - ranking", "  - ranking\n  - publicacion")
    ws = make_workspace(
        slices={"ranking/ranking-diario.md": multi},
        changes={
            "feat-ranking-diario/specs/ranking/spec.md": DELTA,
            "feat-ranking-diario/tasks.md": TASKS_CON_TEST,
        },
    )
    resultado = gate(
        run_gates(ws, slice_name="ranking-diario", change_id="feat-ranking-diario"), "specs-coverage"
    )
    assert resultado.status == "fail"
    assert any("publicacion" in d for d in resultado.details)


def test_test_commands_falla_sin_comando_de_test(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        changes={
            "feat-ranking-diario/specs/ranking/spec.md": DELTA,
            "feat-ranking-diario/tasks.md": TASKS_SIN_TEST,
        },
    )
    resultado = gate(
        run_gates(ws, slice_name="ranking-diario", change_id="feat-ranking-diario"), "test-commands"
    )
    assert resultado.status == "fail"


def test_test_commands_acepta_playwright(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        changes={"feat-x/tasks.md": "```bash\nplaywright test tests/slices\n```\n"},
    )
    assert gate(run_gates(ws, change_id="feat-x"), "test-commands").status == "pass"


def test_slice_inexistente_falla(make_workspace):
    ws = make_workspace(slices=SLICE, changes={"feat-x/tasks.md": TASKS_CON_TEST})
    resultado = gate(run_gates(ws, slice_name="no-existe", change_id="feat-x"), "specs-coverage")
    assert resultado.status == "fail"
    assert any("no encontrado" in d for d in resultado.details)
