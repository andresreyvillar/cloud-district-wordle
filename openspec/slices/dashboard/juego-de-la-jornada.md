---
slice: juego-de-la-jornada
status: proposed
kind: action
actor: jugador
trigger:
  type: ui
  surface: web
  detail: "pestaña SuperWordleBros — /juego: el nivel de la jornada anterior, jugable"
events:
  emits: []
  consumes: []
specs:
  - dashboard
tests_root: tests/slices/juego-de-la-jornada/
blocked: null
---

# La cuadrícula de ayer se convierte en un nivel que se puede jugar

**Actor:** quien entra en la web
**Trigger:** la pestaña SuperWordleBros

## Contexto

Joel ha construido un plataformas donde **las cuadrículas del grupo son el escenario**: cada jugador ocupa un
tramo, sus verdes y amarillos son las plataformas, y debajo va su nombre con la nota del día. Se salta por
encima de la partida de ayer.

Este slice **no es el juego**. El juego lo desarrolla Joel y entra por PR, que es como tiene que entrar
código que se sirve a todo el grupo desde el mismo origen que habla con la base de datos. Lo que se hace aquí
es lo que el juego necesita para existir dentro de la web: **el generador del nivel**, la pestaña donde vive y
el contrato entre las dos piezas.

**El nivel se genera de la tabla, no del canal.** El prototipo lee los mensajes de Slack, y eso le cuesta dos
cosas: nombres de display en vez de los canónicos —`carlos.h` donde el resto de la web dice `Carlos H.`— y
jugadores que se quedan fuera, dos de doce el 22 de septiembre. Generándolo de la tabla sale el grupo entero
con la misma identidad que usa el resto de la web.

**La jornada es la anterior, no la de hoy.** La de hoy está abierta: quien no haya jugado todavía aparecería
sin cuadrícula y el nivel cambiaría bajo los pies de quien lo está jugando. La de ayer está cerrada y es
estable.

## Trigger técnico

La ruta `/juego` de la web estática. El nivel lo genera `nivelDe` a partir de los resultados: es un **render**
de las cuadrículas, no una regla del juego, así que no duplica ninguna verdad del pipeline. Desde
[[nivel-congelado]] no lo ejecuta el navegador sino el cron, una vez por jornada, y la pestaña juega el nivel
congelado.

## Comportamiento observable

### la-pestana-existe-y-dice-de-quien-es
**WHEN** se abre la pestaña SuperWordleBros
**THEN** la vista atribuye el juego a Joel de forma visible.

### la-pestana-lleva-al-juego
**WHEN** se pulsa la pestaña SuperWordleBros desde cualquier otra sección
**THEN** la web navega a `/juego`; y cada pestaña de la navegación lleva a su propia vista, ninguna a la portada
por defecto

### la-pestana-nueva-lleva-sticker-los-primeros-dias
**WHEN** se pinta la navegación antes de que caduque la novedad
**THEN** la pestaña SuperWordleBros lleva un sticker «¡NUEVO!», y a partir del día siguiente a la fecha fijada deja de
llevarlo sin que haga falta tocar el código.

### la-cabecera-dice-que-dia-es
**WHEN** se pinta la pestaña con un nivel
**THEN** la cabecera nombra la jornada por su día —«jornada de ayer» cuando lo fue, y su fecha cuando no— y
lleva además su número.

### la-pestana-explica-como-se-juega
**WHEN** se pinta la pestaña con un nivel
**THEN** trae una guía con los controles del juego y dice que se juega con teclado.

### el-pisoton-rebota-cinco-casillas
**WHEN** en el aire se pulsa ↓ y, al tocar suelo, Espacio dentro de una ventana corta
**THEN** el rebote sube cinco casillas desde donde se pisa. Es una propuesta sobre el motor de Joel, que tiene
la última palabra.

### el-rebote-sale-hacia-delante
**WHEN** sale bien el rebote del pisotón
**THEN** el personaje sale disparado hacia delante a velocidad de carrera —hacia donde se pulsa, o hacia donde
mira—, en lugar de salir parado en horizontal.

### el-tutorial-sale-antes-del-primer-muro-que-pide-pisoton
**WHEN** el jugador se acerca por primera vez a un muro que el salto normal no sube
**THEN** se enseña un tutorial breve del pisotón, con un GIF grabado del propio juego.

### el-tutorial-sale-una-sola-vez
**WHEN** el tutorial ya se vio en ese navegador
**THEN** no vuelve a salir solo, aunque el nivel del día tenga otro muro.

### el-tutorial-pausa-la-partida
**WHEN** el tutorial está abierto
**THEN** la partida está en pausa y el cronómetro no avanza, y al cerrarlo sigue donde estaba.

### el-tutorial-se-puede-volver-a-ver
**WHEN** alguien quiere repasar cómo se hace el pisotón
**THEN** la guía de controles tiene un enlace que abre el tutorial.

### las-teclas-del-juego-no-mueven-la-pagina
**WHEN** el juego tiene el foco y se pulsan el espacio o las flechas, con o sin Shift
**THEN** las recibe el juego y la página no se mueve.

### la-pagina-se-sigue-moviendo-con-lo-demas
**WHEN** el juego tiene el foco y se usa la rueda, el trackpad, la barra o Re Pág / Av Pág
**THEN** la página se mueve como siempre; y con el foco fuera del juego, las flechas también.

### el-nivel-sale-de-la-jornada-anterior
**WHEN** se genera el nivel
**THEN** los tramos son los de la última jornada **fechada antes de hoy**, no los de la jornada en curso — y a
primera hora, cuando aún no ha jugado nadie, sigue siendo la de ayer y no la de anteayer.

### cada-jugador-tiene-su-tramo
**WHEN** una jornada tiene N jugadores
**THEN** el nivel mide `N * 8 + 5` columnas y cada jugador ocupa ocho, en orden estable.

### la-cuadricula-es-el-escenario
**WHEN** un jugador resolvió con un patrón
**THEN** cada acierto es una plataforma verde y cada letra desplazada una naranja, colocadas de abajo arriba:
la fila 1 es su último intento y la fila más alta el primero.

### el-suelo-no-tiene-agujeros
**WHEN** se genera el nivel
**THEN** hay suelo bajo todas las columnas, de la primera a la última.

### cada-tramo-lleva-nombre-y-nota
**WHEN** se genera el tramo de un jugador
**THEN** lleva una etiqueta con su nombre y su nota, por encima de su cuadrícula.

### el-nombre-es-el-de-la-tabla
**WHEN** un jugador aparece en el nivel
**THEN** se le nombra como lo nombra el resto de la web, no con su identificador de Slack.

### el-coleccionable-se-puede-alcanzar
**WHEN** se coloca el coleccionable de un tramo
**THEN** descansa sobre una plataforma de ese tramo, nunca en el aire.

### la-misma-jornada-da-el-mismo-nivel
**WHEN** se genera el nivel de la misma jornada dos veces
**THEN** sale idéntico, porque nada en la generación depende del azar ni del reloj.

### una-jornada-sin-nadie-no-genera-nivel
**WHEN** la jornada anterior no tiene resultados
**THEN** la vista lo dice en lugar de pintar un nivel vacío.

### quien-no-tiene-cuadricula-no-rompe-el-nivel
**WHEN** un resultado no trae patrón
**THEN** ese jugador se queda fuera del nivel y el resto se genera igual.

### al-terminar-se-ofrece-compartir
**WHEN** alguien termina el nivel
**THEN** la vista le ofrece un texto con su tiempo y sus estrellas, listo para pegar en el canal.

### el-texto-lo-pega-la-persona-no-el-bot
**WHEN** se comparte una puntuación
**THEN** el texto se copia al portapapeles y lo publica quien jugó, igual que se publican los resultados de
Wordle. La web no tiene cómo publicar en su nombre: el token del bot vive solo en el workflow.

### el-texto-compartido-dice-de-que-jornada-es
**WHEN** se genera el texto para compartir
**THEN** lleva el número de jornada, el tiempo y las estrellas conseguidas sobre el total.

### el-mismo-resultado-da-el-mismo-texto
**WHEN** se genera dos veces el texto de la misma partida
**THEN** sale idéntico.

### sin-terminar-no-hay-nada-que-compartir
**WHEN** todavía no se ha terminado el nivel
**THEN** no se ofrece compartir.

## Estado después

La web gana una pestaña. **Ninguna cifra cambia**: el nivel es una lectura de lo que ya está publicado, no
escribe nada y no toca la instantánea.

## Edge cases

- **Un solo jugador**: el nivel mide 13 columnas y se juega igual.
- **Jornada con fallos (`X/6`)**: quien no resolvió no tiene fila verde final; su tramo es el que sea.
- **Patrón de menos filas que la nota**: se pinta lo que haya; el generador no inventa filas.
- **Nombres largos**: la etiqueta es texto y el juego la recorta si no cabe — no es cosa del generador.

## Fuera de alcance

- **El juego.** Lo desarrolla Joel y entra por PR. Aquí solo se define qué recibe y dónde se monta.
- **El ranking por tiempo.** Es el slice siguiente. Ojo: compartir en el canal cambia su diseño, porque un
  mensaje de Slack **lleva autor de verdad**. Un ranking leído del canal no necesita ni tabla con escritura
  anónima ni desplegable de «elige tu usuario», que era justo lo que lo hacía falsificable.
- **Subir código en caliente.** Un campo donde se pegue JavaScript y se ejecute es acceso a los datos del
  grupo desde el mismo origen que la clave pública. El código entra por rama, como todo.

## Slices compañeros

- [[clasificacion-de-temporada]] — la vista que ya carga los resultados que este nivel usa.
