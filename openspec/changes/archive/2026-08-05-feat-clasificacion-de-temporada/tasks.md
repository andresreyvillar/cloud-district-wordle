# Tasks — feat-clasificacion-de-temporada

## Tarea 1 — Tests de escenario (TDD rojo)

`tests/slices/clasificacion-de-temporada/test_clasificacion.py`, sobre fixtures a mano.

```bash
.venv/bin/python3 -B -m pytest tests/slices/clasificacion-de-temporada -q
python3 -m tools.wslice slice coverage clasificacion-de-temporada
```

## Tarea 2 — `tools/standings.py`

`clasificacion(resultados, temporada)` y `dificultad_por_dia(...)`. Puros, sin reloj.

El orden: media imputada ascendente, y a igualdad **más días jugados** delante; luego el nombre, para que
sea determinista.

## Tarea 3 — La instantánea

`instantanea()` gana `clasificacion`, `dificultad`, `mas_dificil`, `mas_facil`, `media_grupo` y totales.

## Tarea 4 — La vista con el diseño de la liga arcade

`v2/js/ui/temporada.js` y sus estilos: paleta de puntuación, Poppins/DM Mono/Silkscreen, HUD, titular,
podio, MARCADOR, LOGROS con los iconos SVG, y dificultad por jornada.

## Tarea 5 — Verificación

```bash
node --test tests/v2/
.venv/bin/python3 -B -m pytest -q
python3 tools/local_stack.py --temporada 2026-07
#   y mirar julio en el navegador: 14 jugadores, 23 días
```

## Tarea 6 — Gates y cierre

**Gate 4c — mutación**: quitar el `max` de la imputación, quitar el margen, quitar el tope, invertir el orden.
