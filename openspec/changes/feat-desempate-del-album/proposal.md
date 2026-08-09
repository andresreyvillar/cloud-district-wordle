# Proposal — feat-desempate-del-album

> **Slice:** `clasificacion-de-figuras` (modificación del desempate)

## Why

Lo reportó el dueño: en el ranking de figuras **no había segundo ni cuarto puesto**. Dos personas en el
primero, dos en el tercero y tres en el sexto.

No era un fallo de cálculo. En agosto hay **cinco jornadas y todo el mundo ha jugado las cinco**, así que
los puntos por partida solo pueden tomar seis valores para ocho jugadores: los empates están forzados por
aritmética. En la temporada 0, con 72 a 149 partidas por persona, **no hay ni uno**.

Y no eran empates de redondeo. Los empatados tenían **colecciones idénticas**:

```
1º  Cata           📐0 🦜1 🌷3 🌀1
1º  Claire         📐0 🦜1 🌷3 🌀1
3º  Dani Sanchez   📐0 🦜0 🌷4 🌀1
3º  Raquel         📐0 🦜0 🌷4 🌀1
6º  Andrés R.      📐0 🦜0 🌷2 🌀3
6º  Carlos H.      📐0 🦜0 🌷2 🌀3
6º  Luis           📐0 🦜0 🌷2 🌀3
```

Ningún criterio sacado del álbum podía separarlos: han hecho exactamente lo mismo.

## De los dos baremos propuestos, uno no se sostiene

El dueño ofreció dos: la puntuación general o el orden de publicación, premiando a quien sube antes.

**El orden de publicación no es medible con los datos que hay.** La única marca de tiempo es la de la
escritura del cron, que trabaja por lotes cada hora. Medido sobre el histórico:

- solo el **34%** de los resultados de una jornada tienen minuto distinto;
- en **8 jornadas** todos comparten el mismo minuto;
- en **ninguna** jornada son todos distintos.

Ordenar por ahí no premiaría a quien publica antes, sino a quien cayó del lado bueno de una hora en punto.
La hora real sí llega de Slack —el extractor la recibe— pero **no se guarda**; sería otro trabajo, con
columna nueva y backfill.

Así que se usa **la puntuación general**, que separa a los siete empatados de agosto.

## Resultado

```
1º Claire  1,00   (marcador 3,80)      5º Clara C     0,60   (5,60)
2º Cata    1,00   (marcador 4,20)      6º Andrés R.   0,40   (3,20)
3º Dani S. 0,80   (marcador 4,20)      7º Luis        0,40   (4,60)
4º Raquel  0,80   (marcador 4,40)      8º Carlos H.   0,40   (4,80)
```

## Precio declarado

Acopla los dos ejes. El álbum existe para premiar a otra gente que el marcador, y ahora el marcador decide
sus empates. Actúa **solo cuando el criterio propio ya no distingue**, y quienes empatan también ahí siguen
compartiendo puesto: el desempate no fabrica diferencias que no existan.

## Un fixture que mentía, corregido de camino

Los tests de medallas construían filas **sin `slack_user_id`**, y producción no tiene ni una así desde la
canonización de identidades. Al pasar el álbum a consultar la tabla de puntuación —que identifica por ese
campo— saltaron. Se ha arreglado el fixture y no el código: un doble más permisivo que la realidad es
exactamente cómo este repositorio se ha equivocado antes.
