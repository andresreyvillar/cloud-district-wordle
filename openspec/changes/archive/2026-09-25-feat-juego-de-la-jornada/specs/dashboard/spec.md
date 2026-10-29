# Deltas de `dashboard` — feat-juego-de-la-jornada

## ADDED Requirements

### Requirement: El nivel del juego se deriva de la jornada anterior, y es una función pura

La web ofrece el nivel de un plataformas cuyos escenarios son las cuadrículas del grupo. El nivel se calcula
**a partir de los resultados ya publicados**, en JavaScript (`nivelDe`), y es una función pura de ellos:
mismos resultados, mismo nivel, sin reloj y sin azar. Quién lo ejecuta y cuándo lo decide `nivel-congelado`
(el cron, una vez por jornada).

Vive en JavaScript porque **no es una regla del juego sino un render**: no clasifica nada ni decide nada que
la tabla no diga ya. Un clasificador reimplementado en JavaScript sería una segunda verdad; dibujar una
cuadrícula que ya existe, no.

La jornada es la **anterior**, no la en curso: la de hoy sigue abierta, así que quien aún no haya jugado
aparecería sin cuadrícula y el nivel cambiaría bajo los pies de quien lo está jugando.

#### Scenario: el nivel usa la última jornada cerrada
- GIVEN resultados de varias jornadas, la última de ellas en curso
- WHEN se genera el nivel
- THEN los tramos son los de la jornada anterior a la última

#### Scenario: la misma jornada da el mismo nivel
- GIVEN los mismos resultados
- WHEN se genera el nivel dos veces
- THEN los dos niveles son idénticos

verified-by:
  - tests/slices/juego-de-la-jornada/nivel.test.js


### Requirement: La cuadrícula de cada jugador es el escenario de su tramo

Cada jugador ocupa **ocho columnas**, y las cinco centrales llevan su cuadrícula: un acierto es una
plataforma verde, una letra desplazada una naranja, y una letra ausente es hueco. Las filas se colocan **de
abajo arriba** —la fila 1 es el último intento, el que resolvió— así que el escenario se lee como se leyó la
partida: cuanto más arriba, más lejos estaba de acertar.

El ancho del nivel es `N * 8 + 5`, con las cinco columnas de cola para la meta. Y hay suelo bajo **todas** las
columnas: un hueco en el suelo es una caída por la que se pierde la partida sin haber fallado.

Bajo la cuadrícula de cada tramo va una etiqueta con el nombre del jugador y su nota.

#### Scenario: los verdes y amarillos se convierten en plataformas
- GIVEN un jugador con un patrón conocido
- WHEN se genera su tramo
- THEN cada acierto es una plataforma verde y cada letra desplazada una naranja, en su columna

#### Scenario: la última fila es la de abajo
- GIVEN un jugador que resolvió en varios intentos
- WHEN se genera su tramo
- THEN la fila 1 corresponde a su último intento

#### Scenario: el suelo cubre el nivel entero
- GIVEN una jornada cualquiera
- WHEN se genera el nivel
- THEN hay suelo en todas las columnas, de la primera a la última

verified-by:
  - tests/slices/juego-de-la-jornada/nivel.test.js


### Requirement: A los jugadores se les nombra como en el resto de la web

El nivel usa el nombre que la tabla guarda para cada jugador, que es el mismo que aparece en el marcador y en
las fichas. El prototipo leía los mensajes del canal y arrastraba dos defectos: identificadores de display
—`carlos.h` donde la web dice `Carlos H.`— y jugadores que se quedaban fuera, dos de doce en una jornada
medida. Leyendo la tabla no pasa ninguna de las dos cosas.

#### Scenario: el nombre del nivel es el de la tabla
- GIVEN un jugador cuyo nombre mostrado difiere de su identificador
- WHEN se genera su etiqueta
- THEN lleva el nombre de la tabla

verified-by:
  - tests/slices/juego-de-la-jornada/nivel.test.js


### Requirement: Lo que falta no rompe el nivel

Un resultado **sin patrón** no puede pintarse, así que su jugador se queda fuera y el resto del nivel se
genera igual; contarlo con un tramo vacío dejaría ocho columnas de nada en mitad del recorrido.

Una jornada **sin nadie** no produce nivel: la vista lo dice en lugar de pintar un escenario vacío.

El coleccionable de cada tramo **descansa sobre una plataforma** de ese tramo. Dónde exactamente lo decide el
repositorio y no el azar: el prototipo lo colocaba aleatoriamente, y este proyecto exige que la misma jornada
dé siempre el mismo nivel.

#### Scenario: un resultado sin patrón no genera tramo
- GIVEN una jornada donde un resultado no trae patrón
- WHEN se genera el nivel
- THEN ese jugador no aparece y los demás sí

#### Scenario: sin resultados no hay nivel
- GIVEN una jornada anterior sin resultados
- WHEN se genera el nivel
- THEN no se devuelve nivel

#### Scenario: el coleccionable se apoya en una plataforma
- GIVEN el tramo de un jugador con cuadrícula
- WHEN se coloca su coleccionable
- THEN hay una plataforma justo debajo

verified-by:
  - tests/slices/juego-de-la-jornada/nivel.test.js


### Requirement: La puntuación se comparte como se comparte el Wordle — la pega quien juega

Al terminar el nivel, la vista ofrece un texto con la jornada, el tiempo y las estrellas, y lo copia al
portapapeles. **Lo publica la persona, no el bot.**

Es el mismo modelo que ya usan los resultados de Wordle —cada uno pega el suyo— y hay dos razones para no
hacerlo de otra forma. La primera es que **la web no puede usar el token del bot**: es estática, sin servidor,
y el token vive solo en los secrets del workflow. Que el bot publicara la puntuación de alguien exigiría un
endpoint con el token dentro, expuesto a la web pública — una vía de escritura al canal desde fuera del
workflow, que es lo que las reglas de este repositorio prohíben.

El bot sí publica texto en el canal, pero **siempre pegado a un fichero**: el resumen diario es el
`initial_comment` de la subida de la captura, que cabe en su scope `files:write`. Lo que no tiene es
`chat:write`, para mensajes sueltos. Esa limitación no es la razón de este diseño; la razón es la anterior.

Y tiene una consecuencia que vale más que la comodidad: **un mensaje de Slack lleva autor de verdad**. Una
puntuación pegada por su dueño está firmada por quien la hizo, sin desplegable de «elige tu usuario» y sin
escritura anónima contra la base de datos. El texto se escribe con una cabecera estable y legible por si algún
día se quiere leer el ranking del canal, igual que se leen los resultados.

El texto es **función pura** del resultado de la partida: la misma partida da siempre el mismo texto.

#### Scenario: al terminar se ofrece compartir
- GIVEN una partida terminada con su tiempo y sus estrellas
- WHEN la vista recibe el final
- THEN ofrece un texto para compartir

#### Scenario: el texto lleva jornada, tiempo y estrellas
- GIVEN un resultado de partida
- WHEN se genera el texto
- THEN incluye el número de jornada, el tiempo y las estrellas sobre el total

#### Scenario: el mismo resultado da el mismo texto
- GIVEN el mismo resultado
- WHEN se genera el texto dos veces
- THEN los dos textos son idénticos

#### Scenario: sin partida terminada no se ofrece compartir
- GIVEN que nadie ha terminado el nivel
- WHEN se pinta la vista
- THEN no hay nada que compartir

verified-by:
  - tests/slices/juego-de-la-jornada/compartir.test.js


### Requirement: El pisotón rebota cinco casillas

Con la física del motor de Joel el salto máximo es 3,52 casillas, y una cuadrícula puede levantar una columna
de hasta 6, así que un escalón de 4 es un muro: el nivel del 24 de septiembre no se podía terminar. El dueño
probó primero una casilla más y la subió a **cinco en total**: con +1, la parte de Luis del 24 de septiembre
solo se pasaba rebotando en el último bloque de Juan con media casilla de margen, y en la práctica no salía.

En el aire, ↓ (o S) hace caer en picado; si al tocar suelo se pulsa Espacio dentro de una ventana corta, el
rebote sube **cinco casillas** desde donde se pisa, con un destello y chispas para que se note que salió. La
velocidad se deriva de la gravedad en lugar de escribirse a mano, así que sigue siendo cinco aunque cambie.

**Cinco casillas no salvan una pared de 6 desde el suelo** —17 de 221 jornadas la tienen—, pero sí desde lo
alto del tramo anterior, que es un reto y es lo que se pidió: el muro lo pone el grupo con sus propias
partidas, y le cuesta, porque una pared de altura *h* exige una cuadrícula de al menos *h* intentos. Y una de 5
se pasa desde el suelo por un margen de cinco píxeles que depende de la duración del fotograma: en una
pantalla de más refresco podría no pasarse.

#### Scenario: el rebote sube cinco casillas
- GIVEN la física del motor
- WHEN se calcula el salto del rebote
- THEN su altura máxima es de cinco casillas

#### Scenario: el rebote sale hacia delante
- GIVEN un rebote del pisotón
- WHEN sale bien
- THEN el personaje sale a velocidad de carrera hacia donde se pulsa, o hacia donde mira

#### Scenario: el pisotón pasa un muro que el salto normal no
- GIVEN un muro de cuatro casillas
- WHEN se intenta con el salto normal y con el pisotón
- THEN el normal se queda delante y el pisotón lo pasa

```yaml
checks:
  - type: regex
    file: v2/js/juego/motor.js
    pattern: 'rebote \? REBOTE_VELOCITY : JUMP_VELOCITY'
    describe: el motor usa el rebote al saltar dentro de la ventana del pisotón, no solo lo calcula
  - type: regex
    file: v2/js/juego/motor.js
    pattern: 'setVelocityX\(impulsoDelRebote\('
    describe: el rebote sale hacia delante, no solo hacia arriba
```

verified-by:
  - tests/slices/juego-de-la-jornada/pisoton.test.js


### Requirement: El tutorial del pisotón sale justo cuando hace falta

La primera vez que el jugador se acerca a un muro que el salto normal no sube, el juego se pausa y enseña un
tutorial breve: un GIF grabado del propio motor y los tres pasos del combo. Se enseña **una sola vez por
navegador** —si saliera cada día, al tercero sería un estorbo—, y la guía de controles tiene un enlace para
volver a verlo.

El sitio lo decide **el motor con su propia física**, no el generador: si el salto cambia, el aviso sigue
saliendo delante del muro correcto. Y cuenta como muro solo lo apilado desde el suelo sin huecos: un bloque
flotante se pasa por debajo, y avisar delante de él sería enseñar a resolver un problema que no existe.

La pausa no es cortesía: el tutorial sale con el cronómetro corriendo, justo delante de un muro, y leerlo
costaría segundos en el ranking.

#### Scenario: el tutorial sale antes del primer muro que pide pisotón
- GIVEN un nivel con un muro más alto que el salto normal
- WHEN el jugador se acerca a él por primera vez
- THEN se abre el tutorial

#### Scenario: el tutorial sale una sola vez
- GIVEN que el tutorial ya se vio en ese navegador
- WHEN el jugador llega a un muro que pide pisotón
- THEN no se abre solo

#### Scenario: el tutorial pausa la partida
- GIVEN el tutorial abierto
- WHEN pasa el tiempo
- THEN el cronómetro no avanza, y al cerrarlo la partida sigue

```yaml
checks:
  - type: regex
    file: v2/js/juego/motor.js
    pattern: 'dispatchEvent\(new CustomEvent\("superbros:pista-pisoton"'
    describe: el motor avisa a la página delante del primer muro que pide pisotón
  - type: regex
    file: v2/js/ui/juego.js
    pattern: 'addEventListener\(EVENTO_PISTA'
    describe: la página escucha ese aviso para abrir el tutorial
```

verified-by:
  - tests/slices/juego-de-la-jornada/tutorial.test.js


### Requirement: Las teclas del juego no mueven la página, y lo demás sí

Con el juego enfocado, el espacio y las flechas son del juego **también con Shift**. Phaser bloquea el scroll de
sus teclas, pero deja de hacerlo cuando va pulsado un modificador, y el pisotón se hace corriendo con Shift:
Shift + Espacio —«subir la página» en cualquier navegador— mandaba la página arriba justo al rebotar.

La rueda, el trackpad, la barra y Re Pág / Av Pág siguen moviendo la página con el juego enfocado —Phaser se
quedaba la rueda por defecto, y con el puntero encima del juego no se podía bajar—. Con el foco fuera del
juego, las flechas mueven la página y el personaje no se mueve, porque el motor escucha el teclado en el
lienzo y no en toda la ventana. Un clic en el juego le devuelve el foco, y mientras no lo tiene un aviso lo
dice.

**El bloqueo del scroll se engancha en el padre del lienzo, no en el lienzo.** Phaser descarta las teclas que
le llegan ya bloqueadas, y enganchado en el lienzo el bloqueo iba antes que él: el juego se quedaba sin
teclas. Se detectó repitiendo las pruebas de juego tras arreglar el scroll, no con la prueba del scroll, que
solo miraba la página.

#### Scenario: el pisotón con Shift no mueve la página
- GIVEN el juego enfocado
- WHEN se hace el pisotón corriendo con Shift
- THEN la página no se mueve y el personaje sí

#### Scenario: la rueda sigue moviendo la página
- GIVEN el juego enfocado
- WHEN se usa la rueda del ratón encima del juego
- THEN la página se mueve

#### Scenario: con el foco fuera, las flechas son de la página
- GIVEN el foco fuera del juego
- WHEN se pulsa una flecha
- THEN la página se mueve y el personaje no

```yaml
checks:
  - type: regex
    file: v2/js/ui/juego.js
    pattern: "lienzo\\.parentElement\\.addEventListener\\('keydown'"
    describe: el bloqueo del scroll va en el padre; en el lienzo le quitaba las teclas al juego
  - type: regex
    file: v2/js/juego/motor.js
    pattern: 'keyboard: \{ target: lienzo \}'
    describe: el motor escucha el teclado en el lienzo, no en toda la ventana
  - type: regex
    file: v2/js/juego/motor.js
    pattern: 'preventDefaultWheel: false'
    describe: la rueda no se la queda el juego
```

verified-by:
  - tests/slices/juego-de-la-jornada/teclado.test.js
