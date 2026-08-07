"""Los probes de `checks:`: lo que antes era `indeterminate` para todo.

Cada probe se prueba contra un repositorio de mentira construido en un `tmp_path`, no contra este mismo
repo: un test que dependa de que `post_ranking.yml` tenga hoy tal paso se rompe al reordenar el workflow y
no estaría probando el probe.

Los dos tests que importan son `test_env_var_caza_la_variable_que_falta` y
`test_dom_selector_caza_el_selector_que_no_existe`: son los dos fallos reales de esta semana, los dos
silenciosos, y los dos encontrados a mano días después.
"""

from __future__ import annotations

import pytest

from tools.wslice.probes import FAIL, INDETERMINADO, PASS, ejecutar, resumen
from tools.wslice.workspace import Workspace, WorkspaceConfig

WORKFLOW = """
name: Post ranking
on:
  schedule:
    - cron: '0 17 * * 1-5'
jobs:
  post:
    runs-on: ubuntu-latest
    steps:
      - name: Update data before snapshot
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        run: python3 tools/extract_slack.py | python3 tools/add_results.py

      - name: Capture and Post Ranking
        env:
          SLACK_BOT_TOKEN: ${{ secrets.SLACK_BOT_TOKEN }}
        run: python3 tools/post_ranking.py
"""


@pytest.fixture
def ws(tmp_path):
    """Un repositorio de mentira con un workflow, una config y dos surfaces."""
    (tmp_path / ".github/workflows").mkdir(parents=True)
    (tmp_path / ".github/workflows/post_ranking.yml").write_text(WORKFLOW, encoding="utf-8")

    (tmp_path / "wrangler.v2.jsonc").write_text(
        '// comentario que un .jsonc puede llevar\n'
        '{\n  "name": "cloud-district-wordle-2",\n'
        '  "assets": { "not_found_handling": "single-page-application" }\n}\n',
        encoding="utf-8",
    )

    (tmp_path / "v1").mkdir()
    (tmp_path / "v1/index.html").write_text('<div class="summary-cards"></div>', encoding="utf-8")
    (tmp_path / "v2/js").mkdir(parents=True)
    (tmp_path / "v2/js/ui.js").write_text('return `<div class="fila">…</div>`;', encoding="utf-8")

    return Workspace(root=tmp_path, config=WorkspaceConfig())


# ── el probe que justifica el módulo ────────────────────────────────────────────────────────────
def test_env_var_caza_la_variable_que_falta(ws):
    """El fallo real: el paso que publica no recibía `SUPABASE_URL`, así que el resumen salió sin medallas."""
    falta = ejecutar(ws, {
        "type": "env-var", "workflow": "post_ranking.yml",
        "step": "Capture and Post Ranking", "name": "SUPABASE_URL",
    })

    assert falta.estado == FAIL
    assert "NO recibe" in falta.detalle


def test_env_var_pasa_cuando_el_paso_la_recibe(ws):
    presente = ejecutar(ws, {
        "type": "env-var", "workflow": "post_ranking.yml",
        "step": "Update data before snapshot", "name": "SUPABASE_URL",
    })

    assert presente.estado == PASS


def test_env_var_mira_el_paso_y_no_el_workflow_entero(ws):
    """La variable existe en el workflow, pero en OTRO paso. Un `in contenido` daría un falso `pass`."""
    del_otro_paso = ejecutar(ws, {
        "type": "env-var", "workflow": "post_ranking.yml",
        "step": "Capture and Post Ranking", "name": "SUPABASE_URL",
    })
    sin_paso = ejecutar(ws, {"type": "env-var", "workflow": "post_ranking.yml", "name": "SUPABASE_URL"})

    assert del_otro_paso.estado == FAIL, "el probe está mirando el workflow entero"
    assert sin_paso.estado == PASS, "sin `step:` la pregunta es por el workflow, y ahí sí está"


def test_env_var_declara_un_paso_inexistente(ws):
    veredicto = ejecutar(ws, {
        "type": "env-var", "workflow": "post_ranking.yml", "step": "Paso que no existe", "name": "X",
    })

    assert veredicto.estado == FAIL
    assert "no tiene un paso" in veredicto.detalle


# ── el otro fallo real ──────────────────────────────────────────────────────────────────────────
def test_dom_selector_caza_el_selector_que_no_existe(ws):
    """La captura esperaba `.summary-cards`, que existe en la v1 y no en la v2."""
    en_v1 = ejecutar(ws, {"type": "dom-selector", "selector": ".summary-cards", "in": "v1"})
    en_v2 = ejecutar(ws, {"type": "dom-selector", "selector": ".summary-cards", "in": "v2"})

    assert en_v1.estado == PASS
    assert en_v2.estado == FAIL, "apuntar la captura a la v2 con este selector deja el resumen sin publicar"


def test_dom_selector_encuentra_un_selector_compuesto(ws):
    veredicto = ejecutar(ws, {"type": "dom-selector", "selector": ".liga .fila", "in": "v2"})

    assert veredicto.estado == PASS, "el selector compuesto se busca por su última parte"


# ── cron y workflow ─────────────────────────────────────────────────────────────────────────────
def test_cron_comprueba_la_expresion_declarada(ws):
    assert ejecutar(ws, {"type": "cron", "schedule": "0 17 * * 1-5"}).estado == PASS
    assert ejecutar(ws, {"type": "cron", "schedule": "0 9 * * *"}).estado == FAIL


def test_workflow_comprueba_que_existe_y_que_ejecuta_el_comando(ws):
    assert ejecutar(ws, {"type": "workflow", "workflow": "post_ranking.yml"}).estado == PASS
    assert ejecutar(
        ws, {"type": "workflow", "workflow": "post_ranking.yml", "runs": "python3 tools/post_ranking.py"}
    ).estado == PASS
    assert ejecutar(
        ws, {"type": "workflow", "workflow": "post_ranking.yml", "runs": "python3 tools/inventado.py"}
    ).estado == FAIL
    assert ejecutar(ws, {"type": "workflow", "workflow": "no_existe.yml"}).estado == FAIL


# ── config-key, con .jsonc ──────────────────────────────────────────────────────────────────────
def test_config_key_lee_un_jsonc_con_comentarios(ws):
    """Los config del proyecto llevan comentarios de línea, que JSON no admite."""
    bien = ejecutar(ws, {
        "type": "config-key", "file": "wrangler.v2.jsonc",
        "key": "assets.not_found_handling", "value": "single-page-application",
    })
    mal = ejecutar(ws, {
        "type": "config-key", "file": "wrangler.v2.jsonc",
        "key": "assets.not_found_handling", "value": "none",
    })

    assert bien.estado == PASS
    assert mal.estado == FAIL
    assert ejecutar(ws, {"type": "config-key", "file": "wrangler.v2.jsonc", "key": "no.existe"}).estado == FAIL


# ── honestidad: lo que no se puede decidir se declara ───────────────────────────────────────────
def test_los_tipos_que_necesitan_base_de_datos_dicen_por_que_son_indeterminados(ws):
    """Un probe que dijera `pass` sin mirar la base sería peor que no tenerlo."""
    for tipo in ("column", "table", "constraint", "rls-policy"):
        veredicto = ejecutar(ws, {"type": tipo, "table": "wordle_results", "column": "score"})
        assert veredicto.estado == INDETERMINADO, tipo
        assert "credenciales" in veredicto.detalle, tipo


def test_un_tipo_desconocido_es_indeterminado_y_no_revienta(ws):
    veredicto = ejecutar(ws, {"type": "telepatia"})

    assert veredicto.estado == INDETERMINADO
    assert "telepatia" in veredicto.detalle


def test_un_check_incompleto_es_indeterminado_y_no_revienta(ws):
    for check in ({"type": "env-var"}, {"type": "cron"}, {"type": "dom-selector"}, {"type": "config-key"}):
        assert ejecutar(ws, check).estado == INDETERMINADO, check


def test_el_resumen_da_prioridad_al_fallo(ws):
    from tools.wslice.probes import Veredicto

    assert resumen([Veredicto("a", PASS, "")]) == PASS
    assert resumen([Veredicto("a", PASS, ""), Veredicto("b", INDETERMINADO, "")]) == INDETERMINADO
    assert resumen([Veredicto("a", INDETERMINADO, ""), Veredicto("b", FAIL, "")]) == FAIL
    assert resumen([]) == INDETERMINADO, "sin checks no se puede afirmar nada"


# ── el probe de índice: el destino de la lección del doble permisivo ────────────────────────────
def test_index_caza_un_doble_que_no_impone_el_indice(tmp_path):
    """Diez tests en verde, seis mutantes muertos, y la migración real reventó a mitad.

    El doble no imponía el índice único, así que aceptaba escrituras que la tabla rechaza. Ningún mutante
    puede cazar eso: el hueco está en el test, no en el código. Este probe sí.
    """
    (tmp_path / "tests/slices/x").mkdir(parents=True)
    permisivo = tmp_path / "tests/slices/x/test_permisivo.py"
    permisivo.write_text(
        "class TablaFalsa:\n    def upsert(self, fila):\n        self.filas.append(fila)\n", encoding="utf-8"
    )
    ws = Workspace(root=tmp_path, config=WorkspaceConfig())
    check = {
        "type": "index", "table": "wordle_results",
        "name": "idx_slack_user_wordle_unique", "kind": "unique",
        "columns": ["slack_user_id", "wordle_id"],
    }

    veredicto = ejecutar(ws, check, {"tests_root": "tests/slices/x"})

    assert veredicto.estado == FAIL
    assert "más permisivo" in veredicto.detalle

    # y con un doble que impone las dos columnas y lanza, pasa
    permisivo.write_text(
        "class TablaFalsa:\n"
        "    def upsert(self, fila):\n"
        "        clave = (fila['slack_user_id'], fila['wordle_id'])\n"
        "        if clave in self.por_clave:\n"
        "            raise ViolacionDeIndiceUnico(clave)\n",
        encoding="utf-8",
    )
    assert ejecutar(ws, check, {"tests_root": "tests/slices/x"}).estado == PASS


def test_index_sin_tests_root_no_afirma_nada(tmp_path):
    ws = Workspace(root=tmp_path, config=WorkspaceConfig())
    check = {"type": "index", "name": "idx", "columns": ["a", "b"]}

    assert ejecutar(ws, check).estado == INDETERMINADO
    assert ejecutar(ws, {"type": "index", "name": "idx"}, {"tests_root": "t"}).estado == INDETERMINADO


# ── el probe de regex ───────────────────────────────────────────────────────────────────────────
def test_regex_comprueba_el_patron_en_el_fichero(ws, tmp_path):
    (tmp_path / "modulo.py").write_text('SEPARADOR = "/"\n', encoding="utf-8")

    assert ejecutar(ws, {"type": "regex", "file": "modulo.py", "pattern": '^SEPARADOR = "/"$'}).estado == PASS
    assert ejecutar(ws, {"type": "regex", "file": "modulo.py", "pattern": "^OTRA"}).estado == FAIL
    assert ejecutar(ws, {"type": "regex", "file": "no_existe.py", "pattern": "x"}).estado == FAIL
    assert ejecutar(ws, {"type": "regex", "file": "modulo.py"}).estado == INDETERMINADO
    assert ejecutar(ws, {"type": "regex", "file": "modulo.py", "pattern": "([bad"}).estado == INDETERMINADO
