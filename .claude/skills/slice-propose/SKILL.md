---
name: slice-propose
description: Propone un slice nuevo (o modifica uno existente) siguiendo el protocolo canónico de wordle-stats — autoría de slice + deltas + change pack, con gates mecánicos y TDD rojo. Usar cuando el usuario pida "crea un slice para X", "especifica la feature Y" o describa un comportamiento nuevo de la app.
---

# /slice-propose — Fases 0-2 del protocolo

**Constitución:** `openspec/slice-system.md` (LEER §2, §3, §5 antes de escribir nada).
**Herramienta:** `python3 -m tools.wslice` (desde la raíz del repo).

## Fase 0 — Bootstrap + colisión
1. Verificar el harness: `python3 -m tools.wslice slice list` funciona.
2. **Detección de colisión:** buscar en `slice list --json` un slice con el mismo trigger
   (`type + surface + detail` equivalente). Si existe → esto es una **modificación**, no un slice nuevo:
   - *menor* (texto/escenarios internos): editar el slice directamente.
   - *significativo* (eventos, specs[], actor): change pack sobre el slice existente.
   - *estructural* (trigger, afecta >1 slice): parar y proponérselo al usuario como propuesta aparte.
3. Identificar las capabilities cruzadas (de `openspec/specs/*`, ver la tabla de `openspec/README.md`).

## Fase 1 — Autoría
Escribir (usando `openspec/slices/_template.md` como base):

1. **Slice** `openspec/slices/<capability>/<slug>.md` — frontmatter §2 completo + escenarios
   `### <slug-escenario>` con **WHEN/THEN** bajo `## Comportamiento observable`.
   - `specs:[]` declara TODAS las capabilities cruzadas (multi-spec es la norma).
   - Trigger legal según §3: `ui` solo en `web`; `cron`/`command` en `pipeline`. `http` y `event`
     no tienen surface válida todavía — si el comportamiento la necesita, para y dilo.
   - Lo no verificado se marca `?` — NUNCA inventar columnas, mensajes de Slack ni selectores.
2. **Deltas** `openspec/changes/<change-id>/specs/<capability>/spec.md` por CADA capability de
   `specs:[]` — `## ADDED/MODIFIED/REMOVED Requirements`, cada Requirement con `checks:` y/o
   `verified-by:` + `#### Scenario:` GIVEN/WHEN/THEN.
   - **NUNCA editar `openspec/specs/` directamente** (federated-untouched, §5).
3. **Change pack** `openspec/changes/<change-id>/` — `proposal.md` (Why · What Changes ·
   **Out of Scope** · Impact · Validation Gates · tabla Capabilities) + `tasks.md` (pasos numerados
   para un implementador sin contexto, con comandos de test exactos).

Naming: change-id `feat-<slug>`; rama `chore/openspec-slice-<slug>`.

### Estilo de autoría (escenarios, Requirements, proposals)
- **Presente atemporal**: "el ranking excluye al jugador", nunca "excluirá" ni "se ha implementado".
- **Un comportamiento verificable por escenario** — si necesitas "y además", son dos escenarios.
- **Resultado observable, no implementación**: "la fila queda con score 7", no "llama a `upsert()`".
- **Testeable sin interpretación** — un test automatizado debe poder verificarlo tal cual.
- **Sin** fechas, números de PR, ni narrativa de changelog. Los nombres de jugadores reales solo
  cuando el comportamiento va específicamente de ellos (alias, fusiones); si no, usar roles.

## Fase 2 — TDD rojo
1. Crear los tests en `tests_root` (`tests/slices/<slug>/`), uno por grupo de escenarios,
   anotados y marcados como pendientes:

   ```python
   # @scenarios publica-captura, sin-resultados-no-publica
   @pytest.mark.skip(reason="TDD rojo — sin implementación todavía")
   def test_publica_el_ranking_del_dia():
       ...
   ```

   En JS/TS la anotación va en un bloque `/** @scenarios ... */` sobre un `test.fixme(...)`.
   Un unitario que viva fuera de `tests_root` debe declarar además `# @slice <slug>`.
2. **Gate 2:** `python3 -m tools.wslice slice coverage <slug>` → N/N escenarios declarados, exit 0.
3. Los tests DEBEN estar en rojo o pendientes. Verde aquí = test vacuo.

## Gates (máx 3 rondas de corrección; a la 3ª fallida → escalar al humano)
```bash
python3 -m tools.wslice slice validate <slug>                                  # Gate 1a
python3 -m tools.wslice verify gates --slice <slug> --change-id <change-id>    # Gate 1b
python3 -m tools.wslice slice coverage <slug>                                  # Gate 2
```
Los tres con exit 0 antes de continuar.

## Handoff
- `git add` de: slice, deltas, change pack, tests. **NUNCA commit automático.**
- Registrar el run de la fase `propose` en `openspec/changes/<change-id>/runs.yaml` (§11).
- Reportar al usuario: archivos creados, tabla capability→Requirements, resultado de gates,
  y el comando para arrancar la implementación: `/slice-implement <slug>`.
- Si el slice toca credenciales, RLS, el esquema de la tabla o los secrets de los workflows,
  avisar de que la Fase 4 incluirá security review.
