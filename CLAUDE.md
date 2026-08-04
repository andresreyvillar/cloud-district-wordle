# CLAUDE.md

Guía para Claude Code al trabajar en este repositorio.

## Project Overview

`wordle-stats` captura los resultados del Wordle diario que el grupo publica en un canal de Slack de
CloudDistrict y los convierte en una web de estadísticas y ranking, más una captura del ranking que
se publica cada día en el propio canal.

**Optimiza para:** desarrollo **spec-driven por slices verificables**. La spec es la fuente de
verdad; el código es una derivada demostrada por tests. Ver [ADR 0001](openspec/decisions/0001-desarrollo-por-slices.md).

**Constraints clave:**
- **Los datos son de personas reales.** La tabla tiene los resultados de compañeros identificables y
  el repositorio es **público**. Nada de escrituras exploratorias en producción, nada de volcar
  conversaciones del canal al repo.
- **Mergear a `main` despliega**: Cloudflare publica los assets y los cron corren desde `main`
  ([ADR 0003](openspec/decisions/0003-modelo-de-ramas-y-despliegue.md)).
- Specs, slices y documentación en español; identificadores y código en inglés. Palabras reservadas
  del esquema sin traducir (`WHEN`, `THEN`, `## ADDED Requirements`, claves de frontmatter).

## Tech Stack

- **Pipeline**: Python 3.12 (`slack_sdk`, `supabase`, `python-dotenv`, `PyYAML`) ejecutado por GitHub Actions
- **Web**: HTML + CSS + JavaScript vanilla, Plotly 2.27 y `@supabase/supabase-js` desde CDN, sin build
- **Datos**: Supabase (PostgREST + RLS de solo lectura para la clave pública)
- **Despliegue**: Cloudflare Workers assets (`wrangler.jsonc` + `.assetsignore`)
- **Harness**: `tools/wslice` (Python, solo PyYAML) — ver [ADR 0002](openspec/decisions/0002-harness-en-python.md)
- **Tests**: `pytest` (unitario y harness) + Playwright Python (e2e por slice)

El stack de la v2.0 está sin decidir ([ADR 0004](openspec/decisions/0004-stack-de-la-v2.md)).

## Architecture

```
openspec/
  slice-system.md        ← LA CONSTITUCIÓN: protocolo canónico (leer antes de cualquier slice)
  slices/<capability>/   ← slices (comportamiento observable, WHEN/THEN)
  specs/<capability>/    ← capability specs consolidadas (7 dominios)
  changes/<id>/          ← change packs (proposal + tasks + runs + deltas) · archive/
  decisions/             ← ADRs
tools/wslice/            ← harness: validate · coverage · verify · gates · metrics
tools/*.py               ← el pipeline: extract_slack → add_results · post_ranking
tests/slices/<slug>/     ← un directorio por slice (= tests_root del frontmatter)
tests/harness/           ← tests del propio harness
index.html · js/ · css/  ← la web (surface `web`)
docs/                    ← contexto, lecciones, diario
openspec.workspace.yaml  ← manifest del workspace para wslice
```

**Rules:**
- Comportamiento nuevo u observable = **slice** (vía `/slice-propose`). Nunca código directo sin spec.
- Los cambios de spec viven como **deltas** en `openspec/changes/<id>/specs/`; las consolidadas
  (`openspec/specs/`) solo se tocan en el archive post-merge.
- Trigger `ui` solo en la surface `web`; `cron`/`command` en `pipeline`. `http` y `event` no tienen
  surface válida todavía (§3).

## Coding Conventions

- **Determinista por defecto (§10):** la fecha y los datos entran por parámetro. Sin `datetime.now()`
  ni `Date.now()` fuera del borde del sistema (CLI, cron, carga de página) — es lo que hace posibles
  los golden tests del ranking.
- **Python**: `load_dotenv()` al inicio de todo script; `python3` explícito (nunca `python`).
- **JavaScript**: sin dependencias nuevas por CDN sin justificarlo; todo lo que entre al DOM desde
  datos pasa por `escapeHtml`.
- Slugs (slices, escenarios, change-ids): kebab-case estricto `[a-z0-9]+(-[a-z0-9]+)*`.
- Commits sin trailers de atribución y sin mencionar herramientas de IA.

## Testing and Quality Bar

El listón lo define `openspec/slice-system.md` §6. Antes de dar nada por completo:
- **TDD**: tests de escenario escritos ANTES de implementar (rojo o `skip`), verdes al terminar.
- Cada test de slice anota `# @scenarios <slug>, ...` (o `/** @scenarios ... */` en JS); cobertura
  100% de escenarios (`wslice slice coverage <slug>` exit 0).
- `wslice slice validate` + `wslice verify slice <slug>` + `wslice verify gates` en verde.
- PROHIBIDO debilitar/vaciar un test para ponerlo verde (los gates de mutación y adversarial lo cazan).
- **Prueba de mutación** (Gate 4c): 1-3 errores deliberados en el código nuevo deben poner los tests
  en rojo justo en el escenario mutado; restaurar (`git restore` desde el index) y volver a verde.
- La suite completa (`.venv/bin/python3 -B -m pytest`) sin regresiones.

## Context Pipeline

`docs/context/` es la capa de contexto (ver `docs/context/INDEX.md`): `inbox/` → `sources/` →
`briefs/` → canónico (`openspec/`). Ingesta SIEMPRE vía `/context-add`. La fuente principal de
requisitos es el **canal de Slack del grupo**: las reglas del juego se deciden conversando allí.
Jerarquía de verdad: specs+slices > ADRs/glosario > briefs > sources.

## Observability & Lessons (§11)

- Cada ejecución de fase sobre un change pack registra su run en `openspec/changes/<id>/runs.yaml`;
  `wslice metrics` agrega el histórico.
- Todo fallo con causa raíz produce una regla permanente vía `/leccion` → `docs/lecciones.md`
  (cascada: gate/CI > protocolo > skill > CLAUDE.md). Una lección `pendiente` es deuda — el audit la reporta.

## Development Diary

`docs/diario-desarrollo.md` es el registro didáctico del proyecto. Añadir entrada (qué / por qué /
decisión / aprendizaje) en cada hito: decisión de arquitectura, slice completado, cambio de método.
Presente atemporal, honesto con los errores.

## File Placement Rules

- Slice nuevo → `openspec/slices/<capability>/<slug>.md` (base: `openspec/slices/_template.md`).
- Deltas de spec → `openspec/changes/<change-id>/specs/<capability>/spec.md`.
- Tests del slice → `tests/slices/<slug>/` (= `tests_root` del frontmatter).
- No crear capabilities nuevas sin acordarlo: las 7 existentes salen del análisis del sistema en
  producción (ver `openspec/README.md`).
- Preferir editar un slice existente (modificación) a duplicarlo — colisión por trigger en Fase 0.

## Modelo de ramas — LEER ANTES DE EMPEZAR

Decisión completa en [ADR 0003](openspec/decisions/0003-modelo-de-ramas-y-despliegue.md).

```
feat/<change-id> · chore/openspec-slice-<slug>  ──PR──▶  main  ──▶  despliegue automático
```

- **Nunca se trabaja en `main`.** Toda autoría e implementación va en su rama.
- Merge **`--no-ff`** para que un cambio entero se deshaga con `git revert -m 1 <merge>`.
- **Mergear es desplegar.** Antes de mergear algo que toque `tools/`, asumir que el próximo cron
  escribirá en Supabase con ese código.

## Guardrails — Do NOT Touch Without Explicit Request

- NUNCA editar `openspec/specs/` fuera del paso de archive (federated-untouched).
- NUNCA editar `openspec/slice-system.md` — es la constitución; cambios requieren acuerdo explícito.
- NUNCA commit/push/merge automático: handoff staged, el humano decide.
- NUNCA escribir en la tabla de producción para explorar o probar. Los tests usan fixtures locales.
- NUNCA publicar en el canal de Slack fuera del workflow (el bot tiene `files:write`: un mal uso
  escribe delante de todo el grupo).
- NUNCA commitear `.env` ni pegar tokens en specs, tests o documentación.
- Máximo 3 intentos ante un gate que falla; al 3º parar y reportar.

## Commands

```bash
# Entorno de desarrollo
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt

# Harness (desde la raíz)
python3 -m tools.wslice slice list
python3 -m tools.wslice slice validate [slug]
python3 -m tools.wslice slice coverage <slug>
python3 -m tools.wslice verify slice <slug> [--strict]
python3 -m tools.wslice verify gates --slice <slug> --change-id <id>
python3 -m tools.wslice metrics

# Tests
.venv/bin/python3 -B -m pytest                 # todo
.venv/bin/python3 -B -m pytest tests/harness   # solo el harness
node --check js/script.js                   # sintaxis del frontend

# Pipeline (toca producción: usar con cabeza)
python3 tools/extract_slack.py | python3 tools/add_results.py
python3 tools/post_ranking.py

# Flujo
/slice-propose → /slice-implement <slug> → /slice-audit
```
