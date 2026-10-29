# El podio de cierre se dibuja como el del resumen

> Slice: `podio-de-cierre-de-mes` (modificación).

## Why

Septiembre de 2026 acaba con Cata y Joel empatados en el primer puesto. La lista con medallas del podio de
cierre ponía «🥇 Cata» y debajo «· Joel», como si fueran distintos. El dueño pide el mismo podio ASCII del
resumen diario, con los dos en lo más alto, para el podio que se publica el 1 de octubre.

## What Changes

`tools/podio.py::texto` dibuja el podio con `podios.podio_de_texto`.

## Out of Scope

La felicitación, las medallas del campeón y la despedida no cambian.

## Validation Gates

```bash
python3 -m tools.wslice slice validate podio-de-cierre-de-mes
python3 -m tools.wslice slice coverage podio-de-cierre-de-mes
python3 -m tools.wslice verify gates --slice podio-de-cierre-de-mes --change-id fix-podio-ascii-del-cierre
.venv/bin/python3 -B -m pytest tests/slices/podio-de-cierre-de-mes
```

## Capabilities

| Capability | Requirements |
|---|---|
| `publicacion` | el podio de cierre se dibuja como el del resumen diario |
