# Proposal — feat-captura-del-patron

> **Slice:** [`captura-del-patron`](../../slices/ingesta/captura-del-patron.md)

## Why

Cada resultado publicado en el canal trae la cuadrícula de emojis con el camino hasta la solución, y la
ingesta la tira: la fila persiste `raw_text = "La palabra del día #1671 5/6"` y nada más. Verificado
contra producción — ninguna de las 1530 filas tiene el patrón.

Esa cuadrícula es la materia prima del ranking de figuras
([brief](../../../docs/context/briefs/ranking-de-figuras.md)). Sin ella no hay nada que clasificar, y
cada hora que pasa se pierden ~10 patrones más.

Este cambio es deliberadamente estrecho: **deja de tirar el dato**. No clasifica, no puntúa y no muestra
nada. La clasificación depende de una calibración que todavía no existe, y meterla aquí acoplaría un
cambio verificable con uno que hoy no lo es.

## What Changes

- **`wordle_results` gana la columna `pattern`** (texto, opcional): el camino en formato normalizado.
- **`tools/extract_slack.py`** — el extractor debe preservar las líneas de cuadrícula de forma que el
  parser pueda asociarlas a su resultado.
- **`tools/add_results.py`** — al reconocer un resultado, acumula las filas de cuadrícula que lo siguen,
  las normaliza y las escribe en `pattern`.
- **Tests de escenario** en `tests/slices/captura-del-patron/`.

Formato acordado: filas separadas por `/`, celdas `G` / `Y` / `.`. Un resultado en tres intentos queda
como `...YY/.G.YY/GGGGG`.

## Out of Scope

| Fuera | Disparador que lo traería |
|---|---|
| Clasificar el patrón en 🦜 🌷 📐 💩 | `clasificacion-de-figuras`, bloqueado por la calibración con patrones etiquetados |
| Rellenar el histórico ya registrado | [`backfill-de-patrones`](../feat-backfill-de-patrones/proposal.md), su propio pack |
| Mostrar el patrón en la web | Slice de `dashboard` cuando exista la clasificación |
| Capturar resultados publicados dentro de hilos | `resultados-publicados-en-hilos`: es una carencia distinta y anterior a este cambio |
| Validar coherencia entre número de filas y puntuación | Que aparezca un caso real de incoherencia. Hoy el patrón se guarda tal cual llega |
| Arreglar la identidad de jugador (`slack_user_id` con nombres) | Fase 1 del roadmap. Este cambio no la toca ni la empeora |
| Sistema de migraciones versionadas | Pack propio. **Mientras no exista, la columna se añade a mano** (ver Riesgo) |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Crea `captura-del-patron` |
| **Capabilities** | `ingesta` (3 Requirements) · `resultados` (3 Requirements) |
| **Archivos nuevos** | `tests/slices/captura-del-patron/test_captura_del_patron.py` |
| **Archivos modificados** | `tools/extract_slack.py`, `tools/add_results.py` |
| **Migraciones** | **Una**: `alter table wordle_results add column pattern text`. Aditiva y reversible |
| **Compatibilidad** | Sin ruptura. La v1 no conoce la columna; ningún consumidor la lee todavía |
| **Riesgo** | **Medio.** Toca el pipeline que escribe en producción cada hora. Un fallo en el parser podría dejar de registrar resultados, que es peor que no tener patrones |

### Capabilities

| Capability | Toca | Por qué |
|---|---|---|
| `ingesta` | sí | Extraer y normalizar la cuadrícula es comportamiento de la captura |
| `resultados` | sí | La columna nueva y el formato de almacenamiento pertenecen al almacén |
| `identidad` | no | La resolución de jugador no cambia. El patrón se escribe en la fila que la ingesta ya resolvía |
| `publicacion`, `ranking`, `estadisticas`, `dashboard` | no | Nadie consume el patrón todavía |

## Validation Gates

```bash
# 1 · Harness
python3 -m tools.wslice slice validate captura-del-patron
python3 -m tools.wslice verify gates --slice captura-del-patron --change-id feat-captura-del-patron
python3 -m tools.wslice slice coverage captura-del-patron

# 2 · Tests (con -B: obligatorio, §6 Fase 4.1)
.venv/bin/python3 -B -m pytest tests/slices/captura-del-patron -q
.venv/bin/python3 -B -m pytest -q            # sin regresiones en el resto

# 3 · El pipeline sigue en pie sin tocar producción
python3 -m py_compile tools/extract_slack.py tools/add_results.py

# 4 · Verificación en producción DESPUÉS del merge (una sola comprobación de lectura)
#     que las filas nuevas traen patrón y las viejas siguen intactas
```

**Gate 4c (mutación)** aplica: candidatos naturales son el número de celdas exigido por fila (cinco → cuatro)
y la normalización del cuadrado blanco.

**Gate 4e (security review)** aplica: el cambio toca el esquema de la tabla y el script que corre con
`SUPABASE_SERVICE_ROLE_KEY`.

## Notas de honestidad

- **No hay migraciones versionadas en este repo.** La columna se añade a mano en Supabase antes de
  mergear, y eso significa que el orden importa: si el código llega a `main` antes que la columna, la
  ingesta falla al escribir y se pierden resultados durante una hora. `tasks.md` fija el orden.
- **El extractor cambia de formato de salida.** `extract_slack.py` y `add_results.py` están acoplados por
  un formato de texto sin delimitador de fin de mensaje. Tocar uno sin el otro rompe la ingesta, y por eso
  los dos están en el mismo pack pese a que ensancha el diff.
- **La verificación real es en producción.** Los tests usan fixtures; que el patrón llegue bien a la tabla
  solo se comprueba tras el merge, porque no hay entorno de staging (ADR 0003).
