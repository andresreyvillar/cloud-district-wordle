# El archivo de temporadas enseña los tres campeones desde octubre

> Slice: `archivo-de-temporadas` (modificación). Depende de `feat-juego-en-la-temporada` (la clave `juego` de
> la instantánea).

## Why

La tarjeta de cada temporada en `/temporadas` solo enseña al campeón del marcador general. Desde octubre hay
**tres competiciones activas** —el marcador, el SuperWordleBros y las figuras— y el dueño quiere ver a los tres
campeones.

Decisiones del dueño:
- **Solo desde octubre de 2026.** Septiembre y las anteriores siguen con el campeón del marcador: el juego
  empezó a mitad de septiembre.
- **El medallero cuenta los títulos por competición**, sin mezclar un título del marcador con uno de belleza.

## What Changes

- `v2/js/data/archivo.js`: `competiciones` por temporada (`marcador`, y desde `2026-10` también `juego` y
  `figuras`), cada una con sus `lideres` y `campeones` —todos los del primer puesto—; el medallero con
  `titulos: { marcador, juego, figuras }`.
- `v2/js/ui/temporadas.js`: la tarjeta pinta un hueco por competición; el medallero, la columna «Títulos» con
  🏆 🎮 🎨 y solo las que tienen algún título.
- `v2/css/styles.css`: los huecos de competición.

## Out of Scope

- La ficha de jugador no enseña títulos.
- Las cifras no se recalculan: salen de la instantánea (ADR 0008).
- Las temporadas anteriores a octubre no cambian.

## Impact

Solo la web. Hasta que exista la temporada de octubre, en producción no se ve ningún cambio salvo el nombre de
la columna del medallero («Títulos»).

## Validation Gates

```bash
python3 -m tools.wslice slice validate archivo-de-temporadas
python3 -m tools.wslice slice coverage archivo-de-temporadas
python3 -m tools.wslice verify gates --slice archivo-de-temporadas --change-id feat-tres-campeones
node --test tests/slices/archivo-de-temporadas/
```

## Capabilities

| Capability | Requirements |
|---|---|
| `ranking` | desde octubre, cada temporada tiene tres campeones · títulos por competición |
| `dashboard` | la tarjeta enseña los tres campeones desde octubre |
