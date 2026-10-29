# Proposal — feat-temporada-cero

> **Slice:** [`temporada-mensual`](../../slices/ranking/temporada-mensual.md) (modificación del modelo)

## Why

Decisión del dueño el 2026-08-05: **todo lo jugado hasta el 31 de julio es la temporada 0, y la temporada 1
empieza en agosto**. Las temporadas pasan a estar numeradas desde un límite, no a existir una por cada mes
con datos.

## What Changes

- **`tools/seasons.py`** — un límite (`2026-08`) parte el histórico. Antes del límite, todo es la temporada
  `0`; desde él, un mes es una temporada y lleva su número de orden.
- **`tools/standings.py`** — la temporada 0 se ordena por **media de partidas jugadas, sin imputar**.
- **`tools/rules.py`** — una regla nueva que lo explica, porque es justo el tipo de excepción que sin
  explicar se lee como arbitrariedad.
- **La vista** — etiqueta con el número de orden y, en la temporada 0, sin tira por jornada.

### Por qué la temporada 0 no se imputa

Medido sobre los 159 días válidos anteriores a agosto:

| Jugador | Jugados | Se le imputarían | Se incorporó |
|---|---|---|---|
| Carlos | 148 (93%) | 11 | noviembre |
| Juan (Kokuma) | 85 (53%) | 74 | marzo |
| Dani Sanchez | 35 (22%) | 124 | mayo |
| Sandra | 3 (2%) | **156** | 22 de julio |
| Carmen | 1 | **158** | diciembre |

**Siete de veinte jugadores tendrían más del 70% de la temporada imputada.** Imputar a Sandra 156 ausencias
desde noviembre, cuando entró el 22 de julio, no produce una clasificación sino un artefacto: castiga por no
jugar antes de estar. Y las reglas nuevas no estaban en vigor entonces, así que aplicarlas hacia atrás es
cambiar el resultado de un partido ya jugado.

Se descartó también **imputar solo desde la incorporación de cada uno**: es más justo que imputarlo todo,
pero premia llegar tarde —quien entró en julio competiría sobre 8 días y quien estaba desde noviembre sobre
159— y añade una regla más que explicar.

### El identificador

Los meses conservan `AAAA-MM` y la temporada 0 usa `0`. El **número de orden se deriva** del límite
(`2026-08` → 1, `2026-09` → 2), no se almacena, así que no puede desincronizarse. Se mantiene `AAAA-MM` para
que un enlace pegado en el canal siga diciendo de qué mes habla — la razón por la que el
[ADR 0006](../../decisions/0006-estructura-de-informacion-v2.md) lo eligió.

## Out of Scope

| Fuera | Disparador |
|---|---|
| Los nueve meses como temporadas visitables | Decisión explícita: la temporada 0 es **un bloque**. Consecuencia aceptada: el archivo pierde el "quién ganó en marzo" y los 6 ganadores distintos |
| Coronar un ganador de la temporada 0 | El grupo no ha decidido si la etapa se cierra con premio |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Modifica `temporada-mensual` (+3 escenarios) |
| **Capabilities** | `ranking` |
| **Migraciones** | Ninguna, pero **hay que rematerializar**: las 9 instantáneas mensuales anteriores a agosto dejan de ser temporadas y se sustituyen por una sola |
| **Riesgo** | Medio. Cambia lo que el grupo ve como historia: nueve temporadas con seis ganadores pasan a ser una con uno |

## Validation Gates

```bash
python3 -m tools.wslice slice validate temporada-mensual
python3 -m tools.wslice verify gates --slice temporada-mensual --change-id feat-temporada-cero
.venv/bin/python3 -B -m pytest -q
node --test tests/v2/
python3 tools/local_stack.py --temporada 0 --temporada 2026-08
```

**Gate 4c (mutación):** el límite, el criterio sin imputación de la temporada 0 y el cálculo del número de
orden.

## Notas de honestidad

- **Esto tira contenido a la basura.** El roadmap vendía que la web nacía con nueve temporadas cerradas y
  seis ganadores distintos; ahora nace con una temporada 0 y la 1 en curso. Es la decisión tomada, pero
  conviene decir qué se pierde.
- **Las instantáneas mensuales viejas quedan huérfanas** hasta que se rematerialice. Hay que borrarlas, o la
  web mostraría temporadas que el modelo ya no reconoce.
- **El límite es una fecha escrita en el código.** Si el grupo decidiera que la temporada 1 empieza en
  septiembre, es una constante — pero cambiarla renumera todo, así que conviene que la fecha esté acordada.
