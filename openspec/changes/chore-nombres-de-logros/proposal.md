# Proposal — chore-nombres-de-logros

> **Slice:** [`medallas-en-el-resumen-diario`](../../slices/estadisticas/medallas-en-el-resumen-diario.md)
> (modificación de nombre, no de regla)

## Why

El [diseño de la liga arcade](../../../docs/context/sources/2026-08-05-diseno-liga-arcade.md) trae nombres
propios para los logros, y el brief ya declaraba los nombres como **abiertos a falta de bautizo del grupo**.
Se adoptan los de la maqueta donde mejoran, y **se rechaza uno** porque adoptarlo dejaría dos reglas
distintas con el mismo nombre.

Ninguna regla cambia: los umbrales, los alcances y el cálculo se quedan exactamente como están. Lo único que
cambia es cómo se llama una medalla en el mensaje del canal.

## What Changes

| Antes | Ahora | Motivo |
|---|---|---|
| `pleno` / "Pleno" | `metronomo` / **"Metrónom@"** | El nombre de la maqueta dice mejor qué premia: publicar cada día |
| — | `Abstract@` → **`Fontaner@`** (solo en el brief) | La medalla de figuras no está implementada; se renombra donde vive |

**Rechazado a propósito:** la maqueta llama `Superviviente` a "cerrar el mes sin un solo fallo". Ese nombre
**ya está** en otra regla implementada (resolver en ≤4 tres días de media ≥4,5), así que adoptarlo dejaría
dos medallas distintas llamadas igual. "Mes sin fallo" sigue siendo `Impecable`.

**No adoptado todavía:** `Rajad@` (tres o más ausencias en los días duros). Sería el primer logro
explícitamente negativo y **señala a una persona por no jugar**: eso lo confirma el grupo, no un pack de
renombrado.

- `tools/badges.py` — la clave y el nombre del catálogo, y la constante del mínimo de días.
- El escenario `pleno-solo-exige-los-dias-laborables` pasa a `metronomo-solo-exige-los-dias-laborables`.

## Out of Scope

| Fuera | Disparador |
|---|---|
| Las medallas de figuras | Bloqueadas por la calibración del clasificador |
| `Rajad@` | Confirmación del grupo |
| Los motes y las once estadísticas del diseño | Su propio slice, y varias están bloqueadas por el grupo |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Modifica `medallas-en-el-resumen-diario` (renombra un escenario; 14 escenarios, sin cambio de número) |
| **Capabilities** | `estadisticas` (1 MODIFIED) |
| **Migraciones** | Ninguna. Las medallas son derivadas |
| **Riesgo** | Bajo en datos, **visible en el canal**: la próxima vez que alguien gane esa medalla, el mensaje dirá "Metrónom@" |

## Validation Gates

```bash
python3 -m tools.wslice slice validate medallas-en-el-resumen-diario
python3 -m tools.wslice slice coverage medallas-en-el-resumen-diario
python3 -m tools.wslice verify gates --slice medallas-en-el-resumen-diario --change-id chore-nombres-de-logros
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c (mutación):** no aplica de forma útil. Un renombrado no tiene lógica que mutar; el riesgo es que
quede una referencia al nombre viejo, y eso lo cubre `grep` más la suite.

## Notas de honestidad

**Un renombrado parece gratis y no lo es.** El palmarés de una medalla se calcula, no se guarda, así que
renombrarla reescribe el pasado: quien ganó "Pleno" en febrero ahora ganó "Metrónom@". Nadie lo va a notar
porque nunca se publicó —la rama no está mergeada—, pero conviene decirlo antes de que la costumbre de
renombrar cosas se instale.
