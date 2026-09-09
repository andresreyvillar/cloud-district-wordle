# 🍑 CULO, una categoría propia para la forma del #1707

## De dónde sale

La jornada #1707 tuvo una particularidad: **8 de los 10 jugadores terminaron con la misma penúltima fila**,
`G.G.G`. La palabra tenía las letras impares fáciles y las pares difíciles, así que el grupo entero convergió
en el mismo esqueleto y ahí se decidió quién la sacaba en 3, en 4 o en 5.

El dueño reconoció la forma y pidió categoría propia:

```
X . G . Y     ⬛⬛🟩⬛⬛     X e Y libres
G . G . G     🟩⬛🟩⬛🟩
G G G G G     🟩🟩🟩🟩🟩
```

## Cuánto sale: cuatro definiciones medidas

La forma se definió cuatro veces, y cada una se midió sobre 1.809 cuadrículas antes de decidir:

| Definición de la fila de arriba | Encajan | Por qué se descartó |
|---|---|---|
| verde central (`X.G.Y`) | 6 | dejaba fuera a quien tiene ahí un amarillo — tres de los diez de la jornada que la originó |
| tres huecos (`G...G`) | 1 | un solo caso en toda la historia |
| solo los extremos verdes | 9 | dejaba fuera a quien abre la silueta por un lado |
| **solo las dos últimas filas** | **25** | la elegida |

Con la definición final, **la forma es de la jornada más que de quien juega**, y eso es deliberado: en el
#1707 se la llevan siete de los diez jugadores, porque la palabra tenía las letras impares fáciles y las pares
difíciles.

De las 25, con el orden elegido las que son espejo se van a geométrico — incluido el caso más puro,
`G.G.G/G.G.G/GGGGG`. Es lo que el dueño anticipó con «la mayoría de culos deben ser a la vez geométricos».

## El orden, y su consecuencia declarada

Decisión del dueño: **espejo, culo, geométrico, loro, flores**.

Poner el culo **detrás del espejo** lo deja en minoría, y es intencionado: el dueño lo anticipó con «la mayoría
de culos deben ser a la vez geométricos». La consecuencia visible es que el culo más puro —`G.G.G/G.G.G/GGGGG`,
el de Joel— **no** es culo, porque es un espejo perfecto.

El reorden mueve además el espejo por delante del loro, y eso cambiaría **57 cuadrículas** del histórico. El
corte de `PRIMERA_JORNADA_DEL_ORDEN_NUEVO` lo evita: medido, **cambia una** —la de Claire, de loro a culo.

## Puntuación

**3 puntos, lo mismo que el geométrico**, por decisión del dueño. Coherente con el razonamiento de arriba: el
culo no es «más difícil» que el geométrico aunque sea más raro, porque los culos difíciles ya se van a
geométrico por el espejo. El que queda es otra forma de la misma dificultad.

## Fixtures que resultaron medir otra cosa

Cuatro aserciones de los tests del álbum escribían la lista de categorías a mano —`{"loro": 1, "flores": 2,
"geometrico": 1, "abstracto": 1}`— y se pusieron en rojo al añadir una clave con valor cero, sin que el
comportamiento hubiera cambiado. Atadas ahora a `VOCABULARIO` y a `FIGURAS`, que son la fuente.

## Qué no hace

- **No reclasifica el histórico**: una cuadrícula cambia, y es de hoy.
- No añade emoji a la web a mano: la tira sale del catálogo publicado y se adapta sola.
