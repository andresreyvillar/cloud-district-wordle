# Tasks — refactor-adopcion-slices

Plan de ejecución para un implementador **sin contexto previo**. Este pack ya está ejecutado; el plan
queda como registro reproducible y como referencia de formato para los packs siguientes.

Regla del proyecto: máximo **3 intentos** ante un gate que falla; al tercero, parar y escalar.

---

## Tarea 0 — Preflight: confirmar el entorno antes de escribir nada

**Contexto.** El harness va en Python y su única dependencia es PyYAML. Hay que confirmar que está
disponible antes de decidir la implementación, y que `pytest` **no** está en el intérprete del sistema
(por eso se usa un venv del proyecto, no el global).

```bash
which python3 && python3 -V                      # esperado: 3.12.x
python3 -c "import yaml; print(yaml.__version__)" # esperado: 6.x
python3 -c "import pytest" 2>&1 | tail -1         # esperado: ModuleNotFoundError
git branch --show-current
```

**Decisión a tomar con lo que devuelva:**
- Si PyYAML **no** estuviera disponible: parar. Un parser de frontmatter a mano no entra en este pack.
- `pytest` se instala en `.venv/` del proyecto, **nunca** en el intérprete del sistema.

**Verificación.** Anotar las versiones en `runs.yaml` (campo `notas`).

---

## Tarea 1 — Estructura y manifest

### 1.1 · Directorios

```bash
mkdir -p openspec/slices openspec/changes/archive openspec/decisions
for c in resultados ingesta identidad estadisticas ranking publicacion dashboard; do
  mkdir -p "openspec/specs/$c" && touch "openspec/specs/$c/.gitkeep"
done
touch openspec/changes/archive/.gitkeep
mkdir -p tools/wslice tests/slices tests/harness
mkdir -p docs/context/sources docs/context/briefs docs/context/inbox
touch docs/context/inbox/.gitkeep tests/slices/.gitkeep
mkdir -p .claude/skills/{slice-propose,slice-implement,slice-audit,leccion,context-add}
```

### 1.2 · `openspec.workspace.yaml`

Las claves `slices`/`specs`/`changes`/`e2e_tests` son las que lee `tools/wslice/workspace.py`.
`apps` son las surfaces legales para triggers `ui`/`http` (§3): **solo `web` y `pipeline`**.
`test_roots` son las raíces extra donde el escáner busca `@scenarios`.

**Verificación.** `python3 -m tools.wslice slice list` responde sin excepción (dirá que no hay slices).

---

## Tarea 2 — La constitución y los artefactos de método

Escribir, en este orden (cada uno se apoya en el anterior):

1. `openspec/slice-system.md` — las 11 secciones. **§9 es obligatoria**: toda desviación respecto a
   `pga-cms` se declara ahí con su motivo. No inventar reglas nuevas: si algo no aplica, decir que no
   aplica y por qué.
2. `openspec/README.md` — la tabla de las 7 capabilities, **cada una citando el código del que se
   infiere**, y la tabla de surfaces.
3. `openspec/slices/_template.md` — con las secciones obligatorias del §2.
4. `openspec/decisions/README.md` + los 4 ADRs. El 0004 (stack de la v2.0) se deja con la sección
   **Decisión en blanco**: no se firma una decisión que el humano no ha tomado.
5. `docs/lecciones.md`, `docs/diario-desarrollo.md`, `docs/context/INDEX.md`,
   `docs/context/_ficha-template.md`.
6. `.claude/skills/*/SKILL.md` — los comandos de las skills deben ser los de **este** repo
   (`python3 -m tools.wslice`, `.venv/bin/python3 -B -m pytest`), no los de `pga-cms`.
7. `CLAUDE.md`.

**Verificación.** Los enlaces relativos entre documentos resuelven:

```bash
grep -ohE '\]\([0-9a-zA-Z._/-]+\.md\)' CLAUDE.md openspec/**/*.md docs/*.md \
  | tr -d '()' | sed 's/^\]//' | sort -u
```
Comprobar a mano que cada ruta existe (son pocas).

---

## Tarea 3 — El harness

**Contexto.** Port de `slspec` módulo a módulo. Los nombres de comandos, gates y estados se mantienen
**idénticos** a propósito (ADR 0002): los dos harness deben producir los mismos veredictos.

Orden de escritura (respeta las dependencias entre módulos):

| # | Archivo | Equivalente en slspec | Qué hace |
|---|---|---|---|
| 3.1 | `tools/wslice/workspace.py` | `workspace.ts` | localiza y valida el manifest |
| 3.2 | `tools/wslice/slice_schema.py` | `slice/schema.ts` | frontmatter, EventRef, matching de discriminadores |
| 3.3 | `tools/wslice/slice_parser.py` | `slice/parser.ts` | frontmatter + escenarios + wikilinks |
| 3.4 | `tools/wslice/discover.py` | `slice/discover.ts` | recorre `openspec/slices`, salta `_*.md` |
| 3.5 | `tools/wslice/validate.py` | `slice/validate.ts` | las 10 reglas del Gate 1a |
| 3.6 | `tools/wslice/coverage.py` | `slice/coverage.ts` | escáner `@scenarios` **multi-lenguaje** |
| 3.7 | `tools/wslice/spec_parser.py` | `spec/parser.ts` | Requirements, `checks:`, `verified-by:` |
| 3.8 | `tools/wslice/verify.py` | `verify/slice.ts` | Gate 4a |
| 3.9 | `tools/wslice/gates.py` | `verify/gates.ts` | los 3 gates mecánicos |
| 3.10 | `tools/wslice/metrics.py` | `metrics.ts` | schema de `runs.yaml` + agregación |
| 3.11 | `tools/wslice/cli.py` + `__main__.py` | `cli.ts` | argparse, iconos, exit codes |

**Tres puntos donde el port NO es literal** (y por qué):

- **`coverage.py`**: `slspec` solo entiende JSDoc + `test()`. Aquí hay que soportar además Python en
  sus formas idiomáticas: comentario `#` antes del `def`, docstring de una línea y docstring
  multilínea. La regla de propiedad es: *la anotación pertenece al `def test_` inmediatamente anterior
  si está a ≤ 3 líneas (caso docstring); si no, al siguiente*. Y `pending` se detecta por
  `@pytest.mark.skip/skipif/xfail/todo` o `pytest.skip(...)` en las primeras 5 líneas del cuerpo.
- **`metrics.py`**: YAML parsea un timestamp sin comillas como `datetime`. Hay que normalizarlo a
  string en lugar de rechazarlo (`slspec` tuvo la misma lección; ver su `runs.yaml`).
- **`gates.py`**: el regex de `test-commands` busca `pytest` / `playwright test` / `node --test`, no
  `pnpm test`.

**Verificación.**

```bash
python3 -m tools.wslice slice list
python3 -m tools.wslice slice validate
python3 -m tools.wslice verify gates
python3 -m tools.wslice metrics
```
Los cuatro con exit 0.

---

## Tarea 4 — Los tests del harness

**Contexto.** El harness es el único código de este pack, así que es lo único que puede tener tests.
Los fixtures se generan en `tmp_path`: un archivo con `@scenarios` dentro del repo contaminaría la
cobertura real de un slice futuro.

### 4.1 · Cableado

```bash
touch tests/__init__.py tests/harness/__init__.py
```

`pytest.ini` con `pythonpath = .` (necesario para `from tools.wslice... import`) y `testpaths = tests`.

### 4.2 · Los archivos

- `tests/harness/conftest.py` — fixture `make_workspace(slices, capabilities, tests, changes, specs)`
  que monta un workspace completo en `tmp_path`, y las constantes `MANIFEST` / `SLICE_VALIDO`.
- `tests/harness/test_validate.py` — una prueba por regla, más los casos negativos (frontmatter
  inválido) y el caso "la plantilla `_template.md` no cuenta como slice".
- `tests/harness/test_coverage.py` — las seis formas de anotación, el caso `@slice` explícito fuera de
  `tests_root`, el test sin anotación, el `@scenarios` inexistente y el archivo que no es de test.
- `tests/harness/test_gates.py` — `specs-coverage` (pasa / falta delta / delta sin Requirements /
  falta una capability de un slice multi-spec) y `test-commands` (con y sin comando).
- `tests/harness/test_verify_y_metrics.py` — `verify` en sus cuatro veredictos, `--strict`, el parser
  de `checks:`, y `metrics` (agregación, malformado, timestamp sin comillas).

**Verificación.**

```bash
.venv/bin/python3 -B -m pytest tests/harness -q
```
Esperado: **57 passed**.

---

## Tarea 5 — Cableado final del repo

### 5.1 · `requirements.txt` y `requirements-dev.txt`

El runtime declara lo que el pipeline ya usaba (`slack_sdk`, `supabase`, `python-dotenv`) más
`PyYAML`. El de desarrollo añade `pytest` y `playwright`.

### 5.2 · `.assetsignore`

Añadir el andamiaje para que Cloudflare **no** lo publique: `openspec/`, `docs/`, `tests/`, `.venv/`,
`pytest.ini`, `requirements*.txt`, `CLAUDE.md`, `.claude/`, `openspec.workspace.yaml`.

### 5.3 · `.gitignore`

Añadir `.venv/`, `.pytest_cache/`, `ranking_snapshot.png` (lo genera `post_ranking.py`).

### 5.4 · `README.md`

Reescribir: hoy dice que `data/data.json` es "la base de datos de resultados", falso desde febrero
(el almacén es Supabase y el JSON está congelado). Debe describir el sistema real, la puesta en
marcha y el método.

**Verificación.**

```bash
# El andamiaje no se publica
grep -E '^(openspec|docs|tests|\.venv|pytest\.ini|requirements|CLAUDE\.md|\.claude)' .assetsignore

# El código de producto sigue intacto
git diff --stat HEAD -- tools/add_results.py tools/extract_slack.py js/ css/ index.html .github/
#    esperado: sin salida
```

---

## Tarea 6 — Gate 4c: prueba de mutación sobre el harness

**Contexto.** El harness arranca con 52 tests verdes. Hay que demostrar que protegen algo.

```bash
git add -A          # fija la implementación en el index: la restauración sale de aquí
```

Mutaciones inyectadas (una a una, restaurando entre cada una) y su resultado real:

| # | Archivo | Mutación | Resultado |
|---|---|---|---|
| 1 | `tools/wslice/validate.py` | invertir la condición del trigger §3 (`not in` → `in`) | **muere** — caen `test_trigger_ui_sobre_surface_no_declarada_es_error` y `test_trigger_ui_sobre_surface_declarada_pasa` |
| 2 | `tools/wslice/coverage.py` | `DOCSTRING_LOOKAHEAD = 3` → `0` | **muere** — caen `test_python_docstring_del_test` y `test_python_docstring_multilinea` |
| 3 | `tools/wslice/gates.py` | quitar el filtro `.md` de `federated-untouched` | **SOBREVIVE** en la primera pasada → se refuerza (ver abajo) → **muere** en `test_federated_untouched_ignora_lo_que_no_es_markdown` |
| 4 | `tools/wslice/gates.py` | quitar `--untracked-files=all` | **muere** — cae `test_federated_untouched_falla_si_se_toca_una_spec_consolidada` |

Por cada una:
```bash
.venv/bin/python3 -B -m pytest -q       # DEBE fallar, y en el test esperado
git restore tools/wslice/<archivo>      # recupera desde el index
.venv/bin/python3 -B -m pytest -q       # DEBE volver a verde
```

**Qué hacer con el mutante 3, que sobrevivió.** `federated-untouched` depende de `git status` del
repo real y ningún test lo ejercitaba. El protocolo manda **reforzar**, no declarar el hueco: se
añaden 5 tests que montan un repo git temporal (`git init` en `tmp_path`) y cubren pass, fail, spec
ya staged, archivo no-markdown y ausencia de repo.

Al escribirlos, uno **falló contra el código sano** y destapó un bug real heredado del port:
`git status --porcelain` colapsa un directorio enteramente sin trackear en una sola línea
(`?? openspec/`), así que crear `openspec/specs/<nueva>/spec.md` en una capability nueva esquivaba el
gate por completo. Arreglo: `--untracked-files=all` (mutante 4 lo protege).

**Dos trampas del procedimiento, encontradas ejecutándolo** (ambas ya codificadas en el protocolo y
la skill):
- Sin `-B`, el `.pyc` del mutante sobrevive al `git restore` cuando coinciden tamaño y mtime al
  segundo, y el veredicto del gate es falso.
- Tras un arreglo real hecho a mitad del gate hay que `git add` antes de la siguiente mutación: el
  `git restore` restaura el index y un index viejo se lleva el arreglo.

---

## Tarea 7 — Registrar el run y cerrar

1. Crear `openspec/changes/refactor-adopcion-slices/runs.yaml` con las entradas de las fases
   `propose` y `verify` (§11): gates, rondas de corrección, datos de mutación y notas.
2. `python3 -m tools.wslice metrics` → debe leer el archivo sin errores de schema.
3. `git add -A` y **parar**. El commit y el merge son del humano (§7).

**Commits sugeridos** (un solo commit es aceptable dado que el pack es indivisible):

```
chore(method): adopt spec-driven slice development

- openspec/: constitution, 7 capabilities, slice template, 4 ADRs
- tools/wslice: python harness (validate, coverage, verify, gates, metrics)
- tests/harness: 52 tests over temporary workspaces
- .claude/skills: slice-propose, slice-implement, slice-audit, leccion, context-add
- docs/: lessons log, development diary, context pipeline
- CLAUDE.md, pytest.ini, requirements: project wiring
```

## Validación de cierre

```bash
python3 -m tools.wslice slice list
python3 -m tools.wslice slice validate
python3 -m tools.wslice verify gates --change-id refactor-adopcion-slices
python3 -m tools.wslice metrics
.venv/bin/python3 -B -m pytest -q
node --check js/script.js
git status --short
```
