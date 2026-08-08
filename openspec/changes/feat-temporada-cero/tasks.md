# Tasks — feat-temporada-cero

## Tarea 1 — El modelo

`tools/seasons.py`: `INICIO_TEMPORADAS`, `TEMPORADA_CERO`, `temporada_de()` con el límite, `ordinal()` y
`etiqueta()`.

**Ojo con los fixtures existentes:** los que usan `2026-07` como temporada propia dejan de valer, porque
julio pasa a ser parte de la temporada 0. Hay que moverlos a un mes posterior al límite.

## Tarea 2 — El criterio de la temporada 0

`tools/standings.py`: sin imputación cuando la temporada es la 0. La instantánea lo declara.

## Tarea 3 — La regla, explicada

`tools/rules.py`: una regla nueva. Una excepción sin explicar se lee como arbitrariedad.

## Tarea 4 — El router y la vista

`/t/0` tiene que resolver. La vista etiqueta con el número de orden y, en la temporada 0, no pinta la tira
por jornada: 159 casillas no se leen.

## Tarea 5 — Rematerializar

Las nueve instantáneas mensuales anteriores a agosto **hay que borrarlas**: el modelo ya no las reconoce y
la web las mostraría como temporadas fantasma.

```bash
.venv/bin/python3 -B -m pytest -q
node --test tests/v2/
python3 tools/local_stack.py --temporada 0 --temporada 2026-08
```

## Tarea 6 — Gates

**Gate 4c**: el límite, el criterio sin imputar de la temporada 0, y el número de orden.
