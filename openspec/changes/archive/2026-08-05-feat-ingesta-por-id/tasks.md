# Tasks — feat-ingesta-por-id

Plan para un implementador **sin contexto previo**. Si un paso no verifica, **para** y reporta.

Regla del proyecto: máximo **3 intentos** ante un gate que falla; al tercero, parar y escalar.

⚠️ **Esto es la ingesta.** Si escribe mal, corrompe la tabla cada hora y de forma acumulativa. Y mergear
es desplegar: el primer cron después del merge ya escribe con este código.

⚠️ **Va DESPUÉS de la migración de identidad**, que ya está ejecutada. Al revés, las filas de la ventana de
reprocesado se duplicarían.

---

## Tarea 0 — Preflight

```bash
python3 -m tools.wslice slice validate ingesta-por-id-de-slack
.venv/bin/python3 -B -m pytest -q
```

---

## Tarea 1 — Tests de escenario (Fase 2, TDD rojo)

Archivo: `tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py`

Siete escenarios sobre lotes de líneas construidos a mano y un doble de la tabla. Nada de Slack, nada de
Supabase.

El doble **impone la clave del upsert** `(slack_user_id, wordle_id)`. No es un detalle: un doble más
permisivo que la tabla ya dejó pasar un fallo que reventó una migración en producción
(`docs/lecciones.md`, 2026-08-05).

Interfaz que los tests asumen:

```python
from tools.add_results import ETIQUETAS, CLAVE_DE_CONFLICTO, filas_a_escribir, escribir, nombre_para
from tools.extract_slack import linea_de_mensaje
```

| Función | Entrada | Salida |
|---|---|---|
| `linea_de_mensaje(mensaje, nombres)` | dict de Slack + `{id: nombre}` | la línea `USER_START\|…`, o `None` |
| `filas_a_escribir(lineas)` | las líneas del lote | `(filas, descartadas)` |
| `nombre_para(identificador, nombre_de_slack)` | los dos | el nombre a guardar |
| `escribir(filas, tabla)` | filas + tabla | cuántas se escribieron |

**Verificación.**

```bash
.venv/bin/python3 -B -m pytest tests/slices/ingesta-por-id-de-slack -q
#   esperado: 7 skipped
python3 -m tools.wslice slice coverage ingesta-por-id-de-slack
#   esperado: 7/7, exit 0
```

---

## Tarea 2 — `tools/patterns.py`: un campo más en el encabezado

`USER_START|<identificador>|<nombre>|<hora>|<texto>`. `HEADER_RE` gana un grupo y `BloqueResultado` gana
`nombre`. `usuario` pasa a ser **el identificador**.

Los fixtures de `tests/slices/captura-del-patron/` usan el formato viejo: hay que actualizarlos. **Sus
aserciones no se tocan** — si alguna deja de valer, para y reporta, porque significa que el cambio de
formato altera la captura del patrón y eso es una regresión, no un ajuste.

**Verificación.**

```bash
.venv/bin/python3 -B -m pytest tests/slices/captura-del-patron -q     # sin regresiones
```

---

## Tarea 3 — `tools/extract_slack.py`: emitir el identificador

`linea_de_mensaje(mensaje, nombres)` como función pura, y el `fetch_messages` la usa. Emite el
identificador del campo `user` del mensaje y el nombre del directorio.

Un mensaje sin `user` devuelve `None`: no se emite línea. La identidad no se inventa.

---

## Tarea 4 — `tools/add_results.py`: identidad, nombre y testabilidad

1. `ETIQUETAS` con **exactamente tres** entradas (las de quien muestra un handle). `USER_IDENTITY` y
   `NAME_TO_ID` se eliminan: medido, aplicar el primero por identificador renombraría a seis personas y a
   una con el nombre de otra.
2. `nombre_para(identificador, nombre_de_slack)`: la etiqueta gana; si no hay, el nombre de Slack; si
   tampoco, el identificador (feo, pero no pierde el resultado).
3. `filas_a_escribir(lineas)`: devuelve las filas y las descartadas por no tener autor.
4. **El cliente de Supabase se crea dentro de `main`.** Hoy se crea al importar y llama a `sys.exit(1)` sin
   credenciales, así que el módulo no se puede importar en un test.

**Verificación.** Quitar los `skip` y ejecutar:

```bash
.venv/bin/python3 -B -m pytest tests/slices/ingesta-por-id-de-slack -q    # esperado: 7 passed
.venv/bin/python3 -B -m pytest -q
```

---

## Tarea 5 — Ensayo end-to-end sin escribir

El extractor real contra el canal real, el parseo completo, y la escritura sustituida por un doble que
imprime lo que escribiría.

```bash
set -a; . ./.env; set +a
.venv/bin/python3 -B - <<'PY'
import sys; sys.path.insert(0, "tools")
import extract_slack, add_results
lote = extract_slack.fetch_messages().split("\n")
filas, descartadas = add_results.filas_a_escribir(lote)
print(f"{len(filas)} filas · {len(descartadas)} descartadas")
for f in filas[:10]:
    print(f"  {f['slack_user_id']:14} {f['player_name']:16} #{f['wordle_id']} {f['score']} {f['pattern']}")
malas = [f for f in filas if not str(f["slack_user_id"]).startswith("U")]
print(f"filas con identidad que NO es identificador: {len(malas)}   (debe ser 0)")
PY
```

**Leer la salida antes de seguir.** Cada fila tiene que llevar un identificador en la identidad y un nombre
legible en el nombre. Si aparece una identidad que no empieza por `U`, **parar**.

---

## Tarea 6 — Gates de la Fase 4

```bash
python3 -m tools.wslice verify slice ingesta-por-id-de-slack
python3 -m tools.wslice verify gates --slice ingesta-por-id-de-slack --change-id feat-ingesta-por-id
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c — mutación** (`-B`, `git add -A` antes, **re-stagear tras cualquier arreglo**):

| Mutación | Test que debe caer |
|---|---|
| el encabezado emite el nombre en el campo de la identidad | `resultado-guarda-el-identificador` |
| el nombre de Slack gana a la etiqueta | `etiqueta-acordada-gana-al-handle` |
| un mensaje sin autor se guarda con identidad de relleno | `mensaje-sin-autor-no-inventa-identidad` |
| la clave del upsert pasa a ser solo el puzzle | `reprocesar-la-ventana-no-duplica` |

**Gate 4e — security review:** es la ingesta.
- la identidad solo puede venir del campo `user` del mensaje, nunca del texto;
- un mensaje con `|` en su texto no puede alterar el reparto de campos;
- el `upsert` envía exactamente las columnas declaradas y ninguna más.

---

## Tarea 7 — Registrar y cerrar

1. Entrada en `runs.yaml` con la salida del ensayo de la tarea 5.
2. `git add -A` y **parar**. El merge es del humano, y aquí el merge significa escribir en producción.

**Commit sugerido:**

```
feat(ingesta): identify results by slack user id

- extract_slack emits the author's id and display name in the header
- add_results stores the id as identity and a readable name for the web
- replaces USER_IDENTITY, which applied by id would rename six people
  and label one of them with another person's name
- supabase client moves into main so the module can be imported in tests
```

## Validación de cierre

```bash
python3 -m tools.wslice slice validate ingesta-por-id-de-slack
python3 -m tools.wslice slice coverage ingesta-por-id-de-slack
python3 -m tools.wslice verify gates --slice ingesta-por-id-de-slack --change-id feat-ingesta-por-id
.venv/bin/python3 -B -m pytest -q
git status --short
```
