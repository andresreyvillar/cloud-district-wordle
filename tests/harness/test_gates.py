"""Gate 1b: gates mecánicos sobre las specs vivas (ADR 0009): specs-coverage, checks-probe y test-commands."""

from __future__ import annotations

from tests.harness.conftest import SLICE_VALIDO
from tools.wslice.gates import run_gates

SLICE = {"ranking/ranking-diario.md": SLICE_VALIDO}
SPEC = """\
# Spec de `ranking`

## Requirement: El ranking del día se publica una sola vez
Una reejecución del schedule el mismo día no publica un segundo mensaje.

verified-by:
  - tests/slices/ranking-diario/test_happy_path.py
"""
SPEC_CON_CHECK_ROTO = SPEC + """
## Requirement: El extractor declara su ventana

```yaml
checks:
  - type: regex
    file: tools/extract_slack.py
    pattern: 'VENTANA_EN_DIAS = 14'
    describe: la ventana es de catorce días
```
"""
TASKS_CON_TEST = "# Tasks\n\n## Tarea 1\n\n```bash\npython3 -m pytest tests/slices/ranking-diario\n```\n"
TASKS_SIN_TEST = "# Tasks\n\n## Tarea 1\n\nHacer las cosas y confiar.\n"


def gate(report, name: str):
    return next(g for g in report.gates if g.name == name)


def nombres(report) -> list[str]:
    return [g.name for g in report.gates]


def test_sin_argumentos_todo_es_skip_y_no_hay_gate_de_specs_intocables(make_workspace):
    """Con specs vivas, editar `openspec/specs/` es lo normal: el antiguo `federated-untouched` no existe."""
    report = run_gates(make_workspace(slices=SLICE))

    assert "federated-untouched" not in nombres(report)
    assert gate(report, "specs-coverage").status == "skip"
    assert gate(report, "test-commands").status == "skip"
    assert report.ok


def test_specs_coverage_pasa_con_la_spec_viva_del_dominio(make_workspace):
    ws = make_workspace(slices=SLICE, specs={"ranking/spec.md": SPEC})

    report = run_gates(ws, slice_name="ranking-diario")

    assert gate(report, "specs-coverage").status == "pass"
    assert report.ok


def test_specs_coverage_falla_si_el_dominio_no_tiene_spec(make_workspace):
    resultado = gate(run_gates(make_workspace(slices=SLICE), slice_name="ranking-diario"), "specs-coverage")

    assert resultado.status == "fail"
    assert any("ranking" in d and "spec" in d for d in resultado.details)


def test_specs_coverage_falla_si_la_spec_no_tiene_requirements(make_workspace):
    ws = make_workspace(slices=SLICE, specs={"ranking/spec.md": "# Spec de `ranking`\n\nnada todavía\n"})

    resultado = gate(run_gates(ws, slice_name="ranking-diario"), "specs-coverage")

    assert resultado.status == "fail"
    assert any("ningún" in d for d in resultado.details)


def test_specs_coverage_exige_spec_por_cada_capability(make_workspace):
    multi = SLICE_VALIDO.replace("  - ranking", "  - ranking\n  - publicacion")
    ws = make_workspace(slices={"ranking/ranking-diario.md": multi}, specs={"ranking/spec.md": SPEC})

    resultado = gate(run_gates(ws, slice_name="ranking-diario"), "specs-coverage")

    assert resultado.status == "fail"
    assert any("publicacion" in d for d in resultado.details)


def test_checks_probe_ejecuta_los_checks_de_la_spec_viva(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        specs={"ranking/spec.md": SPEC_CON_CHECK_ROTO},
        tests={"tools/extract_slack.py": "VENTANA_EN_DIAS = 7\n"},
    )

    resultado = gate(run_gates(ws, slice_name="ranking-diario"), "checks-probe")

    assert resultado.status == "fail", "la invariante declarada es falsa en el repositorio"


def test_el_change_pack_es_opcional(make_workspace):
    ws = make_workspace(slices=SLICE, specs={"ranking/spec.md": SPEC})

    report = run_gates(ws, slice_name="ranking-diario")

    assert gate(report, "test-commands").status == "skip"
    assert report.ok


def test_test_commands_falla_si_el_pack_opcional_no_declara_comandos(make_workspace):
    ws = make_workspace(slices=SLICE, specs={"ranking/spec.md": SPEC}, changes={"feat-x/tasks.md": TASKS_SIN_TEST})

    assert gate(run_gates(ws, slice_name="ranking-diario", change_id="feat-x"), "test-commands").status == "fail"


def test_test_commands_acepta_playwright(make_workspace):
    ws = make_workspace(slices=SLICE, changes={"feat-x/tasks.md": "```bash\nplaywright test tests/slices\n```\n"})

    assert gate(run_gates(ws, change_id="feat-x"), "test-commands").status == "pass"


def test_test_commands_con_comando_pasa(make_workspace):
    ws = make_workspace(slices=SLICE, changes={"feat-x/tasks.md": TASKS_CON_TEST})

    assert gate(run_gates(ws, change_id="feat-x"), "test-commands").status == "pass"


def test_slice_inexistente_falla(make_workspace):
    resultado = gate(run_gates(make_workspace(slices=SLICE), slice_name="no-existe"), "specs-coverage")

    assert resultado.status == "fail"
    assert any("no encontrado" in d for d in resultado.details)


def test_un_check_de_indice_se_mira_en_los_tests_de_su_requirement(make_workspace):
    """La spec viva es compartida: un check `index` declarado por un Requirement se comprueba con los tests que lo
    demuestran (`verified-by`), no con los de cualquier slice que cruce el dominio."""
    spec = """\
# Spec de `ranking`

## Requirement: Reprocesar no duplica filas

```yaml
checks:
  - type: index
    name: idx_unico
    columns: [slack_user_id, wordle_id]
```

verified-by:
  - tests/slices/ingesta/test_ingesta.py
"""
    doble = (
        "class TablaFalsa:\n"
        "    def upsert(self, fila):\n"
        "        if (fila['slack_user_id'], fila['wordle_id']) in self.vistas:\n"
        "            raise ValueError('duplicate key value violates unique constraint')\n"
    )
    ws = make_workspace(
        slices=SLICE,
        specs={"ranking/spec.md": spec},
        tests={"tests/slices/ingesta/test_ingesta.py": doble, "tests/slices/ranking-diario/test_x.py": "pass\n"},
    )

    resultado = gate(run_gates(ws, slice_name="ranking-diario"), "checks-probe")

    assert resultado.status != "fail", resultado.details
