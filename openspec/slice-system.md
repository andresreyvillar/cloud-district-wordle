# Sistema de Slices — protocolo canónico de wordle-stats

Este documento es la **fuente de verdad del método**. Define qué es un slice, cómo se escribe, y la
serie de **pasos obligatorios (sí o sí)** que todo cambio debe cumplir para llegar a `main`.
Deriva del sistema de slices de `pga-cms`, que a su vez deriva del de Oakmond; las desviaciones
están documentadas en §9.

Palabras clave: **DEBE** = obligatorio, un gate mecánico o de skill lo comprueba. **NUNCA** =
anti-patrón, bloquea el pipeline.

---

## §1 — Las 3 capas

| Capa | Ubicación | Lenguaje | Qué describe |
|---|---|---|---|
| **1. Slice** | `openspec/slices/<capability>/<slug>.md` | comportamiento observable | qué hace el sistema visto desde fuera (actor → trigger → efectos), end-to-end |
| **2. Capability spec** | `openspec/specs/<capability>/spec.md` | contrato técnico | Requirements verificables de un dominio (invariantes, columnas, selectores, schedules) |
| **3. Tests** | `tests/slices/<slug>/` + unitarios junto al código | verificación ejecutable | demuestran los escenarios del slice y los Requirements de las specs |

- Un slice **cruza** una o varias capabilities: las declara TODAS en `specs:[]` (**multi-spec es la norma**).
- N slices pueden referenciar el MISMO Requirement de la misma capability — el comportamiento
  compartido vive UNA vez en la capa 2, nunca duplicado en slices.
- **No existen slices "intermedios"**: lo que hace un módulo por dentro (una función de parseo, un
  helper de formato) es un Requirement de su capability spec, no un slice.

## §2 — Anatomía del slice

Archivo Markdown con frontmatter YAML. Frontmatter obligatorio:

```yaml
---
slice: <slug-kebab-unico>            # único en todo el repo
status: proposed                     # proposed | shipped | deprecated | blocked (monotónico)
kind: action                         # action | reaction | scheduled | maintenance | failure
actor: <jugador|grupo|sistema|...>
trigger:                             # ver §3
  type: <ui|http|event|cron|command>
  surface: <web|pipeline>
  detail: "<pantalla / VERBO ruta / evento / schedule cron>"
events:
  emits: []                          # eventos que emite (nombre canónico)
  consumes: []                       # eventos que consume
specs: [<capability>, ...]           # TODAS las capabilities cruzadas end-to-end
tests_root: tests/slices/<slug>/
blocked: null                        # { reason, since, by } si está pausado
---
```

Body — secciones (las 4 primeras obligatorias):

1. **Contexto** — qué intenta el actor y por qué (2-3 párrafos máx).
2. **Trigger técnico** — pantalla/comando/schedule exacto, payload relevante.
3. **Comportamiento observable** — escenarios `### <slug-escenario>` con **WHEN/THEN** atómicos.
   Cada escenario tiene **slug kebab-case estable y único dentro del slice**: es la clave de
   trazabilidad a tests (`@scenarios <slug>`). Renombrar un slug = rotura consciente (visible en verify).
4. **Estado después** — filas de la tabla, mensajes publicados, efectos externos, UI.
5. *Edge cases* — idempotencia, reejecución del cron, huecos de días, mensajes malformados. (recomendada)
6. *Eventos* / *Cadena downstream* — wikilinks `[[slug]]` a slices que reaccionan. (si aplica)

## §3 — Reglas de trigger (duras)

El slice vive donde está su **entry point externo**. Triggers válidos:

| type | dónde es válido | estado en este repo |
|---|---|---|
| `ui` | solo en surfaces de entrada con interfaz (`web`) | disponible |
| `http` | solo en una surface que exponga HTTP propio | **ninguna hoy**: la web es estática y Supabase es BaaS. Se habilita cuando exista una función servidor (Worker, Slack Events API) |
| `event` | cualquier proceso que consuma un bus | **ninguno hoy**: no hay bus. Reservado |
| `cron` | cualquier proceso con scheduler (`pipeline` vía GitHub Actions) | disponible |
| `command` | CLI / script invocable a mano (`pipeline`) | disponible |

**NUNCA**: un trigger `ui`/`http` sobre un módulo interno (`tools/*` como librería, un helper de
`js/`). Los módulos internos son librerías, no entry points. Su comportamiento se describe como
Requirement en la capability spec y los slices que los atraviesan lo referencian vía `specs:[]`.

Otras reglas duras de forma:
- Un slice **NUNCA** emite y consume el MISMO evento (el evento es un boundary asíncrono →
  son dos slices: `action` que emite + `reaction` que consume).
- Una lectura sin efectos intra-capability (mostrar un dato ya calculado) **no** es un slice →
  Requirement en la spec.
- `specs:` con una sola entrada en un flujo que claramente cruza dominios = síntoma de slice mal
  acotado (el audit lo marca).

## §4 — Requirements y verificación (capa 2)

Cada Requirement de una capability spec **DEBE** tener al menos uno de:

1. **`checks:`** — bloque YAML con ≥1 probe verificable mecánicamente contra el código. Tipos
   reservados (se implementan progresivamente en `tools/wslice`): `column`, `table`, `constraint`,
   `rls-policy`, `cron`, `workflow`, `env-var`, `config-key`, `cli-command`, `dom-selector`,
   `http-request`, `slack-api`.
2. **`verified-by:`** — lista de tests (`ruta/al/test.py` o `ruta#id`) que lo demuestran.

**Política `indeterminate`**: si un probe no puede decidir (o aún no está implementado), devuelve
`indeterminate`; el Requirement solo pasa si un `verified-by:` lo cubre. *(En v1 del harness todos
los probes son `indeterminate` → `verified-by` lleva el peso: TDD obligatorio por diseño.)*

Formato del Requirement (en deltas y en specs consolidadas):

```markdown
### Requirement: <Título en frase>
<cuerpo: la invariante>

```yaml
checks:
  - type: column
    table: wordle_results
    column: season
```

#### Scenario: <descripción>
- GIVEN ...
- WHEN ...
- THEN ...

verified-by:
  - tests/slices/<slug>/test_happy_path.py
```

## §5 — Change packs (ciclo de vida de un cambio)

Todo cambio con slice va en `openspec/changes/<change-id>/`:

```
openspec/changes/<change-id>/
├── proposal.md          # OBLIGATORIO: Why · What Changes · Out of Scope (nunca omitir) ·
│                        # Impact (slices/capabilities/archivos/migraciones/compat/riesgo) ·
│                        # Validation Gates (comandos exactos) · tabla Capabilities
├── tasks.md             # OBLIGATORIO: pasos numerados para un implementador sin contexto
│                        # (Path + contexto + diff/copy-paste + verificación), validación de
│                        # cierre con comandos exactos, commits sugeridos
├── runs.yaml            # OBLIGATORIO desde la primera fase ejecutada (§11)
├── design.md            # opcional
└── specs/<capability>/spec.md   # DELTAS: ## ADDED / MODIFIED / REMOVED Requirements
```

**Regla de oro (federated-untouched):** durante autoría e implementación **NUNCA** se editan las
specs consolidadas (`openspec/specs/<capability>/spec.md`). Los cambios de spec viven como **deltas**
dentro del change pack. Las consolidadas solo se actualizan en el **archive post-merge** (§6 fase 5).
Gate mecánico: `git status --porcelain` no puede contener `openspec/specs/` fuera de un archive.

Cambios sin slice (bug fix menor, docs, tooling): change pack con `> Slice: N/A — <razón>` en
`proposal.md`. Mismo ciclo, sin capa 1.

Naming: change-id `feat-<slug>` / `fix-` / `refactor-` / `docs-`; rama de autoría
`chore/openspec-slice-<slug>`; rama de implementación `feat/<change-id>`.

## §6 — EL PROTOCOLO: pasos sí-o-sí

Seis fases. Cada una tiene gates; **si un gate falla, no se avanza**. A mano se ejecuta vía las skills.

### Fase 0 — Decidir el artefacto
| Caso | Artefacto |
|---|---|
| Comportamiento observable nuevo (cruce de dominios, cron, publicación) | **Slice nuevo** + change pack |
| Modificación de comportamiento existente | **Modificar slice** (menor → editar; significativo → change pack; estructural → propuesta aparte) |
| Bug/refactor/docs sin cambio observable | **Change suelto** (`Slice: N/A`) |

**Gate 0:** decisión explícita. La skill detecta colisiones contra `wslice slice list` (mismo trigger ⇒ modificar, no duplicar).

### Fase 1 — Proponer (`/slice-propose`)
1. Bootstrap: `wslice` operativo, workspace válido.
2. Autoría: slice `.md` (frontmatter §2 + escenarios `WHEN/THEN` con slug) + **deltas** por cada
   capability de `specs:[]` (≥1 Requirement cada una) + change pack (`proposal.md` + `tasks.md`).
3. **Gate 1a — `wslice slice validate <slug>`:** frontmatter completo, trigger legal (§3), `specs:[]`
   resuelven, escenarios con slug único, wikilinks resolubles.
4. **Gate 1b — gates mecánicos:** federated-untouched · **spec-coverage** (cada capability declarada
   tiene delta con ≥1 Requirement) · tasks.md con comandos de test exactos.
5. Máximo **3 rondas** de corrección contra los gates; a la 3ª fallida → escalar al humano.
6. Handoff: archivos staged, **sin commit automático** — el humano revisa y committea.

### Fase 2 — TDD rojo (antes de implementar)
1. Por cada escenario del slice: **≥1 test que lo declare** vía `@scenarios <slug>` (e2e en
   `tests_root`; unitarios junto al código) escrito ANTES de la implementación.
2. **Gate 2 — `wslice slice coverage <slug>`:** cobertura declarativa completa (0 escenarios
   huérfanos). Los tests DEBEN estar en rojo o marcados pendientes (`@pytest.mark.skip`,
   `test.fixme`) — verde aquí = test vacuo.
   *(La eficacia real de estos tests se demuestra mecánicamente en el Gate 4c — prueba de mutación.)*

### Fase 3 — Implementar (`/slice-implement`)
1. Cargar contexto: proposal + tasks + deltas (= el contrato) + specs consolidadas (read-only).
2. Presentar plan derivado de `tasks.md` → **confirmación humana**.
3. Implementar acotado: **NUNCA** tocar módulos fuera de `specs:[]`, **NUNCA** inventar
   funcionalidad que el delta no pide, **NUNCA** editar specs consolidadas ni el slice `.md`.
4. Los tests de la Fase 2 pasan de rojo → verde. Prohibido debilitar un test para ponerlo verde.

### Fase 4 — Verificar (gates de "aprobable"; todo verde o no mergea)
1. `python3 -B -m pytest` en verde + sintaxis del frontend comprobada (`node --check js/*.js`).
   El flag `-B` es **obligatorio** en todo comando de test del protocolo: sin él, un `.pyc` escrito
   durante una mutación puede sobrevivir a la restauración y falsear el resultado del Gate 4c.
2. Migraciones de Supabase aplicadas y declaradas (cuando el change las traiga).
3. **Gate 4a — `wslice verify slice <slug>`:** probes de los `checks:` (pass/indeterminate) +
   `verified-by` existentes + **cobertura escenario↔test = 100%**.
4. **Gate 4b — cobertura de deltas:** cada Requirement del delta tiene código localizable
   (`path:line`) + ≥1 test.
5. **Gate 4c — prueba de mutación (eficacia de los tests):** con los tests en verde, inyectar
   deliberadamente 1-3 errores en el código NUEVO del slice (invertir una condición, alterar un
   operador/constante, eliminar una llamada) — solo código de producción, NUNCA los tests
   *(herramienta objetivo: `mutmut` sobre los archivos del diff, ver §10; el procedimiento manual
   es el fallback)*:
   - los tests DEBEN pasar a rojo, y el fallo debe caer en el test que cubre el escenario mutado
     (`@scenarios`); si siguen verdes, los tests no protegen ese punto → reforzarlos (volver a Fase 3);
   - restaurar la mutación (`git restore` desde el index; la mutación NUNCA se stagea ni committea)
     y los tests DEBEN volver a verde;
   - **el index es la única red de la restauración**: tras cualquier arreglo real hecho durante el
     gate, `git add` antes de mutar de nuevo — si no, el siguiente `git restore` se lo lleva;
   - **el bytecode también se restaura**: ejecutar siempre con `python3 -B`. Un `.pyc` del mutante
     con el mismo tamaño y el mismo mtime al segundo que el archivo restaurado se reutiliza, y los
     tests siguen rojos con el código ya correcto (o verdes con el código mutado);
   - registrar en el reporte cada mutación → test que la cazó.
6. **Gate 4d — auditoría adversarial:** verificadores independientes (subagentes sin contexto del
   implementador) intentan **refutar** que los escenarios se cumplen; ≥1 refutación sostenida = fail.
7. **Gate 4e — security review** si toca credenciales, RLS, esquema de la tabla, workflows con
   secrets o el token de Slack.
8. README tocado actualizado o declarado "sin cambios — verificado".

### Fase 5 — Aprobar + archivar
1. Estado `awaiting_approval`: el humano revisa el diff.
2. Merge `--no-ff` a `main`. **Solo el humano aprueba y mergea.**
   ⚠️ **Mergear a `main` despliega**: Cloudflare publica los assets y los workflows programados
   corren desde `main`. Ver [ADR 0003](decisions/0003-modelo-de-ramas-y-despliegue.md).
3. **Archive (post-merge):** los deltas se propagan a `openspec/specs/<capability>/spec.md`
   (ADDED añade, MODIFIED reemplaza, REMOVED borra), el change pack se mueve a
   `openspec/changes/archive/<YYYY-MM-DD>-<change-id>/`, y el slice transiciona
   `proposed → shipped` (primer archive que lo toca).
4. Post-archive: `wslice verify slice <slug>` DEBE pasar con cobertura completa.
5. **Revert de 1 clic**: `git revert -m 1 <merge-commit>` deshace el cambio entero.

### Fase 6 — Auditar (`/slice-audit`)
Periódico y pre-release, sobre TODO el inventario:
- **FAIL:** trigger ilegal (§3) · `wslice verify` en rojo.
- **WARN:** single-spec con señales cross-dominio · wikilinks rotos sin `(TBD)` · lecciones pendientes.
Exit ≠ 0 bloquea release.

## §7 — Reglas transversales (no negociables)

- **Comandos de test deterministas**: los comandos de `tasks.md`/Validation Gates son exactos y
  reproducibles; el implementador no improvisa comandos.
- **Cobertura obligatoria**: todo change que toque código añade o actualiza tests. Sin excepción.
- **El agente NUNCA despliega**: `main` es producción y el humano decide cuándo se mergea.
- **El agente NUNCA auto-committea ni auto-pushea** — handoff staged.
- **Los datos de producción son de personas reales**: los resultados de la tabla son de compañeros
  identificables. Nada de escrituras exploratorias en la tabla de producción; las pruebas usan
  fixtures locales. Si hace falta tocar producción, se hace con confirmación explícita y se revierte.
- **Out of Scope explícito** en toda proposal — lo que no se hace se declara.

## §8 — Anti-patrones (bloquean)

- Trigger `ui`/`http` sobre un módulo interno → **NUNCA** (§3).
- Editar `openspec/specs/` fuera de archive → **NUNCA** (§5).
- Slice que emite y consume el mismo evento → **NUNCA** (partir en dos).
- Implementar sin TDD rojo previo (Fase 2 saltada) → el gate 4a lo detecta.
- Test debilitado/vaciado para poner verde un escenario → los gates 4c y 4d lo cazan.
- Inventar handlers, columnas o mensajes no verificados en la autoría → marcar `?`, nunca rellenar a ojo.
- Duplicar un slice existente (mismo trigger) en vez de modificarlo → colisión en Fase 0.
- Auto-merge sin aprobación humana → **NUNCA**.
- **Reloj o aleatoriedad ambiente** en el código de producto → rompe los golden tests (§10).

## §9 — Desviaciones documentadas respecto a pga-cms

| pga-cms | wordle-stats | Por qué |
|---|---|---|
| Harness `@pga-cms/slspec` (TS/ESM, pnpm, zod) | `tools/wslice` (Python 3.12, solo PyYAML) | el repo no tiene Node ni build; Python ya es el stack del pipeline. Además el escáner de `@scenarios` es **multi-lenguaje** (`.py`, `.js`, `.ts`), así que el harness sobrevive al stack que elija la v2.0 |
| Monorepo pnpm + Turborepo, `apps/*` y `packages/*` | Repo plano: `js/` + `index.html` (web), `tools/` (pipeline) | proyecto de un solo despliegue; no hay workspaces que aislar |
| Playwright TS + Vitest | `pytest` (unitario) + Playwright Python (e2e) | Playwright Python ya es dependencia del pipeline (`tools/post_ranking.py`) |
| Gates `pnpm typecheck` / `lint` / `format:check` | `pytest` + `node --check js/*.js` | no hay TypeScript ni linter todavía; cuando entren, se añaden aquí (no antes) |
| Ramas `feat/… → develop → main` con MR | `feat/… → main` con PR, merge `--no-ff` | un solo desarrollador; `develop` no aporta y añade un salto. Ver ADR 0003 |
| `main` es producción y se despliega por pipeline aprobado | **`main` despliega solo**: Cloudflare publica al push y los cron corren desde `main` | consecuencia declarada, no accidente: el merge ES el despliegue (ADR 0003) |
| StrykerJS como herramienta de mutación (§10) | `mutmut` como objetivo; procedimiento manual como fallback | equivalente Python |
| 12 capabilities inferidas del legacy | 7 capabilities inferidas del pipeline actual | dominio mucho menor; salen del análisis del código y de la tabla en producción |
| Trigger `http` disponible (`apps/api`) | `http` sin surface válida hoy | la web es estática y Supabase es BaaS: no hay servidor propio |
| Pipeline de contexto alimentado por documentos del cliente | Alimentado por el **canal de Slack** del grupo | la fuente de requisitos es la conversación del grupo, no un cliente |

## §10 — Frontera determinista/agéntica

**Principio: determinista por defecto; el agente solo donde hay juicio.** El determinismo exigible
es el de **contrato** (mismo comportamiento observable, demostrado por los tests de escenario).
Todo proceso que no requiera juicio se implementa como herramienta determinista, nunca como agente.

### Reparto

| Proceso | Naturaleza |
|---|---|
| Scaffold de slice/change pack (plantillas) | herramienta |
| validate · coverage · verify · gates · metrics | herramienta (`tools/wslice`) |
| **Archive** (deltas → specs consolidadas, transición de estado) | herramienta — **NUNCA agente** |
| Mecánica git (rama, stage, merge, revert) | herramienta |
| Mutación (Gate 4c) | herramienta — `mutmut` sobre los archivos del diff; el procedimiento manual de la skill es el fallback |
| Cálculo de estadísticas y ranking | código determinista con **reloj y datos inyectados** (habilita golden tests) |
| Draftear slices/escenarios · lógica nueva · auditoría adversarial · destilado de contexto | agente (con los controles de abajo) |

### Controles de varianza donde el agente sí actúa

- **`tasks.md` prescriptivo** (bloques literales/copy-paste cuando sea posible). El plan se genera
  UNA vez; re-ejecutar la implementación es re-seguir el mismo plan, no re-planificar.
- **Append-only:** un slice `shipped` NUNCA se regenera. El rework es un change pack nuevo con
  deltas y diff revisable.
- **Golden/snapshot tests** para salidas sensibles a deriva (JSON del ranking, texto del mensaje de
  Slack, HTML renderizado).
- **Runtime determinista en el código de producto:** la fecha y los datos entran como parámetro;
  sin `datetime.now()`, `Date.now()` ni aleatoriedad fuera de los bordes del sistema (el borde es
  el CLI, el cron y la carga de la página). Es lo que hace posibles los golden tests.
- El no-determinismo del **Gate 4d (adversarial) es deliberado**: ángulos de ataque distintos en
  cada ejecución suman cobertura, no deriva.

## §11 — Observabilidad y bucle error→regla

### Run records (observabilidad)

Toda ejecución de las Fases 1-4 sobre un change pack registra su resultado en
**`openspec/changes/<id>/runs.yaml`** — el registro viaja con el change y se archiva con él.

Entrada mínima: `run` (ISO, **entrecomillado**), `fase` (propose|tdd|implement|verify), `actor`
(humano|fabrica), `gates` (mapa gate→pass|fail|skip), `rondas_correccion`. Opcionales: `modelo`,
`slice`, `mutacion {mutantes, supervivientes}`, `adversarial {intentos, refutaciones_sostenidas}`,
`tokens`, `duracion_min`, `notas`. Schema validado por `wslice metrics` (los malformados fallan).

Nombres de gate estables para que las métricas sean comparables entre packs:
`validate · gates-mecanicos · sintaxis · tests · verify-slice · mutacion · adversarial · security`.

**`wslice metrics`** agrega el histórico (first-pass rate, media de rondas, fails por gate,
mutantes supervivientes, refutaciones). Revisión periódica → al menos una decisión de mejora del
harness basada en datos.

### Bucle error→regla

Todo fallo de proceso con causa raíz (gate en rojo, error del agente, hallazgo humano) produce una
**regla permanente** codificada en el punto más fuerte alcanzable de esta cascada:

**1. mecánico** (gate/linter/CI/schema) > **2. protocolo** (este documento) > **3. skill** > **4. CLAUDE.md**

y se registra en **`docs/lecciones.md`** (vía `/leccion`) con dónde quedó codificada. La lección
NO es el artefacto — la regla codificada lo es: una lección `pendiente` es deuda y `/slice-audit`
la reporta. Los 3 intentos máximos ante un gate terminan, al escalar, en una lección.
