# Proposal — feat-backfill-de-patrones

> **Slice:** [`backfill-de-patrones`](../../slices/ingesta/backfill-de-patrones.md)
> **Depende de:** [`feat-captura-del-patron`](../feat-captura-del-patron/proposal.md) — aporta la columna
> `pattern` y las funciones de extracción que este cambio reutiliza. No se implementa antes.

## Why

`captura-del-patron` hace que los resultados nuevos guarden su cuadrícula, pero las **1530 filas ya
registradas** se guardaron sin ella. Sin recuperarlas, el ranking de figuras nace vacío y tarda meses en
tener material suficiente para que un álbum signifique algo.

El canal conserva los mensajes: verificado a 240 días de antigüedad, las cuadrículas siguen accesibles.
El histórico es recuperable, y merece la pena porque el álbum es más divertido con nueve meses de
colección que con una semana.

## What Changes

- **`tools/backfill_patterns.py`** — comando manual que recorre el histórico del canal paginando, extrae
  el patrón con las funciones de `tools/patterns.py` y lo escribe en las filas que lo tienen vacío.
- **Tests de escenario** en `tests/slices/backfill-de-patrones/`.

No cambia el pipeline horario, no cambia el esquema y no cambia la web.

## Out of Scope

| Fuera | Disparador que lo traería |
|---|---|
| Insertar resultados que faltan en la tabla | `resultados-publicados-en-hilos` y `ventana-de-ingesta-robusta`. Son causas distintas y mezclarlas haría el diff irrevisable |
| Corregir la identidad de jugador para localizar más filas | Fase 1 del roadmap. Aquí se usa la resolución que hay hoy, y lo que no se resuelve se declara |
| Recuperar resultados publicados dentro de hilos | Su propio slice: `conversations.history` no los devuelve, así que este comando tampoco los ve |
| Programar el comando en un workflow | Es puntual por diseño. Programarlo competiría con la ingesta horaria por la cuota de lectura |
| Reclasificar o puntuar los patrones recuperados | Slices de clasificación y álbum |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Crea `backfill-de-patrones` |
| **Capabilities** | `ingesta` (3 Requirements) · `resultados` (3 Requirements) |
| **Archivos nuevos** | `tools/backfill_patterns.py`, `tests/slices/backfill-de-patrones/test_backfill_de_patrones.py` |
| **Archivos modificados** | Ninguno |
| **Migraciones** | Ninguna: la columna la trae el pack anterior |
| **Compatibilidad** | Sin ruptura. Escribe una sola columna, y solo donde está vacía |
| **Riesgo** | **Medio-alto.** Es la única pieza de todo el proyecto que hace una escritura masiva sobre datos de producción: ~1500 filas de personas reales. Un error de asociación mensaje→fila pondría el dibujo de alguien en la fila de otro |

### Capabilities

| Capability | Toca | Por qué |
|---|---|---|
| `ingesta` | sí | Recorrer el canal y extraer patrones es comportamiento de captura |
| `resultados` | sí | La invariante de "solo escribe donde falta" y el censo intacto pertenecen al almacén |
| `identidad` | no | Usa la resolución existente sin cambiarla; lo que no resuelve, lo declara |

## Validation Gates

```bash
# 1 · Harness
python3 -m tools.wslice slice validate backfill-de-patrones
python3 -m tools.wslice verify gates --slice backfill-de-patrones --change-id feat-backfill-de-patrones
python3 -m tools.wslice slice coverage backfill-de-patrones

# 2 · Tests
.venv/bin/python3 -B -m pytest tests/slices/backfill-de-patrones -q
.venv/bin/python3 -B -m pytest -q

# 3 · Ensayo obligatorio antes de escribir nada en producción
python3 tools/backfill_patterns.py --dry-run
#    esperado: informe de filas a rellenar / intactas / no resueltas, SIN escrituras

# 4 · Censo idéntico antes y después (se compara el conteo exacto)
#    la cifra de antes se anota antes de ejecutar sin --dry-run
```

**Gate 4c (mutación)** aplica: candidatos son la condición de "solo si el patrón está vacío" y el corte
de la paginación.

**Gate 4e (security review)** aplica y es el más serio de los dos packs: escritura masiva en producción
con la service role key sobre datos de personas identificables.

## Notas de honestidad

- **`--dry-run` no es opcional.** Sin ensayo previo no hay forma de saber cuántas filas se van a tocar ni
  cuántas quedan sin resolver, y la escritura no tiene vuelta atrás fila a fila.
- **La asociación mensaje→fila es por número de puzzle y autor**, y la identidad de autor es precisamente
  lo que está roto en este repo (1234 filas con un nombre en la columna de ID). Se espera un número no
  trivial de filas no resueltas, y **eso es aceptable**: el slice las declara en lugar de adivinar.
- **El comando lee el canal entero.** Consume cuota de la API de Slack; si se ejecuta a la vez que el cron
  horario pueden competir. Ejecutar a mano y fuera de la hora en punto.
