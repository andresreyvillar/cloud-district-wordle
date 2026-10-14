# El debate de reglas, en su propia pestaña

> Slice: `debate-de-reglas` (modificación).

## Why

El debate nació como apartado al final de Info y en móvil quedaba a unos 11.000 px del principio. El enlace
`/info#debate-de-reglas` no bajaba hasta él: el navegador salta al ancla al cargar, antes de que la vista exista.
El dueño eligió darle su pestaña.

## What Changes

- `v2/js/router.js`: vista `DEBATE` en `/debate` y `destinoConAncla`, que lleva `/info#debate-de-reglas` a ella.
- `v2/js/ui/shell.js`: pestaña Debate en el menú.
- `v2/js/ui/debate.js`: `pintarPaginaDebate`, con cabecera.
- `v2/js/ui/info.js`: el apartado se queda en un párrafo con enlace a la pestaña.
- `v2/js/app.js`: despacha la vista, redirige el enlace viejo y, al cargar, baja al ancla una vez pintada la vista.
- `supabase/migrations/20261014190000_reword_anti_spoilers_poll.sql`: la votación pregunta por la consecuencia de dar
  una pista; «solo prevención» (que era no hacer nada) pasa a «sancionar solo a quien da la pista».

## Out of Scope

- Quién marca una pista y cómo (posible segunda votación).

## Impact

- Web, y un `update` de datos en `rule_polls` aplicado en producción con el visto bueno del dueño (sin votos emitidos).

## Validation Gates

```bash
python3 -m tools.wslice slice validate debate-de-reglas
python3 -m tools.wslice slice coverage debate-de-reglas
python3 -m tools.wslice verify gates --slice debate-de-reglas --change-id feat-pestana-debate
node --test tests/slices/debate-de-reglas/
```

## Capabilities

| Capability | Requirements |
|---|---|
| `dashboard` | el debate tiene su pestaña y el enlace viejo lleva a ella |
