# Wordle Analytics 📊

Estadísticas y ranking del Wordle diario del grupo. Un bot lee los resultados que la gente publica en
el canal de Slack, los guarda en Supabase, los muestra en una web y publica cada día una captura del
ranking en el propio canal.

## Cómo funciona

```
Canal de Slack
   │  bot wordlebot (channels:history, users:read, files:write)
   ▼
tools/extract_slack.py    lee el canal → "USER_START|<nombre>|<hora>|<texto>"
   │
   ▼
tools/add_results.py      parsea "La palabra del día #N X/6" (X → 7)
   │                      la fecha se deriva del número de puzzle, no del timestamp
   ▼
Supabase  wordle_results  upsert idempotente · RLS de solo lectura para la clave pública
   ▲
   │  SELECT paginado desde el navegador
index.html + js/script.js dashboard con Plotly: ranking, estadísticas, evolución, datos
   ▲
tools/post_ranking.py     captura con Playwright → sube la imagen al canal
```

**Automatización** (GitHub Actions, desde `main`):

| Workflow | Cuándo | Qué hace |
|---|---|---|
| `update_stats.yml` | cada hora | extrae del canal y actualiza Supabase |
| `post_ranking.yml` | 17:00 UTC | actualiza y publica la captura del ranking en Slack |

**Despliegue:** Cloudflare Workers assets. Un push a `main` publica la web; `.assetsignore` controla
qué archivos se suben (nada de `tools/`, `openspec/`, `docs/`, `tests/` ni `.env`).

## Puesta en marcha

```bash
# 1 · Credenciales
cp .env.example .env        # SLACK_BOT_TOKEN, SLACK_CHANNEL_ID, SUPABASE_URL,
                            # SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY

# 2 · Entorno de desarrollo
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt

# 3 · Tests
.venv/bin/python3 -B -m pytest

# 4 · La web en local (basta un servidor estático: lee los datos de Supabase)
python3 -m http.server 8000
```

⚠️ Los scripts de `tools/` escriben en la base de datos **de producción**. Los datos son de personas
reales y el repositorio es público: nada de pruebas exploratorias contra la tabla.

## Cómo se desarrolla

Este proyecto usa **desarrollo spec-driven por slices**: un comportamiento observable nuevo se
especifica y se prueba antes de escribirse. La spec es la fuente de verdad; el código es una derivada
demostrada por tests.

- **La constitución del método**: [`openspec/slice-system.md`](openspec/slice-system.md)
- **Los dominios (capabilities)**: [`openspec/README.md`](openspec/README.md)
- **Las decisiones y su porqué**: [`openspec/decisions/`](openspec/decisions/)
- **El diario y las lecciones**: [`docs/`](docs/)

Flujo: `/slice-propose` → `/slice-implement <slug>` → `/slice-audit`.

```bash
python3 -m tools.wslice slice list
python3 -m tools.wslice slice validate [slug]
python3 -m tools.wslice slice coverage <slug>
python3 -m tools.wslice verify slice <slug>
python3 -m tools.wslice verify gates --slice <slug> --change-id <id>
python3 -m tools.wslice metrics
```

**Ramas:** se trabaja en `feat/<change-id>`, nunca en `main`. El merge a `main` **es** el despliegue
(ver [ADR 0003](openspec/decisions/0003-modelo-de-ramas-y-despliegue.md)).

## Nota sobre `data/data.json`

Es el almacén **de la v1**, congelado en 2026-01-30 (251 registros). No alimenta nada: la web lee de
Supabase. Se conserva como histórico hasta que un pack de limpieza decida qué hacer con él.
