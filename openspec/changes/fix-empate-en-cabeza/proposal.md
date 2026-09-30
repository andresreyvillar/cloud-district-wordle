# Un empate en cabeza se cuenta como empate

> Slices: `archivo-de-temporadas` (modificación) · `podio-de-cierre-de-mes` (modificación).

## Why

Septiembre acaba con Cata y Joel empatados en cabeza (3,64). La tarjeta de la temporada en `/temporadas`
decía «VA GANANDO Cata»: `archivo.js` tomaba **la primera fila** de la clasificación, y con la misma media
publicada eso es el desempate interno —días jugados, nombre—, que ordena la lista pero no separa a nadie. Al
cerrarse el mes habría dicho «CAMPEÓN Cata», y el medallero le habría sumado a ella sola la temporada ganada.

El podio de cierre, que se publica en el canal el día 1 a las 11:00, sí nombraba a los dos, pero con frases
escritas para un campeón solo: «Cata y Joel se lleva el mes».

El dueño: debe constar como empate, y los dos deben mencionarse compartiendo el primer puesto.

## What Changes

- `v2/js/data/archivo.js`: `campeones` y `lideres` con **todos** los del primer puesto; el medallero suma la
  temporada a cada campeón. `campeon` y `lider` se conservan como el primero de cada lista.
- `v2/js/ui/temporadas.js`: `tarjeta` (ahora exportada) dice «EMPATE EN CABEZA» o «CAMPEONES», nombra a
  todos y, cerrada, que comparten el primer puesto.
- `tools/refranero.py`: `PODIO_CAMPEONES`, frases en plural que dicen que comparten el primer puesto.
- `tools/podio.py`: con varios campeones usa esas frases.

## Out of Scope

- La clasificación no cambia: a igual media publicada ya compartían puesto.
- El titular de la vista de temporada ya contaba el empate («van empatados»): sin cambios.
- La ficha de jugador no muestra títulos ganados: sin cambios.

## Impact

Se despliega **el 30 de septiembre**, por separado de `feat-juego-en-la-temporada` y
`feat-resumen-con-podios`: el podio de cierre corre el 1 de octubre a las 11:00 desde `main`.

## Validation Gates

```bash
python3 -m tools.wslice slice validate archivo-de-temporadas
python3 -m tools.wslice slice validate podio-de-cierre-de-mes
python3 -m tools.wslice slice coverage archivo-de-temporadas
python3 -m tools.wslice slice coverage podio-de-cierre-de-mes
python3 -m tools.wslice verify gates --slice archivo-de-temporadas --change-id fix-empate-en-cabeza
python3 -m tools.wslice verify gates --slice podio-de-cierre-de-mes --change-id fix-empate-en-cabeza
```

## Capabilities

| Capability | Requirements |
|---|---|
| `ranking` | un primer puesto compartido tiene varios líderes y varios campeones |
| `dashboard` | la tarjeta presenta el empate como empate |
| `publicacion` | el podio de cierre felicita en plural a quienes comparten el título |
