# Proposal — fix-backfill-por-identificador

> **Slice:** [`backfill-de-patrones`](../../slices/ingesta/backfill-de-patrones.md) (modificación)

## Why

El backfill empareja mensaje y fila **por nombre mostrado**. Tras la migración de identidad la columna
guarda identificadores, así que dejó de encontrar nada: **0 filas rellenadas de 299 sin patrón**, cuando
antes resolvía casi todas.

No es un fallo nuevo: es el acoplamiento que el propio slice documentaba con un `?` ("la resolución de
identidad es la que ya usa la ingesta hoy"). La incógnita se resolvió, y toca actualizarlo.

## What Changes

- **`tools/backfill_patterns.py`** — el canal emite el **identificador** del autor y la tabla se indexa por
  `(puzzle, identificador)`. Desaparece `_mapa_de_autores`: ya no hace falta traducir a nombres, lo que
  además ahorra una llamada a `users.list` por ejecución.
- **Dos funciones puras nuevas**, `entrada_de_mensaje` e `indexar`, porque el fallo vivía exactamente en la
  parte sin tests: los siete escenarios de `rellenar()` son agnósticos del tipo de autor y por eso pasaron
  en verde mientras la ejecución real no encontraba nada.

## Out of Scope

| Fuera | Disparador que lo traería |
|---|---|
| Resolver las filas que sigan sin mensaje | Son resultados publicados en hilos (Fase 4.1), no un problema de emparejamiento |
| Insertar los resultados del canal que no existen como fila | Decisión explícita del slice: solo rellena patrones |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Modifica `backfill-de-patrones` (+1 escenario: 7 → 8) |
| **Capabilities** | `ingesta` (1 MODIFIED) |
| **Archivos modificados** | `tools/backfill_patterns.py`, `tests/slices/backfill-de-patrones/` |
| **Migraciones** | Ninguna. Solo escribe la columna `pattern` de filas que la tienen vacía |
| **Riesgo** | Bajo. Es idempotente, no inserta ni borra, y escribe una sola columna |

## Validation Gates

```bash
python3 -m tools.wslice slice validate backfill-de-patrones
python3 -m tools.wslice verify gates --slice backfill-de-patrones --change-id fix-backfill-por-identificador
python3 -m tools.wslice slice coverage backfill-de-patrones
.venv/bin/python3 -B -m pytest -q
.venv/bin/python3 -B tools/backfill_patterns.py --dry-run     # ensayo obligatorio antes de escribir
```

**Gate 4c (mutación)** aplica: el campo del que sale el autor y la clave del índice.

## Notas de honestidad

**Los siete escenarios existentes no cazaban esto y siguen sin cazarlo.** `rellenar()` recibe el autor por
parámetro y le da igual si es un nombre o un identificador; el acoplamiento estaba en los adaptadores, que
no tenían test. Es el mismo patrón que la lección del 2026-08-05: la parte que habla con el mundo real es la
que menos se prueba y la que rompe. De ahí que este pack añada funciones puras en vez de arreglar el
adaptador en su sitio.
