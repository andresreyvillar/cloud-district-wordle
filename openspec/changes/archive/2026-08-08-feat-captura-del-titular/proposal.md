# Proposal — feat-captura-del-titular

> **Slice:** `captura-apunta-a-la-v2` (modificación: qué se fotografía, no a dónde se apunta)

## Why

Lo pidió el dueño: que el mensaje diario lleve también **la imagen del titular y el podio**.

Y encaja con lo que acaba de cambiar: ahora que el texto lleva el marcador y el álbum, fotografiar la vista
entera **dice dos veces lo mismo**. Peor aún, una captura de `.liga` es marcador + logros + álbum +
estadísticas: una tira larguísima que Slack enseña como una miniatura ilegible.

El titular es justo lo que la imagen aporta y el texto no: quién lidera, por cuánta diferencia y las tiras
de los tres del podio, todo de un vistazo.

## What Changes

```
tools/post_ranking.py   el objetivo de la v2 fotografía `.hero` · y falla diciendo qué falta
```

Dos detalles que van juntos:

- **Se espera al mismo selector que se fotografía.** Antes esperaba `.liga .fila` y capturaba `.liga`;
  esperar a uno y capturar otro deja la puerta abierta a fotografiar algo a medio pintar.
- **Un selector que no encaja se declara.** Antes daba `AttributeError: 'NoneType' has no attribute
  'screenshot'`, que no dice ni qué faltaba ni en qué página.

## Verificado tomando la captura de verdad

Contra la web local: **1232 × 530 px, 79 KB**. Apaisada y legible en Slack, frente a la tira vertical de
antes.

## Un mutante que sobrevivió, y el test flojo que destapó

El mutante que quita la guarda del selector inexistente pasaba en verde. El fixture ponía el mismo selector
inexistente en `espera` **y** en `captura`, así que el que fallaba era `wait_for_selector` —cuyo mensaje ya
menciona el selector— y la guarda no se ejercitaba nunca. Rehecho esperando a `body`, que sí existe.

## Impact

- El mensaje diario queda: texto con marcador, figuras y comentarios, más una imagen que aporta lo que el
  texto no puede.
- Solo aplica con `CAPTURA_OBJETIVO=v2`. Mientras el objetivo sea la v1, la captura sigue siendo la de
  siempre.
