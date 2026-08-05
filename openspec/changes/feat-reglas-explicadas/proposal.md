# Proposal — feat-reglas-explicadas

> **Slice:** [`reglas-explicadas`](../../slices/dashboard/reglas-explicadas.md)

## Why

El grupo juega con reglas que no puede leer en ningún sitio. Están repartidas entre un hilo de Slack, dos
conversaciones de diseño y cuatro briefs del repositorio, y eso ya ha tenido consecuencias concretas: la
regla de días laborables se implementó **sin que el canal la votase**, y el modelo de imputación cambia quién
gana en **6 de los 8 meses** del histórico sin que el grupo lo haya visto.

Una clasificación que penaliza ausencias necesita estar explicada, o se lee como arbitrariedad.

## What Changes

- **`tools/rules.py`** (nuevo, puro) — el catálogo de reglas: qué hace cada una, **por qué existe**, su estado
  y sus parámetros. Los parámetros **referencian las constantes del cálculo**, no las copian.
- **`tools/seasons.py`** — la instantánea gana la clave `reglas`, así que viajan con la temporada y una
  cerrada conserva las suyas.
- **`v2/js/ui/reglas.js`** + ruta `/reglas` en el router y en la navegación.

### La decisión de diseño que importa

**Los parámetros no se escriben a mano en ningún sitio.** `MUESTRA_MINIMA_DEL_DIA`, `MINIMO_FONDISTA`,
`MARGEN` y compañía se importan de donde viven, y el catálogo los expone. Un test comprueba que **lo que la
página muestra es lo que el cálculo usa**.

Sin eso, la página miente en cuanto alguien recalibre un umbral — y una página de reglas equivocada es peor
que no tenerla, porque el grupo confía en ella.

### Y la parte incómoda: el estado de cada regla

Cada regla lleva uno de tres estados, y la página los distingue:

| Estado | Qué significa | Cuántas hoy |
|---|---|---|
| `aplicada` | el cálculo la usa ahora mismo | las de temporada y medallas |
| `acordada-sin-aplicar` | decidida pero sin implementar | el modelo de imputación |
| `sin-decidir` | el grupo la tiene sobre la mesa | podios separados, rachas, remontada, figuras |

Y un marcador aparte: **`votada` sí o no**. Hoy solo una regla lo está —las temporadas mensuales, 6-0— y el
resto se acordó en conversación. Decirlo es incómodo y es exactamente lo que el grupo necesita saber.

## Out of Scope

| Fuera | Disparador |
|---|---|
| Votar desde la web | Las reglas se deciden en el canal. La página informa, no es una urna |
| Histórico de cambios de una regla | Exige versionar la instantánea; hoy solo guarda la última |
| Detallar el clasificador de figuras | Sus umbrales no están calibrados |

## Impact

| Dimensión | Detalle |
|---|---|
| **Slices** | Crea `reglas-explicadas` (7 escenarios) |
| **Capabilities** | `dashboard` · `ranking` |
| **Archivos nuevos** | `tools/rules.py`, `v2/js/ui/reglas.js`, `tests/slices/reglas-explicadas/` |
| **Archivos modificados** | `tools/seasons.py`, `v2/js/router.js`, `v2/js/app.js`, `v2/js/ui/shell.js` |
| **Migraciones** | Ninguna: una clave más en la carga útil JSONB, que es para lo que se eligió |
| **Riesgo** | Bajo técnicamente, **alto en percepción**: esta página le dice al grupo que se le están aplicando reglas que no votó. Es el objetivo, no un efecto colateral |

## Validation Gates

```bash
python3 -m tools.wslice slice validate reglas-explicadas
python3 -m tools.wslice verify gates --slice reglas-explicadas --change-id feat-reglas-explicadas
python3 -m tools.wslice slice coverage reglas-explicadas
.venv/bin/python3 -B -m pytest -q
node --test tests/v2/
.venv/bin/python3 -B tools/materialize_seasons.py --todas --dry-run
```

**Gate 4c (mutación):** el estado de una regla y el valor de un parámetro. Mutar un umbral en su constante
debe hacer caer el test de coherencia, que es lo único que impide que la página mienta.

**Gate 4e (security review):** no aplica. Sin superficie nueva y sin datos personales: la página no nombra a
nadie.

## Notas de honestidad

- **Esta página es la que va a provocar la conversación que llevo dos días recomendando.** El grupo va a leer
  que se le aplican dos reglas que no votó. Eso es bueno, pero conviene que alguien lo lleve al canal en
  lugar de que lo descubra solo.
- **El texto de las reglas vive en Python.** Es prosa en un módulo de código, que no es bonito. La
  alternativa —tenerla en el brief y copiarla a la web— reintroduce exactamente el desfase que este slice
  existe para evitar. Se acepta el feo a cambio de que no pueda mentir.
- **Una regla explicada sigue pudiendo ser injusta.** Esta página no valida el modelo de imputación: lo hace
  legible. Que el grupo lo acepte es otra cosa, y sigue pendiente.
