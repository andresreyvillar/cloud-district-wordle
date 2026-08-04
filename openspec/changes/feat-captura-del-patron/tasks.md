# Tasks — feat-captura-del-patron

Plan para un implementador **sin contexto previo**. Los bloques son literales. Si un paso no verifica,
**para** y reporta — no improvises.

Regla del proyecto: máximo **3 intentos** ante un gate que falla; al tercero, parar y escalar.

⚠️ **El orden de las tareas 1 y 5 no es negociable.** La columna debe existir en Supabase **antes** de
que el código llegue a `main`: mergear es desplegar y el cron corre desde `main`
([ADR 0003](../../decisions/0003-modelo-de-ramas-y-despliegue.md)). Si el código se adelanta a la
columna, la ingesta falla al escribir y se pierden resultados hasta que se corrija.

---

## Tarea 0 — Preflight

```bash
git switch -c feat/feat-captura-del-patron        # nunca trabajar en main
python3 -m tools.wslice slice validate captura-del-patron
.venv/bin/python3 -B -m pytest -q                 # baseline verde antes de tocar nada
```

Comprobar que la columna **todavía no existe** (si existe, alguien se adelantó: parar y preguntar):

```bash
set -a; . ./.env; set +a
curl -s -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Range: 0-0" "$SUPABASE_URL/rest/v1/wordle_results?select=*" | python3 -c "
import json,sys; print('pattern' in json.load(sys.stdin)[0])"
#   esperado: False
```

---

## Tarea 1 — La columna, a mano y antes del código

**Contexto.** No hay migraciones versionadas (declarado en el proposal). La columna se añade desde el
editor SQL de Supabase. Es aditiva y reversible.

```sql
alter table wordle_results add column pattern text;
```

**Verificación.** Repetir el comando de la tarea 0: ahora debe imprimir `True`.

**Reversión**, si hiciera falta: `alter table wordle_results drop column pattern;`

---

## Tarea 2 — Tests de escenario (Fase 2, TDD rojo)

**Contexto.** Los siete escenarios del slice, cada uno con su anotación `@scenarios`. Se escriben
**antes** de la implementación y arrancan en rojo. Nada de tocar producción: fixtures de texto.

Archivo: `tests/slices/captura-del-patron/test_captura_del_patron.py`

Los tests ejercitan **funciones puras** sobre el texto del mensaje, no el pipeline completo. Eso obliga a
que la implementación extraiga la lógica de parseo a funciones testeables, que es lo que se quiere.

Interfaz que los tests asumen (y que la tarea 3 debe crear):

```python
from tools.patterns import filas_de_cuadricula, normalizar_patron, patrones_por_resultado
```

| Función | Entrada | Salida |
|---|---|---|
| `filas_de_cuadricula(texto)` | el texto de un mensaje | lista de filas normalizadas (`"...YY"`) |
| `normalizar_patron(filas)` | lista de filas | cadena `"...YY/.G.YY/GGGGG"` o `None` si no hay filas |
| `patrones_por_resultado(lineas)` | el lote que llega por stdin | lista de `(resultado, patrón)` en orden |

**Verificación.**

```bash
.venv/bin/python3 -B -m pytest tests/slices/captura-del-patron -q
#   esperado: 7 skipped (o rojo si se quitan los skip antes de implementar)
python3 -m tools.wslice slice coverage captura-del-patron
#   esperado: 7/7 escenarios con test declarado, exit 0
```

---

## Tarea 3 — `tools/patterns.py`: la lógica de extracción

**Contexto.** Módulo nuevo, sin dependencias externas y sin efectos: solo texto → texto. Es lo que hace
posible testear los siete escenarios sin Slack ni Supabase.

Reglas que implementa, todas verificadas contra el canal:

- Celdas: `:large_green_square:` → `G`, `:large_yellow_square:` → `Y`,
  `:black_large_square:` y `:white_large_square:` → `.` (las dos, según el tema de quien publica).
- Una fila es una línea con **exactamente cinco** celdas y nada más. Cuatro celdas, seis, o una celda
  suelta en una frase: no es fila.
- El separador de filas en el patrón almacenado es `/`.
- Un resultado nuevo cierra el bloque de filas del anterior.

**Verificación.** Quitar los `skip` de la tarea 2 y ejecutar:

```bash
.venv/bin/python3 -B -m pytest tests/slices/captura-del-patron -q
#   esperado: 7 passed
```

---

## Tarea 4 — Cablear el pipeline

### 4.1 · `tools/extract_slack.py`

El extractor debe emitir el texto del mensaje de forma que el parser pueda reconstruir el bloque. Hoy
emite `USER_START|<nombre>|<hora>|<texto>` y el texto lleva saltos de línea dentro.

**No cambiar el formato del encabezado**: `add_results.py` lo espera así y cualquier cambio rompe la
ingesta. Lo que hay que garantizar es que las líneas de cuadrícula siguen llegando después de su
encabezado y sin filtrarse.

### 4.2 · `tools/add_results.py`

Al reconocer un resultado, acumular las filas siguientes con `filas_de_cuadricula`, normalizar con
`normalizar_patron`, y añadir `pattern` al `upsert`. El resto del upsert **no se toca**: mismas columnas,
misma clave de conflicto.

**Verificación (sin tocar producción).**

```bash
python3 -m py_compile tools/extract_slack.py tools/add_results.py tools/patterns.py
.venv/bin/python3 -B -m pytest -q          # toda la suite, sin regresiones
```

**Prueba en seco con un lote de fixture** (no escribe en Supabase — usa el fixture de los tests):

```bash
.venv/bin/python3 -B -m pytest tests/slices/captura-del-patron -q -k patrones_por_resultado
```

---

## Tarea 5 — Gates de la Fase 4

```bash
python3 -m tools.wslice verify slice captura-del-patron
python3 -m tools.wslice verify gates --slice captura-del-patron --change-id feat-captura-del-patron
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c — mutación** (mínimo dos mutantes, `-B` obligatorio, `git add -A` antes):

| Mutación | Test que debe caer |
|---|---|
| en `filas_de_cuadricula`, exigir 4 celdas en vez de 5 | `linea-que-no-es-fila-se-ignora` |
| quitar la normalización de `:white_large_square:` | `ausentes-se-normalizan` |

**Gate 4e — security review**: el cambio toca el esquema y un script que corre con la service role key.
Comprobar que no se registra el texto crudo completo del mensaje más allá de lo que ya se guardaba, y que
el patrón no puede contener nada aportado por el usuario fuera del alfabeto `G`, `Y`, `.` y `/`.

---

## Tarea 6 — Registrar el run y cerrar

1. Añadir la entrada de la fase a `runs.yaml` (§11).
2. `git add -A` y **parar**. El merge es del humano.
3. **Después del merge**, comprobar en producción con una lectura (no escritura) que la siguiente
   ejecución del cron guarda patrón:

```bash
set -a; . ./.env; set +a
curl -s -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  -H "Range: 0-4" "$SUPABASE_URL/rest/v1/wordle_results?select=player_name,wordle_id,pattern&order=created_at.desc"
```

**Commit sugerido:**

```
feat(ingesta): persist the emoji grid of each result

- wordle_results gains an optional `pattern` column (additive)
- tools/patterns.py: pure grid extraction and normalisation
- add_results: associate the grid rows with the result that precedes them
- 7 scenario tests over text fixtures
```

## Validación de cierre

```bash
python3 -m tools.wslice slice validate captura-del-patron
python3 -m tools.wslice slice coverage captura-del-patron
python3 -m tools.wslice verify slice captura-del-patron
python3 -m tools.wslice verify gates --slice captura-del-patron --change-id feat-captura-del-patron
.venv/bin/python3 -B -m pytest -q
git status --short
```
