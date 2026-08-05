# Tasks — fix-backfill-por-identificador

Si un paso no verifica, **para** y reporta. Máximo **3 intentos** ante un gate que falla.

## Tarea 0 — Preflight

```bash
python3 -m tools.wslice slice validate backfill-de-patrones
.venv/bin/python3 -B -m pytest -q
```

## Tarea 1 — Tests de escenario (Fase 2, TDD rojo)

Archivo: `tests/slices/backfill-de-patrones/test_backfill_de_patrones.py`

Tres tests nuevos sobre las dos funciones puras que este pack introduce:

```python
from tools.backfill_patterns import entrada_de_mensaje, indexar
```

**Verificación.**

```bash
.venv/bin/python3 -B -m pytest tests/slices/backfill-de-patrones -q
python3 -m tools.wslice slice coverage backfill-de-patrones     # esperado: 8/8
```

## Tarea 2 — `tools/backfill_patterns.py`

1. `entrada_de_mensaje(mensaje)`: `{"autor": <identificador>, "texto": …}`, o `None` si no hay autor.
2. `indexar(filas)`: `{(puzzle, identificador): fila}`.
3. `CanalSlack.paginar` usa la primera y **deja de consultar `users.list`**.
4. `TablaSupabase.buscar` usa el índice.

**Verificación.**

```bash
.venv/bin/python3 -B -m pytest -q
.venv/bin/python3 -B -m py_compile tools/backfill_patterns.py
```

## Tarea 3 — Ensayo y ejecución

```bash
set -a; . ./.env; set +a
.venv/bin/python3 -B tools/backfill_patterns.py --dry-run
```

**Esperado:** las no resueltas bajan de 299 a cerca de 0. Si siguen en 299, **parar**: significa que el
emparejamiento sigue mirando el campo equivocado.

Después, la ejecución real:

```bash
.venv/bin/python3 -B tools/backfill_patterns.py
```

## Tarea 4 — Gates

```bash
python3 -m tools.wslice verify gates --slice backfill-de-patrones --change-id fix-backfill-por-identificador
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c — mutación** (`-B`, `git add -A` antes, re-stagear tras cualquier arreglo):

| Mutación | Test que debe caer |
|---|---|
| el autor sale del nombre en vez del identificador | `correspondencia-por-identificador` |
| el índice se construye solo con el puzzle | `correspondencia-por-identificador` |
| un mensaje sin autor entra en el recorrido | `correspondencia-por-identificador` |

## Tarea 5 — Registrar y cerrar

1. Entrada en `runs.yaml` con las cifras del ensayo y de la ejecución.
2. `git add -A` y **parar**.
