"""Gate 4a (verify slice) y §11 (metrics)."""

from __future__ import annotations

from tests.harness.conftest import SLICE_VALIDO
from tools.wslice.metrics import build_report, collect_runs
from tools.wslice.spec_parser import parse_spec_file
from tools.wslice.verify import verify_slice

SLICE = {"ranking/ranking-diario.md": SLICE_VALIDO}
TEST_VERDE = """
# @scenarios publica-captura, sin-resultados-no-publica
def test_todo():
    assert True
"""


def test_verify_de_slice_inexistente_falla(make_workspace):
    ws = make_workspace(slices=SLICE)
    assert verify_slice(ws, "no-existe").status == "fail"


def test_verify_indeterminate_sin_spec_consolidada(make_workspace):
    """Antes del archive la spec consolidada no existe: indeterminate, no fail (§4)."""
    ws = make_workspace(
        slices=SLICE, tests={"tests/slices/ranking-diario/test_happy_path.py": TEST_VERDE}
    )
    report = verify_slice(ws, "ranking-diario")
    assert report.status == "indeterminate"
    assert report.requirements[0].status == "indeterminate"


def test_verify_falla_con_escenario_sin_test(make_workspace):
    ws = make_workspace(slices=SLICE)
    report = verify_slice(ws, "ranking-diario")
    assert report.status == "fail"


def test_verify_pasa_con_requirement_verificado_y_cobertura(make_workspace):
    spec = """\
    ## Requirement: El ranking del día se publica una sola vez
    Una reejecución del schedule el mismo día no publica un segundo mensaje.

    verified-by:
      - tests/slices/ranking-diario/test_happy_path.py
    """
    ws = make_workspace(
        slices=SLICE,
        specs={"ranking/spec.md": spec},
        tests={"tests/slices/ranking-diario/test_happy_path.py": TEST_VERDE},
    )
    report = verify_slice(ws, "ranking-diario")
    assert [r.status for r in report.requirements] == ["pass"]
    assert report.status == "pass"


def test_verify_falla_con_verified_by_roto(make_workspace):
    spec = """\
    ## Requirement: Algo
    Cuerpo.

    verified-by:
      - tests/slices/ranking-diario/test_que_no_existe.py
    """
    ws = make_workspace(
        slices=SLICE,
        specs={"ranking/spec.md": spec},
        tests={"tests/slices/ranking-diario/test_happy_path.py": TEST_VERDE},
    )
    report = verify_slice(ws, "ranking-diario")
    assert report.status == "fail"
    assert "verified-by roto" in report.requirements[0].reason


def test_verify_falla_con_requirement_sin_checks_ni_verified_by(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        specs={"ranking/spec.md": "## Requirement: Algo\nSin nada que lo verifique.\n"},
        tests={"tests/slices/ranking-diario/test_happy_path.py": TEST_VERDE},
    )
    report = verify_slice(ws, "ranking-diario")
    assert report.status == "fail"
    assert "al menos uno es obligatorio" in report.requirements[0].reason


def test_verify_strict_falla_con_pendientes(make_workspace):
    pendiente = """
    import pytest

    # @scenarios publica-captura, sin-resultados-no-publica
    @pytest.mark.skip
    def test_todo():
        assert True
    """
    ws = make_workspace(
        slices=SLICE, tests={"tests/slices/ranking-diario/test_happy_path.py": pendiente}
    )
    assert verify_slice(ws, "ranking-diario").status == "indeterminate"
    assert verify_slice(ws, "ranking-diario", strict=True).status == "fail"


def test_spec_parser_extrae_checks(make_workspace):
    spec = """\
    ## Requirement: La tabla tiene columna de temporada

    ```yaml
    checks:
      - type: column
        table: wordle_results
        column: season
    ```

    #### Scenario: se consulta el esquema
    - THEN la columna existe
    """
    ws = make_workspace(slices=SLICE, specs={"ranking/spec.md": spec})
    parsed = parse_spec_file(ws.abs("openspec/specs/ranking/spec.md"))
    assert len(parsed.requirements) == 1
    assert parsed.requirements[0].checks == ({"type": "column", "table": "wordle_results", "column": "season"},)


def test_metrics_agrega_runs(make_workspace):
    runs = """\
    - run: '2026-08-04T10:00:00Z'
      fase: propose
      actor: humano
      gates:
        validate: pass
        gates-mecanicos: pass
      rondas_correccion: 0
    - run: '2026-08-04T12:00:00Z'
      fase: verify
      actor: fabrica
      gates:
        tests: fail
      rondas_correccion: 2
      mutacion:
        mutantes: 3
        supervivientes: 1
    """
    ws = make_workspace(slices=SLICE, changes={"feat-x/runs.yaml": runs})
    report = build_report(collect_runs(ws))
    totals = report.totals
    assert report.parse_errors == 0
    assert totals["runs"] == 2
    assert totals["first_pass"] == 1
    assert totals["avg_rondas"] == 1.0
    assert totals["fails_por_gate"] == {"tests": 1}
    assert totals["mutantes_supervivientes"] == 1


def test_metrics_detecta_runs_malformados(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        changes={"feat-x/runs.yaml": "- run: '2026-08-04'\n  fase: inventada\n  actor: humano\n"},
    )
    report = build_report(collect_runs(ws))
    assert report.parse_errors == 1


def test_metrics_normaliza_timestamp_sin_comillas(make_workspace):
    """YAML parsea un timestamp desnudo como datetime; el schema lo acepta normalizado."""
    ws = make_workspace(
        slices=SLICE,
        changes={"feat-x/runs.yaml": "- run: 2026-08-04T10:00:00Z\n  fase: propose\n  actor: humano\n"},
    )
    report = build_report(collect_runs(ws))
    assert report.parse_errors == 0
    assert report.all_runs[0].run.startswith("2026-08-04")
