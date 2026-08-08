# Context snapshot — 2026-08-04 17:09

## 1 · Session Goal

Adaptar `wordle-stats` al método de desarrollo **spec-driven por slices** definido en
`/Users/andres/Projects/CloudDistrict/Pangea/pga-cms`, y con el método instalado, arrancar la **v2.0**:
temporadas mensuales, reestructuración de la web, ranking de figuras a partir de las cuadrículas de
emojis, y un sistema de medallas.

El proyecto llevaba meses en producción (1533 resultados, ~13 jugadores activos) construido a base de
commits directos a `main`, sin especificación ni un solo test, y con una migración de identidad a medias
que había corrompido datos. El objetivo era que la v2.0 no repitiera ese patrón.

## 2 · Current Status

**Rama `wordle_2`, subida a `origin`. `main` intacta y sin mergear.** Árbol de trabajo limpio.

```
2757a8d  feat(publicacion): wire badges into the daily summary
d144c8c  feat(v2): pattern capture, backfill, canonical identity spec and badges
d779d7e  docs(decisions): record hosting and v1/v2 coexistence decision
34e2e90  chore(method): adopt spec-driven slice development
```

102 archivos frente a `origin/main`. Suite: **73 passed, 8 skipped**. Harness: 4 slices validados,
30/30 escenarios cubiertos, 16 runs, 56% first-pass, 23 mutantes con 0 supervivientes.

### Los cuatro slices y su estado real

| Slice | Especificado | Implementado | En producción |
|---|---|---|---|
| `captura-del-patron` | sí | sí | **columna creada, código sin mergear** |
| `backfill-de-patrones` | sí | sí | **ejecutado: 1228 patrones recuperados** |
| `identidad-canonica-de-jugador` | sí | **NO** | — |
| `medallas-en-el-resumen-diario` | sí | sí (cableado) | no |

### Lo que ya cambió en producción (Supabase)

- **Columna `pattern`** (`text`, nullable) añadida a `wordle_results` vía MCP de Supabase.
- **1228 de 1533 filas** tienen su patrón recuperado del histórico del canal. Verificado: censo idéntico
  (1533), huella md5 de las columnas no-pattern idéntica antes y después
  (`08f2c9c40bcd7b50566fd7c4d395d683`), coherencia filas-del-patrón vs puntuación en las 1228 (1196 +
  32 fallos), y 3 filas comparadas carácter a carácter con su mensaje original.
- **305 filas sin patrón**: 298 con ID de Slack donde el mensaje trae nombre, 7 del jugador renombrado.
  Es el problema de identidad, no del comando.

### Archivos principales (rutas absolutas)

**Método y harness**
- `/Users/andres/Projects/Personal/wordle-stats/openspec/slice-system.md` — la constitución (§1-§11)
- `/Users/andres/Projects/Personal/wordle-stats/openspec/README.md` — las 7 capabilities
- `/Users/andres/Projects/Personal/wordle-stats/tools/wslice/` — harness Python (11 módulos)
- `/Users/andres/Projects/Personal/wordle-stats/tests/harness/` — 57 tests del harness
- `/Users/andres/Projects/Personal/wordle-stats/.claude/skills/` — slice-propose, slice-implement,
  slice-audit, leccion, context-add
- `/Users/andres/Projects/Personal/wordle-stats/CLAUDE.md`
- `/Users/andres/Projects/Personal/wordle-stats/openspec.workspace.yaml`
- `/Users/andres/Projects/Personal/wordle-stats/pytest.ini` — `pythonpath = . tools`

**Código de producto nuevo**
- `/Users/andres/Projects/Personal/wordle-stats/tools/patterns.py` — extracción de la cuadrícula
- `/Users/andres/Projects/Personal/wordle-stats/tools/backfill_patterns.py` — recuperación del histórico
- `/Users/andres/Projects/Personal/wordle-stats/tools/badges.py` — catálogo y cálculo de medallas
- `/Users/andres/Projects/Personal/wordle-stats/tools/add_results.py` — modificado: guarda `pattern`
- `/Users/andres/Projects/Personal/wordle-stats/tools/post_ranking.py` — modificado: sección de medallas
  + import diferido de playwright + viewport 1280px (cambio pendiente del usuario desde mayo)

**Decisiones y contexto**
- `/Users/andres/Projects/Personal/wordle-stats/openspec/decisions/` — ADRs 0001-0007
- `/Users/andres/Projects/Personal/wordle-stats/docs/roadmap-v2.md` — 6 fases
- `/Users/andres/Projects/Personal/wordle-stats/docs/lecciones.md` — 9 lecciones, 4 pendientes
- `/Users/andres/Projects/Personal/wordle-stats/docs/diario-desarrollo.md`
- `/Users/andres/Projects/Personal/wordle-stats/docs/context/briefs/reglas-temporadas.md`
- `/Users/andres/Projects/Personal/wordle-stats/docs/context/briefs/ranking-de-figuras.md`
- `/Users/andres/Projects/Personal/wordle-stats/docs/context/briefs/medallas.md`
- `/Users/andres/Projects/Personal/wordle-stats/docs/context/inbox/etiquetado-patrones.md` — **30
  cuadrículas esperando que el usuario las etiquete**

**Prototipo (scratchpad, NO en el repo)**
- `/private/tmp/claude-501/-Users-andres-Projects-Personal-wordle-stats/79daadfd-c456-4889-8991-553de30d7da1/scratchpad/loro_flores.py`
  — clasificador de figuras sin calibrar
- `.../scratchpad/grids.json` — 143 cuadrículas extraídas

### Roto o incompleto

- **El cron de `main` corre el código viejo**: los resultados nuevos **no** guardan su cuadrícula. Se
  arregla al mergear.
- **El clasificador de figuras no está calibrado**: manda el 69% a caca y falla en el único patrón
  etiquetado a mano. Bloquea 5 slices de la Fase 5 y 5 medallas de la Fase 6.
- **Gate 4d (adversarial) nunca ejecutado** en ninguno de los 5 packs: requiere subagentes, desactivados
  en la sesión salvo petición explícita.
- **Worker `cloud-district-wordle-2` sin crear**: falta el dato de configuración de Cloudflare.

## 3 · Pending Tasks

1. **[BLOQUEANTE] Implementar `identidad-canonica-de-jugador`.** El pack está completo en
   `openspec/changes/feat-identidad-canonica/` (proposal, tasks, deltas, runs.yaml) y los tests en
   `tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py` están en rojo con `skip`.
   Falta escribir `tools/canonical_identity.py` con la interfaz que los tests asumen:
   `canonizar(directorio, tabla, dry_run=False) -> Informe` con `resueltas`, `fusionadas`, `cruzadas`,
   `no_resueltas`, `ya_canonicas`. Seguir `tasks.md`: la **tarea 1 es copia de seguridad obligatoria** de
   la columna a `~/wordle-identidad-antes.json` (fuera del repo, que es público), y la **5.1 es el ensayo
   `--dry-run`**, cuyas cifras esperadas son ~1235 resueltas, 4 fusionadas, 8 cruzadas, 0 no resueltas.
   Si las fusiones o las cruzadas no son 4 y 8, PARAR.
2. **Relanzar `python3 tools/backfill_patterns.py --dry-run` después de la canonización.** Es idempotente
   y debería bajar las 305 filas no resueltas a cerca de 0.
3. **Mergear `wordle_2` a `main`** (decisión del usuario, aún no autorizada). Mergear activa la captura de
   patrones en el cron horario y publica la sección de medallas en el canal. Merge `--no-ff` según ADR 0003.
4. **Especificar e implementar el slice de gráficas.** ADR 0007 firmado: arreglar la **forma** con Plotly
   antes de cambiar de librería. Los seis anti-patrones a corregir están en el ADR, con la tabla de formas
   propuestas por vista. Incluye modo oscuro y escalas fijas (petición del grupo).
5. **Calibrar el clasificador de figuras.** Esperando que el usuario etiquete las 30 cuadrículas de
   `docs/context/inbox/etiquetado-patrones.md` (loro/flor/escuadra/caca). Con las etiquetas: ajustar pesos
   en el prototipo, medir acierto, y decidir si la heurística basta o hace falta un modelo. Desbloquea la
   Fase 5 (5 slices) y las 5 medallas de figuras.
6. **Fase 0.2: crear el Worker `cloud-district-wordle-2`.** Falta un dato del usuario: en *Workers & Pages
   → cloud-district-wordle → Settings → Build*, si hay repo conectado y qué comando de deploy usa. Los MCP
   `cloudflare-builds` y `cloudflare-bindings` están configurados pero **sin autenticar** (`/mcp`). La
   configuración ya está decidida: archivo `wrangler.v2.jsonc` aparte con
   `name: cloud-district-wordle-2`, `assets.directory: "./app"`,
   `not_found_handling: "single-page-application"`, desplegado con `wrangler deploy --config`.
7. **Fase 1.2: `ingesta-por-id-de-slack`** (el extractor emite el ID). Va **después** de la tarea 1, nunca
   antes: emitir IDs primero duplicaría 32 de las 40 últimas filas.
8. **Deuda del método**: 4 lecciones `pendiente` en `docs/lecciones.md`, todas con destino mecánico
   declarado — que el escáner entienda `pytestmark`, un probe `row-count`, que `test-commands` ejecute en
   vez de buscar con regex, un comando `wslice mutate`, y un check de entorno contra
   `requirements-dev.txt`.
9. **Llevar al canal el modelo de participación** para que el grupo lo valide antes de implementarlo. El
   argumento no es la fórmula sino el diagnóstico: hoy el ranking lo gana quien juega tres días.

## 4 · Key Decisions & Context

### Los siete ADRs (`openspec/decisions/`)

| ADR | Estado | Decisión |
|---|---|---|
| 0001 | aceptado | Desarrollo spec-driven por slices, protocolo completo incluidos gates 4c (mutación) y 4d (adversarial) |
| 0002 | aceptado | Harness en **Python** (`tools/wslice`), no el port TS de `slspec`. Escáner de `@scenarios` multi-lenguaje (py/js/ts) para no atar el stack |
| 0003 | aceptado | Ramas `feat/… → main` con PR, merge `--no-ff`. **Mergear a `main` ES desplegar**: Cloudflare publica al push y los cron corren desde `main` |
| 0004 | aceptado | Stack v2: **vanilla + módulos ES, sin build**. `js/domain/` puro + `js/ui/` + `router.js`. Límite declarado: si aparece un segundo consumidor del mismo cálculo, revisar a favor de mover el dominio a Python. **Las medallas ya activaron ese límite** |
| 0005 | aceptado | v2 en Worker nuevo `cloud-district-wordle-2`; **la v1 no se mueve**. Una sola BD con invariante dura: **mientras la v1 esté publicada, el esquema solo crece** — nunca renombrar ni borrar `player_name`, `wordle_id`, `score`, `date` |
| 0006 | aceptado | Estructura de la v2: 5 secciones, selector de temporada como eje, URL propia por vista (`/`, `/t/<AAAA-MM>`, `/t/<AAAA-MM>/j/<x>`, `/temporadas`, `/hoy`, `/datos`) |
| 0007 | aceptado | **Forma antes que librería**: arreglar los seis anti-patrones con Plotly y decidir la librería después |

### Plataforma y entorno

- **macOS**, Python 3.12.8 en `/usr/local/bin/python3`. Venv del proyecto en `.venv/`, creado con
  `pip install -r requirements-dev.txt` (**no** instalar paquetes sueltos: ya causó un fallo).
- **Comandos de test SIEMPRE con `-B`**: `.venv/bin/python3 -B -m pytest`. Sin `-B`, un `.pyc` de una
  mutación puede sobrevivir a `git restore` (mismo tamaño y mtime al segundo) y falsear el Gate 4c.
- **TLS en macOS**: `urllib` y `slack_sdk` fallan con los certificados del sistema. La solución **no** es
  `CERT_NONE` (como hace `tools/extract_slack.py`, que expone el token del bot) sino
  `ssl.create_default_context(cafile=certifi.where())`. Verificado que funciona.
- **Credenciales** en `/Users/andres/Projects/Personal/wordle-stats/.env` (en `.gitignore`):
  `SLACK_BOT_TOKEN`, `SLACK_CHANNEL_ID`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`,
  `SUPABASE_SERVICE_ROLE_KEY`. Los mismos existen como secrets de GitHub Actions.
- **MCP de Supabase conectado y autenticado**, limitado a este proyecto:
  `claude mcp add --transport http supabase "https://mcp.supabase.com/mcp?project_ref=oogturrjjcyrvzmiufff"`
  (scope local, en `~/.claude.json`). Sin `read_only`, así que puede modificar esquema y datos.
- **El repositorio es PÚBLICO** y los datos son de compañeros identificables. Nada de volcados con
  nombres al repo; las copias de seguridad van a `~/`.
- El bot de Slack tiene scopes `channels:history, groups:history, users:read, files:write`. **No** tiene
  `channels:read` (`conversations.info` da `missing_scope`).

### Estado del esquema, verificado por SQL

- PK `id` (uuid). Unicidad por **índice único** `idx_slack_user_wordle_unique (slack_user_id, wordle_id)`
  — **no es una constraint**: `pg_constraint` solo tiene la PK. Es lo que hace funcionar el `on_conflict`.
- `slack_user_id` es nullable, y dos `NULL` no colisionan en un índice único (hoy 0 filas nulas).
- **RLS: una sola política**, `SELECT` para `public` con `qual = true`. No hay políticas de escritura, y
  eso es lo que hace segura la clave publicable del frontend.
- La fecha se deriva del número de puzzle (ancla: #1485 = 2026-01-30), no del timestamp del mensaje. Las
  1533 filas son coherentes con el ancla.

### Datos medidos (no asumir, están verificados)

- 1533 filas, 22 jugadores en el histórico, 13 activos, 253 días con 70 huecos.
- **1234 filas guardan un nombre** en `slack_user_id`, 298 un ID real (`Andrés R.`, `Carlos H.`, `Iván A.`).
  *(Cuidado: una versión anterior de este dato decía 1312 y era falsa, medida sobre una sola página de
  PostgREST. PostgREST pagina a 1000 filas.)*
- `Marcos Granado` y `marcos.granado` → **mismo ID** `U0B1LT5T406`, con 4 puzzles duplicados de
  puntuación idéntica.
- 8 filas con ID `U08KF6V12CB` (que es de **Paula**) llevan `player_name = Carlos H.`, con puntuaciones
  distintas de las de Paula esos días. **Decisión del usuario: eliminarlas.**
- Los 1235 nombres se resuelven **al 100%** a un ID vía `users.list`. Cero casos manuales.
- 97% de las cuadrículas resueltas acaban en `GGGGG`, así que el análisis de figuras excluye la última
  fila. 37% de las partidas dejan ≤2 filas de camino: sin lienzo.
- Los dos rankings premian a gente distinta: partidas sin lienzo 2,9 intentos de media; con lienzo 4,7.
- Suertud@ (resolver en 1 intento): **2 casos en 1533** (Quique #1485, Javi Calvo #1419).
- El día más duro: **#1538, media 6,00**; lo resolvieron en ≤4 solo Claire y Andrés R.

### Reglas de producto acordadas

- **Temporadas mensuales con reset el día 1** — votado en el canal 6 a 0. Lo único cerrado por el grupo.
- **Modelo de participación** (`briefs/reglas-temporadas.md`): el día no jugado se imputa como
  `min(max(dificultad_del_día, tu_media) + 0,5 , 7)`. El `max` cierra el agujero por el que faltar podía
  mejorar la media (9 casos en el histórico). Sustituye al umbral mínimo, a la penalización separada y a
  la regla de "lo avanzado del mes". Cambia el campeón en 6 de 8 meses, y en 5 de ellos el campeón actual
  jugó menos de la mitad de los días.
- **Figuras**: cuatro categorías, sin "ambiguo" — 🦜 loro, 🌷 flor, 📐 escuadra, 💩 caca. Reparto con el
  clasificador actual: 69/12/11/8%. El ranking de belleza ordena por figuras reconocibles; la caca se
  registra pero no suma ahí.
- **Medallas**: siete implementadas (Suertud@, El día imposible, Superviviente, Pleno, Verdugo, Impecable,
  Fondista) con umbrales calibrados sobre 123 pares jugador-mes. Cinco de figuras pendientes de
  calibración. **Se calculan, no se almacenan.** El resumen anuncia solo lo ganado ese día: el estado
  acumulado repetía diez nombres veinte días seguidos.
- La propuesta original de "más de 10 figuras en un mes" era **imposible**: máximo histórico 6, mediana de
  14 partidas al mes.
- **Fecha que manda: 1 de septiembre de 2026**, cuando el grupo arranca la etapa nueva.

### Convenciones del método

- Specs, slices y documentación en **español**; identificadores y código en **inglés**. Palabras reservadas
  sin traducir (`WHEN`, `THEN`, `## ADDED Requirements`, claves de frontmatter).
- **Nunca** editar `openspec/specs/` fuera del archive (gate `federated-untouched`).
- Tests de escenario con `# @scenarios <slug>` y estado pendiente **por test** con
  `@pytest.mark.skip` — nunca `pytestmark` de módulo (el escáner no lo entiende todavía).
- Durante el Gate 4c, **re-stagear tras cada arreglo real** antes de la siguiente mutación. Incumplirlo
  tres veces en esta sesión costó tres arreglos perdidos.
- El agente **nunca** commitea, mergea ni despliega sin autorización explícita.

## 5 · Resume Prompt

```
Read /Users/andres/Projects/Personal/wordle-stats/context-snapshot-2026-08-04-1709.md first —
it holds the full state of the previous session.

We are on branch `wordle_2` (pushed, `main` untouched). Four change packs are done; the
next one is the hard blocker of the roadmap.

Immediate next step: implement the slice `identidad-canonica-de-jugador`, following
Phase 3-4 of the protocol (`/slice-implement`).

The pack is already written and its 7 scenario tests are red with `skip` markers:
- openspec/changes/feat-identidad-canonica/{proposal.md,tasks.md,runs.yaml,specs/}
- tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

What is missing is tools/canonical_identity.py, with the interface the tests assume:
`canonizar(directorio, tabla, dry_run=False) -> Informe`, where Informe exposes
resueltas, fusionadas, cruzadas, no_resueltas and ya_canonicas.

Follow tasks.md in order. Two steps are not optional:
- Task 1: back up the identity column to ~/wordle-identidad-antes.json (OUTSIDE the repo,
  which is public).
- Task 5.1: the --dry-run rehearsal. Expected figures are ~1235 resolved, 4 merged,
  8 cross-attributed, 0 unresolved. If merged or cross-attributed are NOT 4 and 8, STOP
  and report — a case the analysis did not see would have appeared.

Run all tests with `-B` (.venv/bin/python3 -B -m pytest) and re-stage after every real fix
made during the mutation gate. Do not commit, merge or deploy without asking.

Do not run the real write until I confirm the rehearsal output.
```
