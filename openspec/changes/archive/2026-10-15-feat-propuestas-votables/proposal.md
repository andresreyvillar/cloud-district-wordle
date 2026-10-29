# Las propuestas se publican al momento y se votan

> Slice: `debate-de-reglas` (modificación).

## Why

El primer día llegaron tres propuestas pendientes. El dueño prefirió que se vean todas y que el grupo las vote, en
lugar de aprobarlas una a una.

## What Changes

- `supabase/migrations/20261015090000_public_votable_proposals.sql`: la clave pública lee todas las propuestas
  menos las rechazadas; `rule_proposal_votes` y `votar_propuesta` (a favor o en contra, una por persona y propuesta,
  cambiable; una rechazada no admite votos).
- `v2/js/data/results.js`: lee los votos de propuestas; `DEBATE.votarPropuesta`.
- `v2/js/domain/debate.js`: `apoyos`.
- `v2/js/ui/debate.js` y `v2/css/styles.css`: botones A favor / En contra con recuento y nombres; una propuesta
  enviada aparece al momento.

## Decisiones del dueño

- Se publican sin aprobación. El dueño oculta una marcándola `rechazada`.
- Se votan a favor o en contra, con los nombres a la vista, como la votación.

## Out of Scope

- Convertir una propuesta en regla: lo decide el dueño, con su slice.

## Impact

- Esquema aditivo; la migración se aplica en producción con el visto bueno del dueño. **Las tres propuestas
  pendientes pasan a verse al aplicarla.**

## Validation Gates

```bash
python3 -m tools.wslice slice validate debate-de-reglas
python3 -m tools.wslice slice coverage debate-de-reglas
python3 -m tools.wslice verify gates --slice debate-de-reglas --change-id feat-propuestas-votables
.venv/bin/python3 -B -m pytest tests/slices/debate-de-reglas
node --test tests/slices/debate-de-reglas/
```

## Capabilities

| Capability | Requirements |
|---|---|
| `dashboard` | las propuestas se ven al momento y se votan |
| `resultados` | la clave pública lee las propuestas no rechazadas; los votos de propuestas solo los escribe su función |
