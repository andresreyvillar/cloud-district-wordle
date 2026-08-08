"""Gate 2: escáner multi-lenguaje de @scenarios y cobertura escenario↔test."""

from __future__ import annotations

from tests.harness.conftest import SLICE_VALIDO
from tools.wslice.coverage import report_slice_coverage, scan_all_tests
from tools.wslice.discover import find_slice_by_name

SLICE = {"ranking/ranking-diario.md": SLICE_VALIDO}


def estado(ws, slug: str) -> dict[str, str]:
    found = find_slice_by_name(ws, "ranking-diario")
    report = report_slice_coverage(ws, found)
    return {s.slug: s.status for s in report.scenarios}


def test_sin_tests_todo_uncovered(make_workspace):
    ws = make_workspace(slices=SLICE)
    assert estado(ws, "ranking-diario") == {
        "publica-captura": "uncovered",
        "sin-resultados-no-publica": "uncovered",
    }


def test_python_comentario_antes_del_test(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/slices/ranking-diario/test_happy_path.py": """
            # @scenarios publica-captura, sin-resultados-no-publica
            def test_publica_el_ranking():
                assert True
            """
        },
    )
    assert estado(ws, "ranking-diario") == {
        "publica-captura": "covered",
        "sin-resultados-no-publica": "covered",
    }


def test_python_docstring_del_test(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/slices/ranking-diario/test_happy_path.py": '''
            def test_publica_el_ranking():
                """@scenarios publica-captura"""
                assert True
            '''
        },
    )
    assert estado(ws, "ranking-diario")["publica-captura"] == "covered"


def test_python_docstring_multilinea(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/slices/ranking-diario/test_happy_path.py": '''
            def test_publica_el_ranking():
                """Publica la captura del día.

                @scenarios publica-captura
                """
                assert True
            '''
        },
    )
    assert estado(ws, "ranking-diario")["publica-captura"] == "covered"


def test_python_skip_cuenta_como_pendiente(make_workspace):
    """TDD rojo declarado: el escenario está cubierto pero pendiente (Fase 2)."""
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/slices/ranking-diario/test_happy_path.py": """
            import pytest

            # @scenarios publica-captura
            @pytest.mark.skip(reason="sin implementación todavía")
            def test_publica_el_ranking():
                assert True
            """
        },
    )
    assert estado(ws, "ranking-diario")["publica-captura"] == "pending"


def test_python_xfail_cuenta_como_pendiente(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/slices/ranking-diario/test_happy_path.py": """
            import pytest

            # @scenarios publica-captura
            @pytest.mark.xfail(reason="TDD rojo")
            def test_publica_el_ranking():
                assert False
            """
        },
    )
    assert estado(ws, "ranking-diario")["publica-captura"] == "pending"


def test_python_pytest_skip_en_el_cuerpo_cuenta_como_pendiente(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/slices/ranking-diario/test_happy_path.py": """
            import pytest

            # @scenarios publica-captura
            def test_publica_el_ranking():
                pytest.skip("aún no")
            """
        },
    )
    assert estado(ws, "ranking-diario")["publica-captura"] == "pending"


def test_javascript_jsdoc_antes_del_test(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/slices/ranking-diario/render.spec.js": """
            /** @scenarios publica-captura */
            test('pinta el ranking', () => {});
            """
        },
    )
    assert estado(ws, "ranking-diario")["publica-captura"] == "covered"


def test_javascript_fixme_cuenta_como_pendiente(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/slices/ranking-diario/render.spec.js": """
            /** @scenarios publica-captura */
            test.fixme('pinta el ranking', () => {});
            """
        },
    )
    assert estado(ws, "ranking-diario")["publica-captura"] == "pending"


def test_slice_explicito_fuera_de_tests_root(make_workspace):
    """Un unitario junto al código cuenta si declara @slice."""
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/unit/test_ranking.py": """
            # @slice ranking-diario
            # @scenarios sin-resultados-no-publica
            def test_no_publica_sin_datos():
                assert True
            """
        },
    )
    assert estado(ws, "ranking-diario")["sin-resultados-no-publica"] == "covered"


def test_test_sin_anotacion_no_aporta_cobertura(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/slices/ranking-diario/test_otro.py": """
            def test_algo():
                assert True
            """
        },
    )
    assert estado(ws, "ranking-diario")["publica-captura"] == "uncovered"


def test_escenario_inexistente_produce_warning(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/slices/ranking-diario/test_happy_path.py": """
            # @scenarios escenario-que-no-existe
            def test_algo():
                assert True
            """
        },
    )
    found = find_slice_by_name(ws, "ranking-diario")
    report = report_slice_coverage(ws, found)
    assert any('"escenario-que-no-existe" no existe' in w for w in report.warnings)


def test_archivo_que_no_es_test_se_ignora(make_workspace):
    ws = make_workspace(
        slices=SLICE,
        tests={
            "tests/slices/ranking-diario/helpers.py": """
            # @scenarios publica-captura
            def test_no_soy_un_archivo_de_test():
                assert True
            """
        },
    )
    assert scan_all_tests(ws) == []
