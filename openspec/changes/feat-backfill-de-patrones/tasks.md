# Tasks — feat-backfill-de-patrones

Plan para un implementador **sin contexto previo**. Si un paso no verifica, **para** y reporta.

Regla del proyecto: máximo **3 intentos** ante un gate que falla; al tercero, parar y escalar.

⚠️ **Prerrequisito duro:** `feat-captura-del-patron` mergeado y la columna `pattern` existiendo en
Supabase. Este pack reutiliza `tools/patterns.py` y no tiene sentido sin ella.

⚠️ **Este es el único cambio del proyecto que hace una escritura masiva en producción** (~1500 filas de
personas reales). El ensayo con `--dry-run` de la tarea 4 no es opcional.

---

## Tarea 0 — Preflight

```bash
git switch -c feat/feat-backfill-de-patrones
python3 -m tools.wslice slice validate backfill-de-patrones
.venv/bin/python3 -B -m pytest -q

# la columna debe existir ya
set -a; . ./.env; set +a
curl -s -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Range: 0-0" "$SUPABASE_URL/rest/v1/wordle_results?select=*" | python3 -c "
import json,sys; assert 'pattern' in json.load(sys.stdin)[0], 'falta la columna: implementa antes feat-captura-del-patron'; print('columna pattern OK')"

# anotar el censo de partida — se compara al final
curl -s -D - -o /dev/null -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Prefer: count=exact" -H "Range: 0-0" "$SUPABASE_URL/rest/v1/wordle_results?select=id" | grep -i content-range
```

---

## Tarea 1 — Tests de escenario (Fase 2, TDD rojo)

Archivo: `tests/slices/backfill-de-patrones/test_backfill_de_patrones.py`

Los seis escenarios, sobre **dobles en memoria**: un cliente de canal falso que devuelve páginas
preparadas y una tabla falsa que registra las escrituras. Ningún test toca Slack ni Supabase.

Interfaz que los tests asumen (y que la tarea 2 debe crear):

```python
from tools.backfill_patterns import rellenar, Informe
```

`rellenar(canal, tabla, dry_run=False) -> Informe`, donde `Informe` expone `rellenadas`, `intactas`,
`no_resueltas` y `resultados_sin_registrar`. Las dependencias entran por parámetro — sin clientes
globales — porque es lo que hace testeables los seis escenarios y lo que exige el §10 del protocolo.

**Verificación.**

```bash
.venv/bin/python3 -B -m pytest tests/slices/backfill-de-patrones -q
#   esperado: 6 skipped
python3 -m tools.wslice slice coverage backfill-de-patrones
#   esperado: 6/6 escenarios declarados, exit 0
```

---

## Tarea 2 — `tools/backfill_patterns.py`

**Contexto.** Reutiliza `filas_de_cuadricula` y `normalizar_patron` de `tools/patterns.py`. **No
reimplementar la extracción**: si hubiera dos implementaciones, los patrones antiguos y los nuevos
podrían divergir y el Requirement de `ingesta` que exige lo contrario quedaría en falso.

Estructura:

1. Recorrer el canal paginando con el cursor hasta agotarlo.
2. Por cada mensaje de resultado: número de puzzle + autor → localizar la fila.
3. Si la fila existe y su `pattern` está vacío → escribir. Si ya tiene → contar como intacta.
4. Si no hay fila → contar como resultado sin registrar. **No insertar.**
5. Al final, filas sin patrón que no se hayan visto → no resueltas.
6. `--dry-run` recorre y cuenta **sin escribir**.

**Verificación.** Quitar los `skip` y ejecutar:

```bash
.venv/bin/python3 -B -m pytest tests/slices/backfill-de-patrones -q
#   esperado: 6 passed
```

---

## Tarea 3 — Gates de la Fase 4

```bash
python3 -m tools.wslice verify slice backfill-de-patrones
python3 -m tools.wslice verify gates --slice backfill-de-patrones --change-id feat-backfill-de-patrones
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c — mutación** (`-B`, `git add -A` antes de mutar, re-stagear tras cualquier arreglo):

| Mutación | Test que debe caer |
|---|---|
| escribir siempre, no solo cuando `pattern` está vacío | `no-modifica-filas-con-patron` |
| detenerse tras la primera página del histórico | `recorre-todo-el-historico` |
| insertar la fila cuando no existe | `no-inserta-resultados-nuevos` |

**Gate 4e — security review.** Es el gate serio de este pack:
- la escritura usa la service role key y toca datos de personas identificables;
- comprobar que solo se envía la columna `pattern` en el update, nunca un objeto completo que pudiera
  sobrescribir puntuación o fecha;
- comprobar que el informe no volca texto de mensajes ni nombres a un archivo del repo.

---

## Tarea 4 — Ensayo y ejecución (fuera del pipeline, a mano)

**4.1 · Ensayo obligatorio.**

```bash
python3 tools/backfill_patterns.py --dry-run
```

Leer el informe antes de seguir. Si el número de no resueltas es mayor de lo esperado, **parar**: puede
indicar un fallo de asociación mensaje→fila y no un problema de identidad.

**4.2 · Ejecución real**, solo tras revisar el ensayo y **fuera de la hora en punto** para no competir
con el cron:

```bash
python3 tools/backfill_patterns.py
```

**4.3 · Verificar el censo intacto.** Repetir el conteo de la tarea 0: debe dar exactamente la misma
cifra que antes.

```bash
set -a; . ./.env; set +a
curl -s -D - -o /dev/null -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Prefer: count=exact" -H "Range: 0-0" "$SUPABASE_URL/rest/v1/wordle_results?select=id" | grep -i content-range
```

**4.4 · Muestreo manual.** Elegir tres filas rellenadas y comprobar contra el mensaje del canal que el
patrón corresponde a esa persona y a ese puzzle. Es la única comprobación que detecta un cruce de
identidades, y ningún test la sustituye.

---

## Tarea 5 — Registrar el run y cerrar

1. Entrada en `runs.yaml` (§11) incluyendo las cifras del informe: rellenadas, intactas, no resueltas.
2. `git add -A` y **parar**.

**Commit sugerido:**

```
feat(ingesta): backfill grid patterns from channel history

- tools/backfill_patterns.py: paginated walk, writes only where pattern is empty
- reuses tools/patterns.py so old and new patterns cannot diverge
- reports filled / untouched / unresolved counts; --dry-run rehearsal
- 6 scenario tests over in-memory doubles
```

## Validación de cierre

```bash
python3 -m tools.wslice slice validate backfill-de-patrones
python3 -m tools.wslice slice coverage backfill-de-patrones
python3 -m tools.wslice verify slice backfill-de-patrones
python3 -m tools.wslice verify gates --slice backfill-de-patrones --change-id feat-backfill-de-patrones
.venv/bin/python3 -B -m pytest -q
git status --short
```
