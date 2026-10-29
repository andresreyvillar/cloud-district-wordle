# Tasks — feat-solo-dias-laborables

Plan para un implementador **sin contexto previo**. Si un paso no verifica, **para** y reporta.

Regla del proyecto: máximo **3 intentos** ante un gate que falla; al tercero, parar y escalar.

⚠️ Este pack **modifica** un slice ya implementado. Los tests existentes van a ponerse rojos, y eso es
correcto: sus fixtures usan fechas que caen en fin de semana. Arreglar la fecha de un fixture es legítimo;
**relajar lo que el test comprueba, no**.

---

## Tarea 0 — Preflight

```bash
git switch -c feat/feat-solo-dias-laborables
python3 -m tools.wslice slice validate medallas-en-el-resumen-diario
.venv/bin/python3 -B -m pytest -q          # verde antes de empezar: 10 escenarios del slice
```

---

## Tarea 1 — Tests de escenario (Fase 2, TDD rojo)

Archivo: `tests/slices/medallas-en-el-resumen-diario/test_medallas.py`

Cuatro escenarios nuevos:

| Escenario | Qué fija |
|---|---|
| `partida-de-fin-de-semana-no-cuenta-para-umbrales` | 15 partidas con una en sábado → **no** hay Fondista |
| `fin-de-semana-no-fija-dificultad` | domingo con 5 jugadores y media 5,8 → **no** hay día imposible |
| `pleno-solo-exige-los-dias-laborables` | todos los laborables jugados, otro jugó un domingo → **sí** hay Pleno |
| `jornada-de-fin-de-semana-no-anuncia-medallas` | jornada en sábado → sección vacía, mensaje intacto |

**Lo primero es arreglar los fixtures existentes.** `dia=(i % 28) + 1` sobre agosto de 2026 mete cinco
fines de semana en quince días (el 1, 2, 8, 9 y 15 son sábado o domingo), así que un fixture de "15
partidas" pasa a tener 10 que cuentan. Hace falta un helper que devuelva el **n-ésimo día laborable** del
mes, y usarlo en todos los fixtures que cuentan partidas:

```python
def dia_laborable(n: int, mes: str = TEMPORADA) -> int:
    """El día del mes correspondiente al n-ésimo laborable (n empieza en 0)."""
```

Agosto de 2026 tiene 21 días laborables y julio 23: hay sitio de sobra para los fixtures de 15 y de 20.

El fixture del día imposible del escenario nuevo **tiene que caer en domingo a propósito**, con muestra
suficiente (5 jugadores) y media exactamente por encima del umbral: si la media quedase por debajo, la
medalla se denegaría por el umbral y el test pasaría sin probar la regla. Es la misma trampa que costó una
ronda en el pack anterior.

**Verificación.**

```bash
.venv/bin/python3 -B -m pytest tests/slices/medallas-en-el-resumen-diario -q
#   esperado: 4 skipped (los nuevos), el resto verde con los fixtures ya corregidos
python3 -m tools.wslice slice coverage medallas-en-el-resumen-diario
#   esperado: 14/14, exit 0
```

---

## Tarea 2 — `tools/calendario.py`

**Contexto.** La única definición de día laborable del proyecto. Módulo propio porque la van a consumir
tres dominios: medallas (ahora), participación y figuras (cuando existan). Un helper privado en `badges.py`
garantizaría una segunda definición divergente, que es exactamente el fallo que el proyecto ya registró con
"día difícil".

```python
def es_laborable(fecha) -> bool
def solo_laborables(resultados: list[dict]) -> list[dict]
```

Requisitos:

- Acepta la fecha como `str` (`"2026-08-04"`, lo que devuelve PostgREST) o como `date`. El campo llega como
  `fila["date"]`, y en el histórico viene en las dos formas según el camino de ingesta.
- Puro y sin reloj: nada de `datetime.now()`. El día de la semana sale de la fecha recibida (§10).
- Una fila con fecha ilegible **no se cuenta como laborable**. Excluir es lo conservador: contarla metería
  una fila de la que no se sabe el día en un cálculo de temporada.

**Verificación.**

```bash
.venv/bin/python3 -B -m py_compile tools/calendario.py
```

---

## Tarea 3 — `tools/badges.py`

Filtrar en las **dos entradas públicas** del cálculo, `medallas_de_temporada` y `medallas_permanentes`.
Filtrar ahí y no en cada recuento es lo que hace que todo lo derivado quede limpio de una vez: la
dificultad del día, el mejor del día, los recuentos de partidas y —el que importa— el conjunto
`dias_de_la_temporada` del que depende `Pleno`.

`medallas_nuevas`, `repeticiones` y `texto_de_medallas` llaman a esas dos, así que no necesitan filtro
propio. **Comprobarlo, no suponerlo**: es justo el sitio donde un filtro a medias sobrevive a los tests.

**Verificación.** Quitar los `skip` y ejecutar:

```bash
.venv/bin/python3 -B -m pytest tests/slices/medallas-en-el-resumen-diario -q
#   esperado: 14 passed
.venv/bin/python3 -B -m pytest -q
```

---

## Tarea 4 — Ensayo con datos reales (sin publicar)

El palmarés **antes y después** de la regla. Es la única forma de comprobar las cifras del proposal, y va
sin tocar Slack.

```bash
set -a; . ./.env; set +a
.venv/bin/python3 -B - <<'PY'
import os, sys; sys.path.insert(0, "tools")
from supabase import create_client
import badges, calendario
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
filas, off = [], 0
while True:
    p = sb.table("wordle_results").select("player_name,wordle_id,score,date").range(off, off+999).execute().data
    if not p: break
    filas += p
    if len(p) < 1000: break
    off += 1000
print(f"{len(filas)} filas, {len(calendario.solo_laborables(filas))} laborables")
temporadas = sorted({str(f["date"])[:7] for f in filas})
for t in temporadas:
    palmares = badges.medallas_de_temporada(filas, t)
    plenos = [j for j, c in palmares.items() if "pleno" in c]
    fondistas = [j for j, c in palmares.items() if "fondista" in c]
    print(f"{t}: pleno={len(plenos)} fondista={len(fondistas)}")
PY
```

**Esperado:** 1533 filas, 1520 laborables. Y en total, **6 plenos** repartidos en 2026-02 (4), 2026-06 (1)
y 2026-07 (1), donde antes había 0. Si sale otra cosa, **parar**: significa que el filtro no está donde
dice el pack.

---

## Tarea 5 — Gates de la Fase 4

```bash
python3 -m tools.wslice verify slice medallas-en-el-resumen-diario
python3 -m tools.wslice verify gates --slice medallas-en-el-resumen-diario --change-id feat-solo-dias-laborables
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c — mutación** (`-B`, `git add -A` antes, **re-stagear tras cualquier arreglo**):

| Mutación | Test que debe caer |
|---|---|
| `isoweekday() <= 5` por `< 5` (el viernes deja de contar) | los fixtures de umbral exacto |
| quitar el filtro de `medallas_de_temporada` | `partida-de-fin-de-semana-no-cuenta-para-umbrales` |
| quitar el filtro de `medallas_permanentes` | `fin-de-semana-no-fija-dificultad` |
| `solo_laborables` devuelve la lista tal cual | `pleno-solo-exige-los-dias-laborables` |

La tercera y la cuarta son las que importan: comprueban que el filtro está en **las dos** entradas y que
`Pleno` mira de verdad los días laborables.

**Gate 4e — security review:** no aplica. Sin superficie nueva, sin credenciales, sin datos nuevos al canal.
El cambio solo quita filas de un cálculo. Anotarlo como `skip` con este motivo en `runs.yaml`.

---

## Tarea 6 — Registrar y cerrar

1. Entrada en `runs.yaml` con la salida del ensayo de la tarea 4.
2. Lección en `docs/lecciones.md`: la cifra del 12% de `Pleno` era falsa (eran 0) porque se midió con una
   definición de "día del mes" distinta de la que implementa el código.
3. `git add -A` y **parar**. El merge es del humano.

**Commit sugerido:**

```
feat(estadisticas): seasons only count weekdays

- tools/calendario.py: single canonical definition of a working day,
  derived from the row's date (no clock)
- badges: filter at both public entry points, so difficulty, best-of-day,
  game counts and the season's day set are all clean
- fixes Pleno, which was unwinnable: one person playing on a Sunday
  blocked it for the whole group (0 of 123 player-months; now 6)
- weekend results keep being captured and stored; only the calculation
  excludes them
```

## Validación de cierre

```bash
python3 -m tools.wslice slice validate medallas-en-el-resumen-diario
python3 -m tools.wslice slice coverage medallas-en-el-resumen-diario
python3 -m tools.wslice verify slice medallas-en-el-resumen-diario
python3 -m tools.wslice verify gates --slice medallas-en-el-resumen-diario --change-id feat-solo-dias-laborables
.venv/bin/python3 -B -m pytest -q
git status --short
```
