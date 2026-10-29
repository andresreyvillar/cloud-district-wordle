# Tasks — feat-medallas-resumen

Plan para un implementador **sin contexto previo**. Si un paso no verifica, **para** y reporta.

Regla del proyecto: máximo **3 intentos** ante un gate que falla; al tercero, parar y escalar.

⚠️ El riesgo de este pack no es de datos, es **reputacional**: el resultado se publica delante de quince
personas. Un umbral mal calculado se lee en el canal y no se deshace con un revert.

---

## Tarea 0 — Preflight

```bash
git switch -c feat/feat-medallas-resumen
python3 -m tools.wslice slice validate medallas-en-el-resumen-diario
.venv/bin/python3 -B -m pytest -q
```

---

## Tarea 1 — Tests de escenario (Fase 2, TDD rojo)

Archivo: `tests/slices/medallas-en-el-resumen-diario/test_medallas.py`

Ocho escenarios sobre **fixtures de resultados construidos a mano**: nada de producción, nada de Slack.
Los fixtures se escriben con el mínimo de filas que hace verdadera cada condición, para que el test
explique el umbral.

Interfaz que los tests asumen:

```python
from tools.badges import CATALOGO, medallas_de_temporada, medallas_permanentes, texto_de_medallas
```

| Función | Entrada | Salida |
|---|---|---|
| `medallas_de_temporada(resultados, temporada)` | filas + `"AAAA-MM"` | `{jugador: [clave, …]}` |
| `medallas_permanentes(resultados, hasta_wordle=None)` | filas | `{jugador: [clave, …]}` |
| `texto_de_medallas(resultados, temporada, jornada)` | filas + temporada + puzzle del día | el texto de la sección, o `""` si no hay nada |

`temporada` y `jornada` entran **por parámetro**: sin reloj (§10).

**Verificación.**

```bash
.venv/bin/python3 -B -m pytest tests/slices/medallas-en-el-resumen-diario -q
#   esperado: 8 skipped
python3 -m tools.wslice slice coverage medallas-en-el-resumen-diario
#   esperado: 8/8, exit 0
```

---

## Tarea 2 — `tools/badges.py`

**Contexto.** Módulo puro. Los umbrales van en un catálogo declarativo, no repartidos por el código: es
lo que permitirá recalibrarlos sin tocar la lógica.

```python
@dataclass(frozen=True)
class Medalla:
    clave: str; nombre: str; emoji: str; nivel: str; alcance: str
```

Las siete del delta, con sus umbrales:

| clave | alcance | condición |
|---|---|---|
| `suertudo` | permanente | alguna partida con puntuación 1 |
| `dia-imposible` | permanente | puntuación ≤4 en un día de media ≥5,5 |
| `superviviente` | temporada | ≥3 días de media ≥4,5 resueltos en ≤4 |
| `pleno` | temporada | jugó todos los días de la temporada, con ≥10 días |
| `verdugo` | temporada | ≥5 días siendo el mejor del día |
| `impecable` | temporada | ≥10 partidas y ninguna fallada |
| `fondista` | temporada | ≥15 partidas |

La **dificultad de un día** es la media del grupo ese día, y solo cuenta si ese día jugaron **≥5**
personas — el mismo criterio que el modelo de participación, para no tener dos definiciones de "día
difícil" en el mismo proyecto.

**Verificación.** Quitar los `skip` y ejecutar:

```bash
.venv/bin/python3 -B -m pytest tests/slices/medallas-en-el-resumen-diario -q
#   esperado: 8 passed
```

---

## Tarea 3 — Cablear el resumen

`tools/post_ranking.py`: componer el `initial_comment` con la sección de medallas **añadida**, nunca
sustituyendo lo que ya publica. El enlace a la web y la captura se conservan.

Los resultados hay que leerlos de Supabase, paginando (PostgREST devuelve 1000 por página; contar sobre
una sola ya produjo una cifra falsa una vez — `docs/lecciones.md`).

La temporada y la jornada se derivan **en el borde** (el `main` del script), no dentro del cálculo.

**Verificación (sin publicar).**

```bash
python3 -m py_compile tools/badges.py tools/post_ranking.py
.venv/bin/python3 -B -m pytest -q
```

Y el ensayo con datos reales, que imprime el texto **sin subirlo a Slack**:

```bash
set -a; . ./.env; set +a
python3 - <<'PY'
import os, sys; sys.path.insert(0, "tools")
from supabase import create_client
from badges import texto_de_medallas
sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
filas, off = [], 0
while True:
    p = sb.table("wordle_results").select("player_name,wordle_id,score,date").range(off, off+999).execute().data
    if not p: break
    filas += p
    if len(p) < 1000: break
    off += 1000
jornada = max(f["wordle_id"] for f in filas)
print(texto_de_medallas(filas, "2026-08", jornada) or "(sin medallas todavía)")
PY
```

**Leer la salida antes de seguir.** Es exactamente lo que verá el grupo.

---

## Tarea 4 — Gates de la Fase 4

```bash
python3 -m tools.wslice verify slice medallas-en-el-resumen-diario
python3 -m tools.wslice verify gates --slice medallas-en-el-resumen-diario --change-id feat-medallas-resumen
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c — mutación** (`-B`, `git add -A` antes, re-stagear tras cualquier arreglo):

| Mutación | Test que debe caer |
|---|---|
| `>= 15` por `> 15` en Fondista | `umbral-exacto-otorga` |
| quitar la condición de dificultad del día imposible | `dia-imposible-exige-las-dos-condiciones` |
| quitar el filtro de muestra mínima del día | `dia-imposible-exige-las-dos-condiciones` |
| devolver la sección aunque esté vacía | `sin-medallas-no-hay-seccion` |

**Gate 4e — security review**, con un foco distinto al habitual: el cambio publica texto en el canal.
- el texto solo puede contener nombres de jugador y números: comprobar que ningún campo libre llega al
  mensaje;
- ningún dato que no esté ya publicado en la web se añade al canal.

---

## Tarea 5 — Registrar y cerrar

1. Entrada en `runs.yaml` con la salida del ensayo de la tarea 3.
2. `git add -A` y **parar**. El merge es del humano, y aquí el merge significa publicar.

**Commit sugerido:**

```
feat(estadisticas): calibrated badges in the daily summary

- tools/badges.py: seven badges as pure functions, declarative catalogue,
  season and matchday injected (no clock)
- thresholds calibrated against 123 player-months; the original "10 figures
  in a month" was unreachable (historic max is 6)
- post_ranking: badge section added to the message, link and capture kept
- 8 scenario tests over hand-built fixtures
```

## Validación de cierre

```bash
python3 -m tools.wslice slice validate medallas-en-el-resumen-diario
python3 -m tools.wslice slice coverage medallas-en-el-resumen-diario
python3 -m tools.wslice verify slice medallas-en-el-resumen-diario
python3 -m tools.wslice verify gates --slice medallas-en-el-resumen-diario --change-id feat-medallas-resumen
.venv/bin/python3 -B -m pytest -q
git status --short
```
