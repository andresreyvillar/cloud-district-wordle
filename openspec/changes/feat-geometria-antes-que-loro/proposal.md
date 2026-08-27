# La geometría se decide antes que el loro, y no hacia atrás

## Por qué

El orden de las reglas del clasificador era loro → geométrico → flor. Decisión del dueño: la geometría se
comprueba **primero** y, si acierta, no se avanza. Una pirámide con un amarillo suelto es un geométrico, no un
loro.

## Qué mueve, medido

Solo se mueven las cuadrículas que cumplen **las dos** reglas a la vez. Sobre las 1.706 con patrón del
histórico serían **42**, todas de loro a geométrico:

```
loro         221 (13,0%)  →  179 (10,5%)
geometrico   123 ( 7,2%)  →  165 ( 9,7%)
flores       805 (47,2%)  →  805 (47,2%)   sin cambios
abstracto    557 (32,6%)  →  557 (32,6%)   sin cambios
```

## No es retroactivo, y eso es el corazón del cambio

Por decisión del dueño, el orden nuevo rige **a partir de hoy** —jornada 1694, inclusive—. Las cuadrículas
anteriores conservan la categoría que tenían cuando se jugaron.

Tiene precedente en el proyecto: la temporada 0 se rige por las reglas que estaban en vigor entonces
(`seasons.dias_de_temporada`). Y el motivo es concreto: el geométrico vale 3 puntos y el loro 2, así que
aplicarlo hacia atrás subiría la puntuación de quien tenga esas 42 partidas **ya jugadas y ya comentadas en
el canal**, reescribiendo un álbum que el grupo ya ha visto.

Verificado contra producción con el corte puesto: **0 cuadrículas cambian de categoría**. Las 42 que se
moverían están todas antes del corte. Nadie pierde ni gana un punto, y **no hay que rematerializar el
histórico**.

## Cómo

`figura(patron, jornada)`. La jornada decide el orden, vía `geometria_primero(jornada)`. Sin jornada se usa el
orden histórico: es lo que quieren las herramientas que clasifican un patrón fuera de contexto, como la
calibración contra el etiquetado humano, que se hizo con las reglas de entonces.

Los cinco llamadores de producción —dos en `album.py` y tres en `resumen.py`— pasan ahora la jornada. Sin eso
el orden nuevo no se aplicaría nunca y el cambio sería decorativo.

## Qué no hace

- **No arregla la cuadrícula que motivó la conversación.** La simétrica de cuatro filas de la jornada #1694
  tiene densidad de verde 0,70 y el techo del geométrico está en 0,40: no es geométrica para el clasificador,
  así que sigue siendo flor. Se avisó antes de implementar.
- No toca la clasificación del espejo ni el desempate de la obra del día.
- No recalcula el histórico: es justo lo que el corte evita.
