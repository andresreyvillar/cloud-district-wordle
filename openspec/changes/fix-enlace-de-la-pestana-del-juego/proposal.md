# La pestaña del juego lleva al juego

> Slice: `juego-de-la-jornada` (escenario nuevo `la-pestana-lleva-al-juego`).

## Por qué

El dueño avisa: el juego funciona escribiendo la URL, pero **pulsar la pestaña SuperWordleBros lleva a la
portada**. `_rutaInterna` en `v2/js/router.js` no tenía caso para `VISTAS.JUEGO`, caía al `default` y
devolvía `/`. `resolver` sí conocía `/juego`, así que entrar por URL funcionaba.

Se escapó porque todas las pruebas de navegador entraban por URL y ningún test comprobaba adónde apunta cada
pestaña.

## Qué cambia

- `v2/js/router.js`: `case VISTAS.JUEGO: return '/juego';`.
- Un test que recorre todas las pestañas y exige que cada una lleve a su propia vista.

## Verificación

- Unitario: rojo sin el caso y verde con él; al quitar el caso, rojo solo en `la-pestana-lleva-al-juego`.
- Navegador: pulsando la pestaña desde `/`, `/hoy`, `/datos` y `/reglas` se llega a `/2/juego`, el juego
  responde y la pestaña queda activa; al salir a Hoy, no queda ningún lienzo vivo.
