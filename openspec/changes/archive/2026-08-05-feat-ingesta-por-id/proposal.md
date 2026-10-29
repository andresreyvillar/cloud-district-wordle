# Proposal — feat-ingesta-por-id

> **Slice:** [`ingesta-por-id-de-slack`](../../slices/ingesta/ingesta-por-id-de-slack.md)

## Why

La migración de identidad dejó las 1524 filas del histórico con el identificador de Slack. **El extractor
sigue emitiendo el nombre mostrado**, así que cada ejecución horaria crea identidades de nombre junto a las
canónicas y vuelve a partir en dos a cada jugador. Es una regresión que empieza a la hora siguiente de la
migración y crece sola.

Sin esto, la migración no sirve de nada más que un día.

## What Changes

- **`tools/extract_slack.py`** — la línea que pasa por tubería lleva el identificador **y** el nombre. El
  extractor ya consulta `users.list`, así que tiene los dos sin coste añadido.
- **`tools/patterns.py`** — el encabezado gana un campo. Es el contrato entre los dos scripts, y los dos
  cambian juntos en la misma ejecución, así que no hace falta ventana de compatibilidad.
- **`tools/extract_slack.py`** (seguridad, en el mismo archivo) — usaba `ssl.CERT_NONE`, que manda el
  token del bot por una conexión sin verificar. Pasa a `certifi`, como ya hacían `backfill_patterns.py` y
  `canonical_identity.py`. No es alcance del slice pero sí del Gate 4e, y el archivo se reescribe entero.
- **`tools/add_results.py`** — la identidad es el identificador; el nombre legible sale del nombre de
  Slack, con etiqueta acordada para quien muestra un handle. Y el cliente de Supabase pasa a crearse
  dentro de `main`: hoy se crea al importar el módulo y llama a `sys.exit(1)` sin credenciales, así que el
  módulo no se puede importar en un test.

### El diccionario `USER_IDENTITY` se sustituye, no se reutiliza

Hoy tiene 11 entradas y **casi nunca se aplica**: la búsqueda es por identificador y el extractor emitía
nombres, así que solo alcanzaba a las tres personas del `NAME_TO_ID` de emergencia. Al resolver por
identificador se aplicaría a todos, y medido contra la tabla **renombraría a seis personas**:

| Identificador | Nombre en la tabla | `USER_IDENTITY` diría |
|---|---|---|
| U02U5EHPL3A | Carlos | Carlos R. |
| U08KF6V12CB | Paula Granado | Paula G. |
| U08BCSARLSZ | Edu Noeda | Edu N. |
| U04JUF2EWLC | Raquel | Raquel L. |
| U09Q60LNVT9 | Quique | Enrique L. |
| **U02TN4L9HEE** | **Claire** | **Raquel** ← es otra persona |

La última es un error de etiquetado heredado: el comentario del propio diccionario dice
"Confirmado Clara/Raquel". Aplicarlo haría que Clara empezase a publicar resultados bajo el nombre de
Raquel.

Lo medido dice cuál es la regla correcta: **para 18 de los 21 jugadores el nombre de Slack ya es
exactamente el nombre guardado**. Solo tres necesitan etiqueta, porque su nombre en Slack es un handle:

| Identificador | Nombre en Slack | Etiqueta acordada |
|---|---|---|
| U08U27DFDL2 | Andres R | Andrés R. |
| U1CKSFSSX | carlos.h | Carlos H. |
| U09G8KLSE4Q | ivan.antona | Iván A. |

## Out of Scope

| Fuera | Disparador que lo traería |
|---|---|
| Reescribir el `player_name` del histórico | No hace falta: 18 de 21 ya coinciden y los otros 3 son etiquetas. Uniformarlo cambiaría lo que muestra la v1 sin ganar nada |
| Resultados publicados en hilos | Fase 4.1. `conversations.history` solo devuelve mensajes raíz y el grupo usa hilos a diario: es un fallo real, con su slice |
| Ampliar la ventana de 50 mensajes | Fase 4.2. Cubre ~5 días; un puente con Actions caído pierde datos |
| Que la web muestre un solo nombre por jugador | La v2.0 lo resolverá del identificador al pintar |
| Reparar `backfill_patterns.py` | Busca la fila por nombre mostrado y la migración lo dejó sin encontrar ninguna. Va en su propio pack, inmediatamente después |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Crea `ingesta-por-id-de-slack` (7 escenarios) |
| **Capabilities** | `ingesta` · `identidad` · `resultados` |
| **Archivos modificados** | `tools/extract_slack.py`, `tools/add_results.py`, `tools/patterns.py`, `tests/slices/captura-del-patron/` (formato del fixture) |
| **Migraciones** | Ninguna |
| **Compatibilidad** | El esquema no cambia. `player_name` sigue recibiendo lo mismo que hoy, así que la v1 no nota nada |
| **Riesgo** | **Alto: es la ingesta.** Si escribe mal, corrompe la tabla cada hora y de forma acumulativa. Y **mergear es desplegar**: el primer cron después del merge ya escribe con este código |

## Validation Gates

```bash
# 1 · Harness
python3 -m tools.wslice slice validate ingesta-por-id-de-slack
python3 -m tools.wslice verify gates --slice ingesta-por-id-de-slack --change-id feat-ingesta-por-id
python3 -m tools.wslice slice coverage ingesta-por-id-de-slack

# 2 · Tests
.venv/bin/python3 -B -m pytest tests/slices/ingesta-por-id-de-slack -q
.venv/bin/python3 -B -m pytest -q          # la suite entera: patterns.py lo usan tres slices

# 3 · Sintaxis
.venv/bin/python3 -B -m py_compile tools/extract_slack.py tools/add_results.py tools/patterns.py

# 4 · Ensayo end-to-end SIN escribir: el extractor real contra el canal real, y el parseo
#     completo, con la escritura sustituida por un doble que imprime lo que escribiría
```

**Gate 4c (mutación)** aplica. Candidatos: el campo del encabezado que lleva la identidad, la precedencia
entre etiqueta y nombre de Slack, y el descarte del mensaje sin autor.

**Gate 4e (security review)** aplica: es la ingesta. Hay que comprobar que el `upsert` no puede escribir una
identidad que no venga del campo de autor de Slack, y que un mensaje con texto arbitrario no puede alterar
el reparto de campos de la línea.

## Notas de honestidad

- **El ensayo no puede cubrir la escritura real.** Se puede parsear el canal de verdad y comprobar qué
  filas saldrían, pero que el `upsert` haga lo correcto solo se demuestra escribiendo. La primera ejecución
  real después del merge es la verificación, y ocurre sobre la tabla de producción.
- **La línea con `|` como separador es frágil y este pack no lo arregla.** Un mensaje que contenga `|` en
  su texto no rompe el parseo actual porque el último campo se toma hasta el final de la línea, pero el
  diseño depende de eso. Queda anotado: si algún día hace falta un campo más, conviene cambiar a JSON por
  línea en lugar de añadir un cuarto separador.
- **`player_name` deja de ser fuente de verdad y pasa a ser una foto.** A partir de aquí el nombre de una
  fila es el que el jugador mostraba el día que jugó. Es correcto para el histórico y confuso para una
  tabla: la v2.0 tiene que resolver el nombre del identificador al pintar, y hasta que lo haga la web
  puede mostrar dos nombres para la misma persona si alguien se renombra.
