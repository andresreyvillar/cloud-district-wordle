# Tasks — feat-identidad-canonica

Plan para un implementador **sin contexto previo**. Si un paso no verifica, **para** y reporta.

Regla del proyecto: máximo **3 intentos** ante un gate que falla; al tercero, parar y escalar.

⚠️ **Este es el cambio de mayor riesgo del proyecto hasta ahora**: reescribe la columna de identidad de
~1235 filas y **elimina 12**. Los pasos 1 (copia de seguridad) y 5.1 (ensayo) no son opcionales.

⚠️ **Va ANTES del slice del extractor.** Si el extractor emitiera identificadores primero, se duplicarían
32 de las 40 filas de la ventana de reprocesado.

---

## Tarea 0 — Preflight

```bash
git switch -c feat/feat-identidad-canonica
python3 -m tools.wslice slice validate identidad-canonica-de-jugador
.venv/bin/python3 -B -m pytest -q
```

---

## Tarea 1 — Copia de seguridad de la columna (obligatoria)

**Contexto.** No hay vuelta atrás fila a fila: hay que poder reconstruir el estado anterior.

```bash
set -a; . ./.env; set +a
python3 - <<'PY'
import json, os
from supabase import create_client
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
filas, off = [], 0
while True:
    p = sb.table("wordle_results").select("id,slack_user_id,player_name,wordle_id,score").range(off, off+999).execute().data
    if not p: break
    filas += p
    if len(p) < 1000: break
    off += 1000
destino = os.path.expanduser("~/wordle-identidad-antes.json")   # FUERA del repo: es público
json.dump(filas, open(destino, "w"), ensure_ascii=False, indent=1)
print(f"{len(filas)} filas guardadas en {destino}")
PY
```

**Verificación.** El archivo existe y tiene tantas entradas como filas la tabla. **No** se commitea: el
repositorio es público y esto es un volcado con nombres de personas.

---

## Tarea 2 — Tests de escenario (Fase 2, TDD rojo)

Archivo: `tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py`

Los siete escenarios sobre dobles en memoria: un directorio falso (nombre → identificador) y una tabla
falsa que registra escrituras y borrados. Ningún test toca Slack ni Supabase.

Interfaz que los tests asumen:

```python
from tools.canonical_identity import canonizar, Informe
```

`canonizar(directorio, tabla, dry_run=False) -> Informe`, con `Informe` exponiendo `resueltas`,
`fusionadas`, `cruzadas`, `no_resueltas` y `ya_canonicas`.

**Verificación.**

```bash
.venv/bin/python3 -B -m pytest tests/slices/identidad-canonica-de-jugador -q
#   esperado: 7 skipped
python3 -m tools.wslice slice coverage identidad-canonica-de-jugador
#   esperado: 7/7, exit 0
```

---

## Tarea 3 — `tools/canonical_identity.py`

**Contexto.** Igual que el backfill: `canonizar()` recibe directorio y tabla por parámetro; los
adaptadores reales van al final y los valida el ensayo.

Orden de decisión por fila, y este orden importa:

1. Si la identidad **ya es un identificador** (`U…`) y el nombre mostrado corresponde a **otra** persona
   → **atribución cruzada**: se elimina.
2. Si la identidad ya es un identificador y concuerda → no se toca (`ya_canonicas`).
3. Si es un nombre y **resuelve** → se escribe el identificador. Si al escribirlo choca con otra fila del
   mismo jugador y puzzle **con la misma puntuación** → se fusiona (queda una).
4. Si es un nombre y **no resuelve** → se deja y se cuenta como no resuelta.

Para el paso 1 hace falta comparar el identificador de la fila con el que resuelve su `player_name`: si el
directorio dice que ese nombre es otra persona, están cruzados. Reutilizar la misma resolución que el
paso 3 — una sola función, no dos.

**Verificación.** Quitar los `skip` y ejecutar:

```bash
.venv/bin/python3 -B -m pytest tests/slices/identidad-canonica-de-jugador -q
#   esperado: 7 passed
```

---

## Tarea 4 — Gates de la Fase 4

```bash
python3 -m tools.wslice verify slice identidad-canonica-de-jugador
python3 -m tools.wslice verify gates --slice identidad-canonica-de-jugador --change-id feat-identidad-canonica
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c — mutación** (`-B`, `git add -A` antes, re-stagear tras cualquier arreglo):

| Mutación | Test que debe caer |
|---|---|
| fusionar sin comprobar que la puntuación coincide | `renombre-se-fusiona` |
| tratar como cruzada una fila cuyo nombre sí concuerda | `id-existente-no-se-toca` |
| escribir el identificador también cuando el nombre no resuelve | `nombre-desconocido-se-declara` |
| ignorar `dry_run` | `ensayo-no-escribe` |

**Gate 4e — security review.** El más serio del proyecto:
- se **eliminan** filas: comprobar que solo se borra por los dos criterios declarados y que el recuento
  los distingue;
- el update envía **solo** `slack_user_id`, nunca un objeto que pudiera pisar puntuación, fecha o nombre;
- el informe no volca nombres a ningún archivo del repo;
- la copia de seguridad de la tarea 1 está fuera del repo.

---

## Tarea 5 — Ensayo y ejecución

**5.1 · Ensayo, y se lee antes de seguir.**

```bash
python3 tools/canonical_identity.py --dry-run
```

Cifras esperadas, con lo medido hoy: **resueltas ~1235 · ya canónicas ~290 · fusionadas 4 · cruzadas 8 ·
no resueltas 0**. Si las fusiones o las cruzadas **no son 4 y 8**, **parar**: aparecería un caso que el
análisis no vio y la especificación no cubre.

**5.2 · Ejecución real**, tras leer el ensayo:

```bash
python3 tools/canonical_identity.py
```

**5.3 · El censo cuadra con lo declarado.**

```sql
-- esperado: 1533 − 4 − 8 = 1521
select count(*) from wordle_results;
-- esperado: 0
select count(*) from wordle_results where slack_user_id not like 'U%';
```

**5.4 · Muestreo manual.** Tres jugadores: comprobar que su número de partidas antes y después solo difiere
por las fusiones declaradas. El jugador renombrado debe pasar a tener una sola identidad.

**5.5 · Volver a lanzar el backfill de patrones**, que ahora debería resolver casi todo:

```bash
python3 tools/backfill_patterns.py --dry-run
#   esperado: las ~305 no resueltas de la ejecución anterior bajan a cerca de 0
```

---

## Tarea 6 — Registrar y cerrar

1. Entrada en `runs.yaml` con las cifras reales del ensayo y de la ejecución.
2. `git add -A` y **parar**.

**Commit sugerido:**

```
feat(identidad): canonical player identity by slack user id

- tools/canonical_identity.py: resolve display names to slack ids,
  merge rename duplicates, drop cross-attributed rows
- census changes only by the two declared causes, both reported
- --dry-run rehearsal required; 7 scenario tests over in-memory doubles

Runs before the extractor change: emitting ids first would duplicate
32 of the last 40 rows through the reprocessing window.
```

## Validación de cierre

```bash
python3 -m tools.wslice slice validate identidad-canonica-de-jugador
python3 -m tools.wslice slice coverage identidad-canonica-de-jugador
python3 -m tools.wslice verify slice identidad-canonica-de-jugador
python3 -m tools.wslice verify gates --slice identidad-canonica-de-jugador --change-id feat-identidad-canonica
.venv/bin/python3 -B -m pytest -q
git status --short
```
