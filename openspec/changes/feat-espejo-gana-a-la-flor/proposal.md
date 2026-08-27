# El espejo gana a la flor, desde el corte

## Por qué

La cuadrícula más simétrica del histórico llevaba un 🌷. En la jornada #1694:

```
Y...Y      ← dos amarillos en fila limpia: la regla de la flor
GG.GG
GG.GG
GG.GG
GGGGG
```

Cuatro filas de cuerpo, palíndroma fila a fila, etiquetada «flores». El espejo se consultaba **después** de la
flor, así que a esa cuadrícula nunca se le preguntaba si era un espejo. El reorden anterior no lo arregló
porque cambiaba geometría contra loro, y este caso es espejo contra flor: su densidad de verde es 0,70 y el
techo del geométrico está en 0,40.

Ya tenía el **logro** 🪞 desde el cambio anterior, pero la categoría seguía siendo flor.

## Qué cambia, medido

Desde el corte, un espejo reconocible se clasifica como geométrico antes de mirar la flor:

```
cuadrículas que cambian: 1 de 1706
   #1694 Juan (Kokuma)   flores → geometrico
cambios antes del corte: 0
```

**Una sola.** Retroactivo serían 47 y habría que reescribir el álbum de todo el mundo; el corte de
`PRIMERA_JORNADA_DEL_ORDEN_NUEVO` lo evita. En adelante, cualquier espejo reconocible será geométrico.

Efecto conocido: el geométrico vale 3 puntos y la flor 1, así que Juan suma 2 en el álbum de agosto. Es el
premio que va con reconocer el dibujo.

## La incoherencia que esto destapó

Escrito sin umbral, el cambio le quitaba la categoría a **flores legítimas**: el fixture de flor del álbum,
`Y...Y/..Y../GGGGG`, es simétrico de dos filas y pasaba a geométrico. Lo pusieron en rojo los tests del álbum.

Y era una incoherencia de fondo: el logro exige cuerpo ≥ 3 porque un espejo de una o dos filas es simetría por
casualidad, pero la categoría no exigía nada. Las dos reglas discrepaban sobre qué es un espejo.

Arreglado compartiendo **un solo predicado**, `es_espejo_reconocible`, que vive en `figures.py` y del que
`badges.py` tira. Duplicar el umbral es la forma en que este repositorio ya se ha equivocado tres veces.

## Qué no hace

- No toca el histórico: cero cambios antes del corte, así que el álbum de nadie se reescribe hacia atrás.
- No cambia el desempate de la obra del día, que sigue ordenando por rareza de categoría antes que por
  simetría. Con este cambio, eso sí, un espejo pasa a competir como geométrico, que es la categoría más rara.
