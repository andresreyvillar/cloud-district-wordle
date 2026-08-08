# Proposal — chore-nombres-como-botones

> **Slice:** N/A — cambio de presentación. Ningún enlace lleva a otro sitio ni aparece o desaparece: solo
> cambia cómo se ven. No hay comportamiento observable nuevo que especificar.

## Why

Los nombres del marcador salían con **el estilo por defecto del navegador**: azul y subrayados. La v2 no
tenía ninguna regla para enlaces, así que el azul del sistema se colaba en una paleta que no lo tiene — y
competía por la atención con los colores de puntuación, que son los que tienen que destacar.

Lo pidió el dueño con una condición precisa: **que se vea que son pulsables, pero sin marcarlos como
hipervínculos**.

## What Changes

```
v2/css/styles.css   los nombres pulsables pasan a botón; los enlaces de prosa, a la tinta del sitio
```

Botón: tinta heredada, borde del tablero, píldora. Al pasar por encima, el verde de la liga — el mismo
acento que ya usaban la fila del podio y las tarjetas de `/hoy`.

Alcanza a los cinco sitios donde un nombre es pulsable: marcador, podio, campeón del archivo, título de la
tarjeta de temporada y la lista de ausentes de `/hoy`.

Los enlaces de prosa —«volver al marcador», «sí jugó en…»— **siguen pareciendo enlaces**, porque ahí el
subrayado es la señal correcta; lo que cambia es que van en la tinta del sitio con el subrayado verde, en
lugar del azul del navegador.

## Dos detalles que hicieron falta

- **`justify-self` y `align-self`, las dos.** La primera vale en una rejilla y la segunda en un flex, y
  estos botones viven en los dos sitios. Con solo la primera, el título de la tarjeta de temporada se
  estiraba a todo el ancho de la tarjeta y parecía un campo de texto.
- **El nombre largo se recorta** con puntos suspensivos en el marcador: sin eso, un nombre largo empujaba
  la rejilla y descuadraba las columnas de medias.

Y el **foco de teclado** se declara con un contorno morado: son botones y se recorren con el tabulador.

## Verificación

En navegador, sobre datos reales: marcador, podio, `/temporadas`, `/hoy`, ficha y `/datos`. Sin subrayado,
sin azul, hover verde, el botón no se estira y no hay errores de consola.
