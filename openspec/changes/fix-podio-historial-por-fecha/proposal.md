# El cierre de mes comprueba por fecha y corre del 1 al 3

> Slice: `podio-de-cierre-de-mes` (modificación).

## Why

El 2026-10-07 el podio de septiembre se publicó por segunda vez (el original, el día 1). La comprobación de
duplicados leía cinco páginas de 30 mensajes; con la gente nueva el canal pasó de 17 mensajes al día a 37 y el
original quedó en la posición 153. Es el mismo fallo que en agosto (posición 44 con 30 leídos): contar mensajes
se queda corto cada vez que el grupo crece.

## What Changes

- `tools/post_ranking.py`: `mensajes_recientes` acepta `desde` y lee todo lo publicado desde ese instante
  (`oldest` de Slack), siguiendo el cursor hasta el final.
- `tools/post_podium.py`: `desde_de_la_comprobacion(temporada)` —una semana antes del día 1 del mes nuevo,
  calculada desde la temporada— y la comprobación lee por fecha.
- `.github/workflows/post_podium.yml`: el cron pasa de los días 1-7 a 1-3 (decisión del dueño).

## Out of Scope

- La victoria de la última noche sigue con `PAGINAS_DE_HISTORIA`: busca una publicación de esa misma noche.
- El mensaje duplicado del 7 de octubre no se borra desde aquí.

## Impact

- Toca el pipeline: el siguiente cierre (1 de noviembre) corre con este código. No escribe en Supabase.

## Validation Gates

```bash
python3 -m tools.wslice slice validate podio-de-cierre-de-mes
python3 -m tools.wslice slice coverage podio-de-cierre-de-mes
python3 -m tools.wslice verify gates --slice podio-de-cierre-de-mes --change-id fix-podio-historial-por-fecha
.venv/bin/python3 -B -m pytest tests/slices/podio-de-cierre-de-mes
```

## Capabilities

| Capability | Requirements |
|---|---|
| `publicacion` | la comprobación de duplicados del cierre lee por fecha; el cierre se intenta del 1 al 3 |
