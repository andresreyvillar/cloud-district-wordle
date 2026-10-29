# La web puede nombrar a un jugador con un apodo

> Slice: `apodos-en-la-web` (nuevo).

## Why

Carrillo está jugando estos días con ChatGPT, y el dueño quiere que la web le llame «C̶a̶r̶r̶i̶l̶l̶o̶ ChatGPT».
Decisiones del dueño: **solo la web**, **tachado Unicode**, **hasta que lo quite**, y también en la etiqueta
del nivel del SuperWordleBros.

## What Changes

- `v2/js/domain/apodos.js` (nuevo): `APODOS`, `nombreVisible`, `etiquetaVisible`, `nivelConApodos`.
- Los diecisiete puntos de pintado de nombres de `v2/js/ui/` envuelven el nombre con `nombreVisible`.
- `v2/js/ui/juego.js`: monta el motor con `nivelConApodos(nivel)`; el motor de Joel no cambia.

## Out of Scope

- Slack, la base de datos, las rutas y la identidad.

## Impact

- Ninguna escritura. Al mergear, la web lo enseña en segundos.

## Validation Gates

```bash
python3 -m tools.wslice slice validate apodos-en-la-web
python3 -m tools.wslice slice coverage apodos-en-la-web
python3 -m tools.wslice verify gates --slice apodos-en-la-web --change-id feat-apodos-en-la-web
node --test tests/
```

## Capabilities

| Capability | Requirements |
|---|---|
| `dashboard` | la web nombra con su apodo a quien lo tiene declarado, sin cambiar su identidad |
