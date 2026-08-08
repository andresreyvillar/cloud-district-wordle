# OpenSpec — wordle-stats

Convención spec-driven. Todo se redacta en **español**; se mantienen sin traducir las palabras
reservadas del esquema (`WHEN`, `THEN`, `## ADDED Requirements`, claves de frontmatter, identificadores).

- **`slice-system.md`** — LA CONSTITUCIÓN: el protocolo canónico. Leer antes de cualquier slice.
- **`specs/<capability>/spec.md`** — specs consolidadas por dominio (la "verdad" vigente).
- **`slices/<capability>/<slug>.md`** — comportamientos observables end-to-end; se especifican y
  verifican por slice.
- **`changes/<id>/`** + **`archive/`** — ciclo de vida de un cambio (proposal/tasks/runs/deltas → archivado).
- **`decisions/`** — ADRs: las decisiones que condicionan el resto.

Las **capabilities son simplemente los dominios** bajo los que cuelgan specs y slices — no hay
registro central; las specs se van materializando conforme se especifica cada slice.

## Capabilities (inferidas del sistema en producción)

| Capability | Qué posee | Origen en el código actual |
|---|---|---|
| **resultados** | El almacén: esquema de `wordle_results`, unicidad (jugador, wordle), derivación de la fecha desde el ID del puzzle, políticas RLS | tabla Supabase · `ANCHOR_ID`/`ANCHOR_DATE` y el `upsert` de `tools/add_results.py` · `tools/fix_dates.py` |
| **ingesta** | Captura desde Slack: lectura del canal, parseo del mensaje de resultado, ventana de mensajes, idempotencia de la reejecución | `tools/extract_slack.py` · regex `La palabra del día #N X/6` de `tools/add_results.py` · `.github/workflows/update_stats.yml` |
| **identidad** | Quién es un jugador: identificador estable, nombre mostrado, alias y renombres, fusión de duplicados | `USER_IDENTITY` / `NAME_TO_ID` de `tools/add_results.py` · `tools/cleanup_names.py` |
| **estadisticas** | Métricas por jugador: media, distribución 1-6, fallos, % de éxito, participación, rachas | `computeUserStats` de `js/script.js` |
| **ranking** | Clasificaciones y su recorte: orden, mínimos de partidas, podios, temporadas | `renderSummary` / orden de `renderStatsTable` de `js/script.js` |
| **publicacion** | Lo que sale hacia Slack: captura del ranking, texto del mensaje, subida al canal | `tools/post_ranking.py` · `.github/workflows/post_ranking.yml` |
| **dashboard** | La web: pestañas, tablas, gráficos, carga paginada de datos, escapado de HTML | `index.html` · `js/script.js` · `css/styles.css` |

**Notas de alcance:**
- `resultados` es dueña del esquema; `ingesta` solo escribe a través de él. Un cambio de columna es
  un Requirement de `resultados`, no de `ingesta`.
- `temporadas` **no** es capability aparte: es un recorte de `ranking` (mismo dato, distinta ventana).
  Si llega a tener su propio ciclo de vida (crear/cerrar/archivar una temporada), se revisa.
- `identidad` está separada de `ingesta` a propósito: hoy la identidad se resuelve por nombre
  mostrado de Slack y eso produce jugadores duplicados. Es un dominio con invariantes propias.

## Surfaces

| Surface | Qué es | Triggers que admite |
|---|---|---|
| `web` | El dashboard estático publicado por Cloudflare Workers assets | `ui` |
| `pipeline` | Los scripts Python, ejecutados por GitHub Actions o a mano | `cron`, `command` |

`http` y `event` no tienen surface válida todavía (§3 de la constitución).
