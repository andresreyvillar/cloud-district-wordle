# Super Wordle Bros. — el contrato entre la web y el juego

> El juego es de **Joel**. Este documento es lo que la web le entrega y lo que espera de vuelta, para que su
> pull request encaje sin negociación.

## El reparto

La web genera **el nivel**; el juego lo **pinta y lo juega**. Ninguna de las dos piezas necesita saber cómo
funciona la otra por dentro.

Que el nivel lo genere la web y no el juego no es un capricho de reparto: así el nivel se calcula de la
**tabla** y no del canal de Slack, con lo que sale el grupo completo y con los nombres que usa el resto de la
web. El prototipo que lee Slack pierde a quien todavía no había publicado cuando se generó —Cata y Luis el 22
de septiembre, Andrés R. y Claire el 23— y arrastra identificadores de display: `carlos.h` donde la web dice
`Carlos H.`.

## Dónde se engancha

La vista pinta un contenedor y le cuelga el nivel ya calculado. **Es el nivel congelado de la jornada**
(slice `nivel-congelado`): el cron lo genera una vez con `nivelDe`, a partir de las 04:00 del día siguiente,
lo guarda en `game_levels` y no vuelve a cambiar. Todos juegan el mismo escenario y el ranking compara lo
mismo.

```html
<div id="juego-contenedor" class="juego-lienzo" data-nivel='{"widthTiles":101, …}'></div>
```

El motor lo recoge así:

```js
const lienzo = document.getElementById('juego-contenedor');
const nivel = JSON.parse(lienzo.dataset.nivel);
```

El código del juego va en `v2/js/juego/` y lo carga la vista. **No pidas los datos por tu cuenta**: el nivel
ya está ahí, y una segunda consulta sería otra fuente de verdad que se puede desincronizar con la de la
página.

## Cuando alguien termina: avisar a la página

Al llegar a la meta, el motor dispara **un evento** sobre el mismo contenedor:

```js
lienzo.dispatchEvent(new CustomEvent('superbros:fin', {
  detail: { segundos: 83, estrellas: 8 },
}));
```

Eso es todo. La página se encarga del resto: escribe el texto para el canal, pone el botón de copiar y lo
copia al portapapeles. **El total de estrellas no lo mandes**: lo pone la página, que es quien generó los
coleccionables, así que un contador que se pase nunca escribe un `11/10` en el canal.

Lo que sale, para que sepas qué verá el grupo:

```
Super Wordle Bros. #1721 ⏱ 1:23 ⭐ 8/10
🟨🟨🟨🟨🟨🟨🟨🟨⬛⬛
```

**Se pega a mano, igual que el Wordle.** La web no puede publicar en Slack y no debe: el token del bot vive
solo en el workflow y lleva permiso para leer el historial entero del canal. Y así el mensaje lo firma quien
jugó, que es lo que un ranking necesita.

### El mismo evento alimenta el ranking

Debajo del juego hay un ranking por nivel (slice `ranking-del-juego`): cada uno elige quién es y, **en cada
llegada a la meta**, la página manda `segundos` y `estrellas` a la función `registrar_tiempo` de Supabase, que
solo guarda la marca si mejora la anterior. Para ti eso significa tres cosas:

- **Dispara `superbros:fin` en cada partida terminada**, también tras reiniciar con `R`. Hoy lo hace porque
  `create()` vuelve a poner `finished = false`; si cambias el reinicio, que siga siendo así.
- **`segundos` es el tiempo real de la partida, con decimales.** El ranking usa centésimas; no lo redondees.
- **El mínimo de tiempo que acepta la base de datos sale de tu física**: `tramos × 8 casillas × 32 px ÷ (300
  px/s × 1,5)`. Si un PR sube `RUN_SPEED` (o el impulso del pisotón) por encima de **450 px/s**, o cambia
  `TILE` o las columnas por tramo, avísalo: hay que tocar la función o empezará a rechazar tiempos honrados.

## La forma del nivel

**Ojo con cambiarla:** un nivel congelado conserva la forma con la que se congeló. La pestaña solo ofrece el
último, pero el día que entre tu PR ese último se congeló con la forma de antes, así que el motor nuevo tiene
que aceptarla al menos hasta la siguiente congelación.

Es la misma que ya consume tu prototipo — se dedujo de tus dos ficheros y se verificó contra la tabla
reconstruyendo el `pattern` desde los bloques: **idéntico en los 20 jugadores comprobados**.

```jsonc
{
  "widthTiles": 101,        // N jugadores * 8 + 5
  "heightTiles": 8,         // la cuadrícula más alta + 3 de aire
  "blocks": [               // el suelo cubre TODAS las columnas, de 0 a widthTiles-1
    { "col": 0, "row": 0, "type": "ground" },
    { "col": 4, "row": 2, "type": "green" },   // acierto
    { "col": 7, "row": 2, "type": "orange" }   // letra desplazada
  ],
  "labels":       [{ "col": 3, "row": 5, "text": "Ana  3/6" }],
  "collectibles": [{ "col": 4, "row": 3 }],
  "finish":       { "col": 98, "row": 1 }
}
```

Reglas que puedes dar por seguras:

| | |
|---|---|
| Tramo por jugador | 8 columnas; la cuadrícula ocupa las 5 centrales (offsets 3 a 7) |
| Filas | **de abajo arriba**: la fila 1 es el último intento, el que resolvió |
| Orden de los tramos | alfabético por nombre, estable entre ejecuciones |
| Coleccionable | siempre **apoyado sobre una plataforma** de su tramo, nunca en el aire |
| Nota en la etiqueta | `3/6`, y `X/6` cuando no resolvió |
| Jornada | **la anterior a la última**: la de hoy sigue abierta |

Y una garantía que el repositorio comprueba con tests: **la misma jornada da siempre el mismo nivel**. Nada
en la generación depende del reloj ni del azar. Si tu juego necesita aleatoriedad —confeti, variaciones—,
que viva en el juego, no en el nivel.

## ⚠️ Problema conocido: hay niveles que no se pueden terminar

Con la física del motor, el salto máximo es `v² / 2g = 520² / (2 × 1200) = 112 px`, **3,52 bloques**: se
sube un escalón de 3 y no uno de 4. Pero una cuadrícula puede tener una columna de hasta 6 bloques, y como las
cuadrículas son sólidas, un escalón de 4 es una pared.

Medido sobre las últimas 30 jornadas, **al menos 5 niveles tienen un tramo imposible**, y la cuenta es
optimista (supone que se llega a cada tramo desde lo más alto del anterior). El nivel de la jornada 1722 es uno
de ellos: el 6/6 de Andrés R. levanta una pared de 4 bloques. Tus dos prototipos del 22 y el 23 de septiembre
tuvieron suerte —peor escalón de 2 y 3—, y por eso no se veía.

No es un fallo del generador: las reglas del nivel son las tuyas, reproducidas exactamente. Es que **una
cuadrícula es un muro**. Opciones, todas en el motor:

| Opción | Siempre se puede terminar | Qué cambia |
|---|---|---|
| **Doble salto** | sí (llega a ~7 bloques) | mantiene las cuadrículas sólidas y el reto |
| Salto más alto | sí, si llega a 6 | un número; el salto se vuelve flotante |
| Cuadrículas atravesables | sí | el nivel se cruza andando por el suelo: sin reto |

La decisión es tuya. El generador **no** debería meter escalones de ayuda: dejaría de ser el diorama del día.

### Mientras tanto: el pisotón (propuesta, no tuya)

Para que el nivel del 24 de septiembre se pudiera terminar, el dueño pidió un combo de rebote, y está metido en
`v2/js/juego/motor.js` marcado como `ADAPTACIÓN 4 · PROPUESTA`. Quédatelo, cámbialo o tíralo en tu PR:

- En el aire, **↓** o **S**: caída en picado, una vez por salto.
- Al tocar suelo, **Espacio** dentro de `PISOTON_VENTANA` (0,1 s): el rebote sube `PISOTON_CASILLAS` (5)
  desde donde se pisa, con un destello del personaje y chispas en el suelo (`celebrarRebote`).
- **El rebote sale hacia delante**, a velocidad de carrera (`impulsoDelRebote()`): hacia donde se pulsa o, si
  no se pulsa nada, hacia donde mira el personaje.
- `REBOTE_VELOCITY` no está escrita a mano: sale de `velocidadParaAltura()` con tu gravedad, así que si la
  cambias sigue subiendo 5.

El impulso existe porque el pisotón deja caer en vertical, así que sin él se salía del rebote parado en
horizontal y había que acelerar en el aire: la parte de Luis solo se pasaba pulsando →, Shift y Espacio en la
misma décima de segundo. Con él basta con ir corriendo, y la dirección puede llegar hasta 0,3 s tarde. **Sin
Shift sigue sin llegar**, porque tu motor limita la velocidad al paso si no se corre; ese es el reto que
queda.

El dueño empezó con +1 casilla y lo subió a 5 porque la parte de Luis no salía. Comprobado en tu motor:

| Caso | Resultado |
|---|---|
| Muro de 4 desde el suelo | salto normal no pasa; pisotón sí |
| Muro de 5 desde el suelo | pasa, subiendo 5,16 — **con cinco píxeles de margen** |
| Parte de Luis (jornada 1722), rebotando en la columna 6 o 7 de Juan | pasa |

**Dos cosas que quedan en tu tejado.** Una pared de **6** no se pasa desde el suelo —17 de 221 jornadas la
tienen—; solo desde lo alto del tramo anterior. Y esos cinco píxeles del muro de 5 salen de cómo integra tu
motor la física en cada fotograma, que depende de la duración del fotograma: en una pantalla de 144 Hz el
salto se acerca más a las 5,00 exactas y podría no pasar. Si quieres el mismo resultado en todas las
pantallas, o 5,25 casillas o física con paso fijo.

Nota sobre los números: una primera versión de este análisis contaba la altura máxima de cada columna y
trataba como muro los bloques que flotan sobre un hueco. Exageraba. Los de esta página cuentan solo paredes
sólidas, apiladas desde el suelo.

### El tutorial del pisotón

Justo antes del primer muro que tu salto normal no sube, el motor dispara un segundo evento sobre el lienzo:

```js
lienzo.dispatchEvent(new CustomEvent('superbros:pista-pisoton', { detail: { col } }));
```

La página pausa la escena `main`, enseña un GIF con los pasos y la reanuda al cerrarlo. Sale una vez por
navegador (`localStorage`), y la guía tiene un enlace para verlo otra vez. El sitio lo calcula el motor con
**tu** física (`primerMuroQueNecesitaPisoton`), así que si cambias el salto el aviso sigue saliendo delante
del muro correcto. Si cambias el nombre de la escena, la pausa deja de funcionar: está atada a `"main"`.

El GIF (`v2/assets/juego/pisoton.gif`, 38 KB) está **grabado de tu motor** con Playwright, no dibujado: si
cambias el pisotón, hay que volver a grabarlo o enseñará algo que ya no pasa.

### El teclado dentro de la web (adaptación 2, ampliada)

Tu prototipo era una página entera y podía escuchar el teclado en toda la ventana. Dentro de la web eso da tres
problemas, y los tres estaban pasando:

- **El motor escucha el teclado en el lienzo** (`input.keyboard.target`), no en la ventana: sin foco, el
  personaje no se mueve y las flechas mueven la página. Un clic en el juego le devuelve el foco.
- **La rueda no se la queda el motor** (`input.mouse.preventDefaultWheel: false`): por defecto Phaser la
  bloquea y con el puntero encima del juego no se podía bajar la página.
- **Phaser no bloquea el scroll de sus teclas cuando va pulsado Shift**, y Shift + Espacio sube la página. Como
  el pisotón se hace corriendo, la página saltaba justo al rebotar. Lo bloquea la página, **en el padre del
  lienzo**: en el lienzo mismo le quitaba las teclas a tu motor, que descarta las que le llegan bloqueadas.

Si en tu PR cambias cómo escucha el teclado, estas tres cosas tienen que seguir cumpliéndose.

Un detalle que afecta al combo: tu motor detecta las teclas con `JustDown`, que Phaser borra al soltar la
tecla. Un toque de ↓ más corto que un fotograma no cuenta. Con la mano no pasa; con un test automático sí, y
costó un rato descubrirlo.

## Lo que el PR no puede traer

- **Código que se suba y se ejecute en caliente.** Esta página comparte origen con la que habla con Supabase;
  ejecutar JavaScript de fuera es acceso a los datos del grupo.
- **Publicar en Slack.** Ni con el token del bot, ni con un webhook, ni desde un endpoint propio. Compartir
  es copiar; lo pega la persona.
- **Escrituras a la base de datos.** El motor no habla con Supabase: el ranking lo escribe la página, y solo a
  través de `registrar_tiempo`. La tabla, con la clave pública, solo se lee.
- **Dependencias por CDN sin justificarlas.** Phaser es razonable y va en tu PR, con la versión fijada.

## Cómo entra

```bash
git switch -c feat/juego-motor
# tu código en v2/js/juego/
node --check v2/js/juego/*.js
node --test tests/
```

Rama, PR y revisión. Mergear despliega solo, así que lo que entra se ve ese mismo día.
