# Proposal — feat-escala-fija

> **Slice:** `escala-fija-comparable` (openspec/slices/dashboard/escala-fija-comparable.md)

## Why

Lo pidió el grupo en el canal, y las dos gráficas que hay lo tenían mal:

- **La dificultad por jornada** se escalaba al máximo del propio mes. Un mes cuya jornada más dura fue un
  4,2 se veía **exactamente igual de dramático** que uno que llegó a 6,0.
- **La distribución de intentos** se escalaba al máximo del propio jugador. Quien jugó 102 partidas y quien
  jugó 1 dibujaban la misma silueta, las dos tocando el techo.

## What Changes

```
v2/js/data/escala.js      PURO: ESCALA_DE_INTENTOS, alturaDeIntentos, escalaDeDistribucion, alturaEnEscala
v2/js/ui/temporada.js     la dificultad usa la escala de intentos
v2/js/ui/jugador.js       la distribución usa la escala de la temporada
v2/js/data/ficha.js       la ficha publica la escala de su temporada
```

Y **la escala se anuncia** en la cabecera de cada gráfico: una escala fija que no se declara es
indistinguible de una automática, así que no arregla la lectura de un vistazo.

## Lo que se ve ahora, con datos reales

| | Antes | Ahora |
|---|---|---|
| Dificultad, temporada 0 | máxima al 100% | **83%** |
| Dificultad, agosto | máxima al 100% | **56%** |
| Distribución de Claire (102 partidas) | máxima al 100% | **70%** |
| Distribución de Javi Calvo (1 partida) | máxima al 100% | **1%** |

## Dos tests que no valían, cazados por la mutación

- El fixture de la distribución ponía el máximo **en el primer jugador**, así que un clasificador que
  mirase solo la primera fila acertaba por casualidad. Movido a la segunda.
- La guarda de escala cero parecía cubierta por un `Number.isFinite`, pero el recorte convertía el infinito
  en 100 —una barra llena a partir de nada— y eso es finito. Ahora se fija el valor, no su finitud.

## Impact

- Cierra el punto 4.4 y **la Fase 4**.
- Es el requisito previo que el roadmap pedía para cualquier animación entre meses.
- La gráfica de evolución de la ficha, cuando llegue, nace con esta escala.
