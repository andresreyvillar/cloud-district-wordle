# Proposal — refactor-adopcion-slices

> **Slice: N/A** — instalar el método no introduce comportamiento observable de producto. No hay
> actor, no hay trigger de negocio y ningún jugador percibe nada distinto: solo el andamiaje para que
> los slices de la v2.0 tengan dónde vivir. Por §5, mismo ciclo de change pack sin capa 1.

## Why

La v1 lleva meses en producción (1530 resultados, ~13 jugadores activos) construida a base de commits
directos a `main`, sin especificación ni un solo test. El conocimiento del dominio vive implícito en
el código: el ancla de fechas del puzzle, los umbrales del ranking, el mapeo de nombres, la X que
cuenta como 7.

Eso ya produjo un fallo concreto y medible: el cambio que debía pasar la identidad de jugador a
`slack_user_id` quedó a medias — el código lo aparenta pero el extractor sigue emitiendo nombres
mostrados de Slack. Resultado en producción: 1234 de 1532 filas guardan un nombre en la columna de
ID, el diccionario de identidades quedó inerte, hay un jugador partido en dos por un renombre
(`Marcos Granado` / `marcos.granado`) y 8 filas atribuidas al jugador equivocado.

La v2.0 va a tocar exactamente eso — identidad, temporadas y ranking — con una fecha real de por
medio: el grupo acordó reiniciar el marcador el 1 de septiembre. Hacerlo con el mismo proceso
repetiría el mismo patrón.

Dos objetivos concretos:

1. **Que la decisión de producto se escriba antes del código y sea verificable.** Reiniciar el
   marcador y fusionar identidades toca datos históricos de personas reales.
2. **Dar frontera limpia al Gate 4c.** Si el andamiaje y el primer slice llegaran en el mismo cambio,
   la prueba de mutación no podría distinguir "código del harness" de "código nuevo del slice".
   Separarlos es un requisito del método, no una preferencia.

## What Changes

- **`openspec/`** — la constitución (`slice-system.md`, §1-§11 adaptados de `pga-cms` con las
  desviaciones documentadas en §9), el README con las 7 capabilities inferidas del sistema en
  producción, la plantilla de slice, los directorios de specs y changes, y 4 ADRs (tres firmados,
  el del stack de la v2.0 deliberadamente en propuesto).
- **`tools/wslice/`** — harness en Python (10 módulos, ~1200 líneas, única dependencia PyYAML) con
  los mismos comandos, gates y veredictos que `slspec`: `slice list/validate/coverage`,
  `verify slice/gates`, `metrics`. El escáner de `@scenarios` es **multi-lenguaje** (Python, JS, TS).
- **`tests/harness/`** — 57 tests del propio harness sobre workspaces temporales: las 10 reglas de
  validación, el escáner en sus seis formas (comentario, docstring de una línea, docstring
  multilínea, `pytest.mark.skip`, `xfail`, `pytest.skip()` en el cuerpo, JSDoc, `test.fixme`), los
  gates mecánicos, `verify` y el schema de `runs.yaml`.
- **`.claude/skills/`** — 5 skills: `/slice-propose`, `/slice-implement`, `/slice-audit`, `/leccion`,
  `/context-add`, con los comandos de este repo y el canal de Slack como fuente de contexto.
- **`docs/`** — `lecciones.md` (arranca con 3 lecciones reales, una de ellas `pendiente`),
  `diario-desarrollo.md` (incluye lo que la v1 decidió sin documentar) y la capa de contexto.
- **`CLAUDE.md`** — no existía. Guardrails del repo, incluidos los específicos de este proyecto:
  datos de personas reales, repo público, y que mergear a `main` despliega.
- **Cableado** — `openspec.workspace.yaml`, `pytest.ini`, `requirements.txt` / `requirements-dev.txt`,
  `.assetsignore` y `.gitignore` ampliados para que nada del andamiaje se publique en Cloudflare.
- **README.md** — reescrito: describía `data/data.json` como "la base de datos de resultados", que es
  falso desde febrero.

## Out of Scope

Lo que **no** entra, con el disparador objetivo que lo traería:

| Fuera | Disparador |
|---|---|
| Arreglar la identidad de jugadores (los 1234 nombres en la columna de ID, el duplicado de `Marcos Granado`, las 8 filas mal atribuidas) | Primer slice de la capability `identidad` — es comportamiento observable y necesita su propio pack |
| Columna o concepto de temporada en la tabla | Slice de `ranking` para la Season 2 |
| Tests del código de producción existente (`tools/*.py`, `js/script.js`) | Cada slice que toque ese código trae los suyos. Escribirlos ahora fijaría el comportamiento actual sin que nadie haya decidido cuál debe ser |
| Probes reales de `checks:` (`column`, `table`, `rls-policy`, `cron`) | El primer Requirement que los declare y necesite verificación mecánica |
| `mutmut` configurado (Gate 4c automatizado) | Un slice con lógica suficiente para que el mutante valga más que el procedimiento manual |
| Linter (`ruff`, `eslint`) y hook de pre-commit | Pack propio. **Mientras no exista, nada de esto está mecanizado** |
| CI que ejecute los gates en el PR | Pack propio. Hoy los gates se ejecutan a mano |
| Glosario (`openspec/glossary.md`) | El primer término del dominio en disputa (candidatos ya a la vista: "temporada", "racha", "fallo") |
| Tocar `data/data.json`, `extract_data.py` o `update.sh` (restos muertos de la v1) | Pack de limpieza propio; borrar historia merece su propio diff |
| Cambiar el frontend | ADR 0004 sin firmar |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Ninguno. No se crea, modifica ni cierra ningún slice |
| **Capabilities** | Se crean los 7 directorios vacíos. **No se escribe ninguna spec consolidada** (federated-untouched) |
| **Archivos nuevos** | `openspec/**` (13), `tools/wslice/**` (11), `tests/**` (7), `.claude/skills/**` (5), `docs/**` (5), `CLAUDE.md`, `openspec.workspace.yaml`, `pytest.ini`, `requirements*.txt` |
| **Archivos modificados** | `README.md`, `.gitignore`, `.assetsignore` |
| **Código de producto tocado** | **Ninguno.** `tools/*.py`, `js/`, `css/`, `index.html` y los workflows quedan intactos |
| **Migraciones** | Ninguna. No se toca el esquema ni una sola fila |
| **Compatibilidad** | Sin ruptura. El pipeline y la web siguen funcionando igual; el andamiaje es inerte hasta que se escriba el primer slice |
| **Riesgo** | **Bajo.** No hay comportamiento de producto afectado. El riesgo real es de método: es el mayor volumen de código nuevo del repo y no hay CI que lo vigile — de ahí los 57 tests del harness |

### Capabilities

| Capability | Toca | Por qué |
|---|---|---|
| *(ninguna)* | — | El andamiaje no implementa comportamiento de ningún dominio. Los 7 directorios se crean vacíos; la primera spec consolidada llegará en el archive del primer slice |

## Validation Gates

Comandos exactos. Todos deben pasar antes del handoff.

```bash
# 1 · El harness arranca y el workspace es válido
python3 -m tools.wslice slice list
python3 -m tools.wslice slice validate

# 2 · Los tests del harness en verde
.venv/bin/python3 -B -m pytest tests/harness -q

# 3 · Gates mecánicos de este propio pack
python3 -m tools.wslice verify gates --change-id refactor-adopcion-slices
#    esperado: federated-untouched pass · specs-coverage skip · test-commands pass

# 4 · Observabilidad: el runs.yaml de este pack valida
python3 -m tools.wslice metrics

# 5 · El código de producto sigue intacto
git diff --stat HEAD -- tools/add_results.py tools/extract_slack.py js/ css/ index.html .github/
#    esperado: sin salida

# 6 · Nada del andamiaje se publica en Cloudflare
grep -E '^(openspec|docs|tests|\.venv|pytest\.ini|requirements)' .assetsignore
```

**Gates de la Fase 4** y su tratamiento en este pack:

| Gate | Estado | Motivo |
|---|---|---|
| 4a `verify slice` | **skip** | No hay slice |
| 4b cobertura de deltas | **skip** | No hay deltas |
| 4c mutación | **aplica** | Cuatro mutaciones sobre el harness; una sobrevivió y obligó a añadir 5 tests y a arreglar un agujero del gate |
| 4d adversarial | **aplica, calibrado bajo** | No hay lógica de negocio que refutar; el objeto de ataque es el harness |
| 4e security | **aplica** | Se añaden reglas a `.assetsignore` y `.gitignore`; hay que demostrar que ningún secreto ni artefacto de desarrollo se publica |

## Notas de honestidad

- **El gate `test-commands` se satisface con una expresión regular** sobre `tasks.md`: busca `pytest`,
  `playwright test` o `node --test`. Que pase no demuestra que los comandos sean correctos ni que se
  hayan ejecutado. La evidencia real es la salida de los comandos de arriba. Queda registrado como
  lección `pendiente` en `docs/lecciones.md` con destino: probe que ejecute en lugar de buscar.
- **`verify gates` sin `--slice` deja `specs-coverage` en `skip`, y `skip` no rompe `ok`.** Es
  correcto para un pack `Slice: N/A`, pero el `ok: true` de este pack es más débil que el de un pack
  con slice.
- **Los probes de `checks:` no existen todavía** — ni aquí ni en `slspec`. Todo el peso de la
  verificación recae en `verified-by:`, es decir, en los tests. Es coherente con el método, pero no
  conviene llamarlo "verificación mecánica del contrato" hasta que los probes existan.
- **Este pack se autoriza a sí mismo en `main`.** Se escribe en el árbol de trabajo de `main` porque
  el método que exige rama es precisamente lo que este pack instala. Es la última vez: a partir del
  merge, la regla del ADR 0003 aplica.
- **El harness es código sin producto detrás.** 1200 líneas para un repo de 285 líneas de frontend.
  Se acepta porque los gates mecánicos son la diferencia entre un método y una intención, pero es una
  desproporción real que conviene mirar en la revisión de métricas.
