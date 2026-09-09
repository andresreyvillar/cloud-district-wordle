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

## Cuánto sale, medido

**5 de 1.806 cuadrículas (0,28%)** dibujan la forma. Es la categoría más rara del álbum — sale una cada cuatro
meses, más raro incluso que el espejo (1,1%).

Y de esas cinco, con el orden elegido solo **tres** llegan a ser culo:

```
#1434 Carlos          flores      → CULO
#1664 Andrés R.       geometrico  → geometrico   (geométrico por densidad, antes de todo)
#1678 Dani Sanchez    abstracto   → CULO
#1707 Claire          loro        → CULO
#1707 Joel            geometrico  → geometrico   (espejo, y el espejo va antes)
```

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
