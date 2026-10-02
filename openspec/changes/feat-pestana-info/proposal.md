# La pestaña Info sustituye a Reglas

> Slice: `reglas-explicadas` (modificación).

## Why

La pestaña Reglas enseñaba el catálogo entero: reglas aplicadas, acordadas, abiertas, históricas, con marcas de
estado y de votación. Es lo que necesita quien decide las reglas, no quien juega: el dueño pide **una pestaña
Info que explique cómo se juega, qué competiciones hay y qué publica el bot**, con una sección de reglas
**solo con las que se aplican hoy**, «para no liar al personal».

Decisiones del dueño:
- **Las propuestas salen de la web**: siguen en el catálogo (`tools/rules.py`), que es donde se discuten.
- **Info enseña solo las vigentes**: aplicadas y no históricas, sin marcas de estado ni de votación.
- **`/reglas` y `/t/AAAA-MM/reglas` llevan a `/info`**: los enlaces que circulan por el canal no se rompen.

## What Changes

- `v2/js/ui/info.js` (nuevo): `pintarInfo` con cuatro secciones — Cómo se juega, Las competiciones, Lo que
  publica el bot y Reglas vigentes. La explicación **no lleva cifras**: los números solo salen en las reglas,
  que los leen de las constantes del cálculo.
- `v2/js/ui/reglas.js`: `esVigente` y `reglasVigentes`; el eje `juego` («El SuperWordleBros»).
- `v2/js/router.js` · `shell.js` · `app.js`: la vista `INFO`, la pestaña «Info», las rutas viejas resuelven a
  Info y la barra de direcciones se corrige a `/info`. El índice de ejes salta dentro de la página (con el
  `<base href="/2/">`, un `#eje-…` llevaba a la portada; el fallo venía de la pestaña Reglas).
- `tools/rules.py`: el eje `juego` con cinco reglas del SuperWordleBros, y el campo `historica` para las dos
  reglas de la temporada cero.
- `tools/juego.py`: `HORA_DE_CONGELAR`, la misma hora que `v2/js/domain/superbros.js`.

## Out of Scope

- El catálogo no cambia de contenido salvo las reglas del juego: ninguna regla se decide ni se vota aquí.
- La v1 no se toca.

## Impact

- **Las reglas viajan en la instantánea**: hasta la siguiente materialización (cron horario) Info enseña las de
  la instantánea vieja, sin las del juego y con las de la temporada cero (no traen `historica`). Se corrige
  sola en menos de una hora, o con `gh workflow run update_stats.yml`.

## Validation Gates

```bash
python3 -m tools.wslice slice validate reglas-explicadas
python3 -m tools.wslice slice coverage reglas-explicadas
python3 -m tools.wslice verify gates --slice reglas-explicadas --change-id feat-pestana-info
.venv/bin/python3 -B -m pytest tests/slices/reglas-explicadas
node --test tests/
```

## Capabilities

| Capability | Requirements |
|---|---|
| `dashboard` | la pestaña Info explica cómo se juega y enseña solo las reglas vigentes · las rutas viejas llevan a Info |
| `ranking` | las reglas del SuperWordleBros en el catálogo · las reglas históricas se marcan |
