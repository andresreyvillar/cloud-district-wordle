# Proposal — feat-identidad-canonica

> **Slice:** [`identidad-canonica-de-jugador`](../../slices/identidad/identidad-canonica-de-jugador.md)
> **Corrige el orden del roadmap:** la Fase 1 lo tenía como 1.2, después del cambio del extractor. Va
> antes. El motivo está medido en "Why".

## Why

La identidad de un jugador es hoy **el nombre que muestra en Slack**. Medido contra producción: 1235 de
1533 filas guardan un nombre donde debería ir un identificador, y eso ya ha producido tres daños reales:

1. **Un jugador partido en dos.** Dos identidades distintas que resuelven al mismo identificador de Slack,
   con cuatro puzzles registrados dos veces y la misma puntuación en los dos: la misma partida contada
   doble.
2. **Ocho filas con el identificador de otra persona.** Su nombre mostrado dice un jugador y su
   identificador pertenece a otro, con puntuaciones distintas de las de esa otra persona los mismos días.
   Es el residuo de un cruce en el diccionario de mapeos.
3. **El backfill de patrones se quedó al 80%.** Sus 305 filas no resueltas son exactamente este problema:
   298 tienen identificador donde el mensaje trae nombre, y 7 son del jugador renombrado.

Y hay una razón de orden, no de oportunidad: **si el extractor empezara a emitir identificadores antes de
esta migración, las filas de la ventana de reprocesado se duplicarían.** Medido: 32 de las 40 últimas,
11 jugadores. El `upsert` resuelve el conflicto por `(slack_user_id, wordle_id)`, así que una fila nueva
con `U02U5EHPL3A` no colisiona con la vieja que dice `Carlos`.

## What Changes

- **`tools/canonical_identity.py`** — comando manual que resuelve cada nombre mostrado contra el
  directorio del workspace, escribe el identificador, fusiona los duplicados por renombre y elimina las
  atribuciones cruzadas. Con `--dry-run` obligatorio.
- **Tests de escenario** en `tests/slices/identidad-canonica-de-jugador/`.

No toca la ingesta, no toca el esquema y no toca la web.

## Out of Scope

| Fuera | Disparador que lo traería |
|---|---|
| Que el extractor emita el identificador | `ingesta-por-id-de-slack`, el slice siguiente. **Después de este**, nunca antes |
| Retirar el diccionario `USER_IDENTITY` / `NAME_TO_ID` de `add_results.py` | El slice del extractor, que es quien lo deja sin uso |
| Normalizar los nombres mostrados (acentos, abreviaturas) | Nada lo pide: `player_name` es lo que la web muestra y se conserva tal cual |
| Reasignar las filas con atribución cruzada a su dueño probable | Se eliminan, no se reasignan: ver la nota de honestidad |
| Recuperar los patrones que el backfill dejó sin resolver | Volver a ejecutar `backfill-de-patrones` después de esta migración. Es idempotente |
| Un identificador propio del proyecto, independiente de Slack | Que el grupo deje de usar Slack. Hoy sería inventar un problema |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Crea `identidad-canonica-de-jugador`. Estrena la capability `identidad` |
| **Capabilities** | `identidad` (3 Requirements) · `resultados` (3 Requirements) |
| **Archivos nuevos** | `tools/canonical_identity.py`, `tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py` |
| **Archivos modificados** | Ninguno |
| **Migraciones** | Ninguna de esquema. **Sí de datos**: reescribe `slack_user_id` en ~1235 filas, fusiona 4 y elimina 8 |
| **Compatibilidad** | La web v1 no nota nada: `player_name`, `wordle_id`, `score` y `date` no se tocan |
| **Riesgo** | **Alto — el mayor del proyecto hasta ahora.** Reescribe la columna de identidad de 1235 filas y **elimina 12** (4 fusiones + 8 cruzadas). Un error de resolución atribuiría partidas a la persona equivocada, que es exactamente el daño que viene a arreglar |

### Capabilities

| Capability | Toca | Por qué |
|---|---|---|
| `identidad` | sí | Es su primer slice: define qué es un jugador y qué es su nombre |
| `resultados` | sí | El censo de filas cambia, y las invariantes de ese cambio pertenecen al almacén |
| `ingesta` | no | La captura no se toca. Este slice solo canoniza lo ya guardado |
| `ranking`, `estadisticas` | no | Consumen la tabla y se benefician, pero no cambian |

## Validation Gates

```bash
# 1 · Harness
python3 -m tools.wslice slice validate identidad-canonica-de-jugador
python3 -m tools.wslice verify gates --slice identidad-canonica-de-jugador --change-id feat-identidad-canonica
python3 -m tools.wslice slice coverage identidad-canonica-de-jugador

# 2 · Tests
.venv/bin/python3 -B -m pytest tests/slices/identidad-canonica-de-jugador -q
.venv/bin/python3 -B -m pytest -q

# 3 · Ensayo obligatorio, y se LEE antes de seguir
python3 tools/canonical_identity.py --dry-run
#    esperado: resueltas ~1235 · fusionadas 4 · cruzadas 8 · no resueltas 0

# 4 · Censo antes y después: debe cuadrar exactamente con lo declarado
#     filas_después = filas_antes − fusionadas − eliminadas   (1533 − 4 − 8 = 1521)

# 5 · Después de migrar: ninguna fila conserva un nombre como identidad
#     select count(*) from wordle_results where slack_user_id not like 'U%'   → 0
```

**Gate 4c (mutación)** aplica: candidatos son la condición de "ya tiene identificador", el criterio de
fusión (mismo puzzle **y** misma puntuación) y el de atribución cruzada.

**Gate 4e (security review)** aplica y es el más serio del proyecto: reescribe y **elimina** filas de datos
de personas identificables.

## Notas de honestidad

- **Las 8 filas cruzadas se eliminan, no se reasignan.** La decisión es del humano y está tomada con la
  evidencia delante: el jugador que indica su nombre mostrado **ya tiene fila propia** para 6 de los 8
  puzzles, con la misma puntuación en 5. Reasignarlas produciría 6 conflictos contra el índice único y
  seguiría exigiendo elegir cuál se queda. Eliminarlas deja a cada jugador con lo que jugó.
- **Una de esas 8 no cuadra**: en el puzzle 1481 la puntuación difiere de la del jugador que indica el
  nombre (5 frente a 3). Esa fila se elimina igual, y con ello se acepta perder una partida que quizá
  fuera real. Es preferible a atribuirla a alguien por conjetura.
- **La resolución depende del directorio del workspace**, que devuelve el nombre **actual** de cada
  persona. Si alguien se renombra entre el ensayo y la ejecución, el resultado cambia. Ejecutar los dos
  pasos seguidos.
- **No hay vuelta atrás fila a fila.** Antes de la ejecución real hay que exportar la columna de identidad
  actual (`id, slack_user_id`) a un archivo local — no al repo, que es público. Está en `tasks.md`.
