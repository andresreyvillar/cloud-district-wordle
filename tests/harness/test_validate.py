"""Gate 1a: las 10 reglas de validación de slices (§3, §8 de la constitución)."""

from __future__ import annotations

import pytest

from tests.harness.conftest import SLICE_VALIDO
from tools.wslice.discover import discover_slices
from tools.wslice.validate import validate_all_slices


def errores(report) -> list[str]:
    return [issue.message for issue in report.errors]


def warnings(report) -> list[str]:
    return [issue.message for issue in report.warnings]


def test_slice_valido_pasa(make_workspace):
    ws = make_workspace(slices={"ranking/ranking-diario.md": SLICE_VALIDO})
    report = validate_all_slices(ws)
    assert report.ok, errores(report)
    assert report.slices_checked == 1


def test_filename_debe_coincidir_con_el_slug(make_workspace):
    ws = make_workspace(slices={"ranking/otro-nombre.md": SLICE_VALIDO})
    report = validate_all_slices(ws)
    assert not report.ok
    assert any("no coincide con el nombre de archivo" in m for m in errores(report))


def test_slug_de_slice_duplicado(make_workspace):
    ws = make_workspace(
        slices={
            "ranking/ranking-diario.md": SLICE_VALIDO,
            "publicacion/ranking-diario.md": SLICE_VALIDO,
        }
    )
    report = validate_all_slices(ws)
    assert not report.ok
    assert any("duplicado" in m for m in errores(report))


def test_escenario_duplicado(make_workspace):
    duplicado = SLICE_VALIDO.replace("### sin-resultados-no-publica", "### publica-captura")
    ws = make_workspace(slices={"ranking/ranking-diario.md": duplicado})
    report = validate_all_slices(ws)
    assert not report.ok
    assert any('slug de escenario duplicado "publica-captura"' in m for m in errores(report))


def test_sin_escenarios_es_warning(make_workspace):
    sin_escenarios = SLICE_VALIDO.split("## Comportamiento observable")[0]
    ws = make_workspace(slices={"ranking/ranking-diario.md": sin_escenarios})
    report = validate_all_slices(ws)
    assert report.ok, errores(report)
    assert any("no declara escenarios" in m for m in warnings(report))


def test_tests_root_inexistente_es_warning(make_workspace):
    ws = make_workspace(slices={"ranking/ranking-diario.md": SLICE_VALIDO})
    report = validate_all_slices(ws)
    assert any("tests_root" in m and "no existe" in m for m in warnings(report))


def test_capability_desconocida_es_error(make_workspace):
    ws = make_workspace(
        slices={"ranking/ranking-diario.md": SLICE_VALIDO.replace("- ranking", "- inexistente")}
    )
    report = validate_all_slices(ws)
    assert not report.ok
    assert any('capability desconocida "inexistente"' in m for m in errores(report))


def test_specs_vacio_es_error(make_workspace):
    sin_specs = SLICE_VALIDO.replace("specs:\n  - ranking\n", "specs: []\n")
    ws = make_workspace(slices={"ranking/ranking-diario.md": sin_specs})
    report = validate_all_slices(ws)
    assert not report.ok
    assert any("specs[] está vacío" in m for m in errores(report))


def test_trigger_ui_sobre_surface_no_declarada_es_error(make_workspace):
    ilegal = SLICE_VALIDO.replace("type: cron", "type: ui").replace(
        "surface: pipeline", "surface: tools"
    )
    ws = make_workspace(slices={"ranking/ranking-diario.md": ilegal})
    report = validate_all_slices(ws)
    assert not report.ok
    assert any("solo surfaces de entrada" in m for m in errores(report))


def test_trigger_ui_sobre_surface_declarada_pasa(make_workspace):
    legal = SLICE_VALIDO.replace("type: cron", "type: ui").replace(
        "surface: pipeline", "surface: web"
    )
    ws = make_workspace(slices={"ranking/ranking-diario.md": legal})
    report = validate_all_slices(ws)
    assert report.ok, errores(report)


def test_trigger_command_no_valida_surface(make_workspace):
    """command/cron/event no están restringidos a las surfaces de entrada (§3)."""
    ws = make_workspace(
        slices={
            "ranking/ranking-diario.md": SLICE_VALIDO.replace("type: cron", "type: command").replace(
                "surface: pipeline", "surface: cualquier-cosa"
            )
        }
    )
    report = validate_all_slices(ws)
    assert report.ok, errores(report)


def test_consume_sin_emisor_es_warning(make_workspace):
    consumidor = SLICE_VALIDO.replace("  consumes: []", "  consumes:\n    - ResultadoRegistrado")
    ws = make_workspace(slices={"ranking/ranking-diario.md": consumidor})
    report = validate_all_slices(ws)
    assert report.ok, errores(report)
    assert any("ningún slice del workspace emite" in m for m in warnings(report))


def test_consume_con_emisor_no_avisa(make_workspace):
    emisor = (
        SLICE_VALIDO.replace("slice: ranking-diario", "slice: ingesta-resultado")
        .replace("  emits: []", "  emits:\n    - ResultadoRegistrado")
        .replace("tests_root: tests/slices/ranking-diario/", "tests_root: tests/slices/ingesta-resultado/")
    )
    consumidor = SLICE_VALIDO.replace("  consumes: []", "  consumes:\n    - ResultadoRegistrado")
    ws = make_workspace(
        slices={
            "ranking/ranking-diario.md": consumidor,
            "ranking/ingesta-resultado.md": emisor,
        }
    )
    report = validate_all_slices(ws, "ranking-diario")
    assert not any("ningún slice del workspace emite" in m for m in warnings(report))


def test_wikilink_sin_resolver_es_warning(make_workspace):
    con_link = SLICE_VALIDO + "\n## Slices compañeros\n- [[slice-fantasma]] — no existe\n"
    ws = make_workspace(slices={"ranking/ranking-diario.md": con_link})
    report = validate_all_slices(ws)
    assert any("[[slice-fantasma]] sin resolver" in m for m in warnings(report))


def test_wikilink_marcado_tbd_no_avisa(make_workspace):
    con_link = SLICE_VALIDO + "\n## Slices compañeros\n- [[slice-fantasma]] (TBD) — futuro\n"
    ws = make_workspace(slices={"ranking/ranking-diario.md": con_link})
    report = validate_all_slices(ws)
    assert not any("sin resolver" in m for m in warnings(report))


def test_emitir_y_consumir_el_mismo_evento_es_error(make_workspace):
    ambos = SLICE_VALIDO.replace("  emits: []", "  emits:\n    - RankingPublicado").replace(
        "  consumes: []", "  consumes:\n    - RankingPublicado"
    )
    ws = make_workspace(slices={"ranking/ranking-diario.md": ambos})
    report = validate_all_slices(ws)
    assert not report.ok
    assert any("emite y consume el mismo evento" in m for m in errores(report))


def test_plantilla_no_cuenta_como_slice(make_workspace):
    ws = make_workspace(slices={"_template.md": SLICE_VALIDO})
    assert discover_slices(ws).slices == ()


@pytest.mark.parametrize(
    "campo,reemplazo",
    [
        ("status", "status: publicado"),
        ("kind", "kind: cosa"),
        ("trigger.type", "  type: telepatia"),
    ],
)
def test_frontmatter_invalido_es_error_de_parseo(make_workspace, campo, reemplazo):
    roto = SLICE_VALIDO
    if campo == "status":
        roto = roto.replace("status: proposed", reemplazo)
    elif campo == "kind":
        roto = roto.replace("kind: scheduled", reemplazo)
    else:
        roto = roto.replace("  type: cron", reemplazo)
    ws = make_workspace(slices={"ranking/ranking-diario.md": roto})
    report = validate_all_slices(ws)
    assert not report.ok
    assert report.parse_errors
