---
slice: palabras-del-evento
status: shipped
kind: action
actor: participante del evento
trigger:
  type: ui
  surface: web
  detail: "ruta oculta /evento: elegir el nombre de la lista y adivinar las palabras del evento, una tras otra, como en el Wordle"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - resultados
  - ranking
tests_root: tests/slices/palabras-del-evento/
blocked: null
---

# En el evento, cada participante adivina las palabras una tras otra, contra el reloj

**Actor:** quien participa en el evento de la empresa, desde su móvil
**Trigger:** entrar en `/evento`, elegir su nombre de la lista y pulsar «Empezar» o «Siguiente palabra»

## Contexto

La empresa organiza un evento de una mañana con un juego para todos: **el Wordle de siempre** (decisión del dueño),
con varias palabras de cinco letras que se juegan **seguidas**. Cada palabra tiene **seis intentos**, y cada intento
tiene que ser una palabra válida. Tras cada intento, cada letra sale **verde** si está en la palabra y en su sitio,
**amarilla** si está pero en otro sitio, y **gris** si no está; una letra repetida solo sale verde o amarilla tantas
veces como aparece en la solución.

Se juega desde el móvil, sin cuenta. **Solo juegan quienes están en la lista** que la organización carga de antemano:
cada uno busca su nombre en un campo que autocompleta y que también despliega la lista entera. Cada participante
pertenece a uno de diez **grupos**, pero el móvil no lo sabe: los puntos se cuentan por grupo y los ve el admin.

**Antes de que el admin active el evento, el enlace solo dice que se activará en breve**: ni título, ni reglas, ni
nombres. Activado, todas las palabras están disponibles; se juegan una tras otra.

**Cada participante juega las palabras en su propio orden** (decisión del dueño, para que nadie pueda soplar «la
primera es…»): todos ven «Palabra 1/N», «Palabra 2/N»…, pero detrás de cada número hay una palabra distinta según
quién juegue. El orden lo decide el servidor, es fijo para cada participante y el móvil no sabe qué palabra del
evento tiene detrás de cada número hasta que el evento termina.

**Cada palabra tiene su cronómetro** (decisión del dueño): empieza al pulsar «Empezar» (la primera) o «Siguiente
palabra k/N» (las demás) y se para al resolverla o al gastar el sexto intento. El rato entre palabras no cuenta, y el
cronómetro **no se pausa**: cerrar la web no lo para. **La solución no viaja al móvil**: el servidor devuelve solo
los colores, y la palabra se enseña al terminar el evento. Los puntos (ver `admin-del-evento`) no se ven en el móvil.

**Acertar es lo que más cuenta, y el tiempo también, y se dice** (decisión del dueño): la pantalla de empezar y las
reglas dicen cuántos puntos da cada palabra acertada y hasta cuántos más da la rapidez, y que cada intento suma los
segundos que el evento tenga configurados; el cronómetro de cada palabra recuerda que el tiempo cuenta.

## Trigger técnico

Ruta `/evento` de la v2 (bajo `/2/`), que **no aparece en la navegación**: se llega por enlace o QR. La web llama a
funciones de la base de datos (`estado_del_juego`, `nombres_del_evento`, `elegir_nombre`, `mi_juego`,
`empezar_palabra`, `probar_palabra`) y no lee ni escribe ninguna tabla del evento. El identificador del móvil es un
token aleatorio que la web genera y guarda en el navegador antes de pedir el nombre. Si una palabra vale lo decide el
servidor: una del diccionario o la solución de esa misma palabra, que la empresa puede haber elegido fuera de él.

## Comportamiento observable

### la-ruta-del-evento-no-sale-en-el-menu
**WHEN** se abre `/evento` o `/evento/admin`
**THEN** se ve el juego del evento sin la cabecera ni la navegación de la web de estadísticas, y ninguna pestaña de la
navegación lleva a esas rutas

### el-evento-tiene-su-propia-apariencia
**WHEN** se abre cualquier pantalla del evento
**THEN** se ve con el tema del evento —fondo `#FAF9F4`, tinta negra, Helvetica y casillas verde, amarilla y gris
del Wordle—, declarado en variables de una hoja propia que la web de estadísticas no carga

### antes-de-activar-solo-se-ve-la-espera
**WHEN** se abre `/evento` y el admin aún no ha activado el evento
**THEN** solo se ve «El evento se activará en breve»: sin título, sin reglas y sin la lista de nombres, que el servidor
tampoco entrega

### la-espera-pasa-sola-al-juego
**WHEN** el admin activa el evento con la pantalla de espera abierta
**THEN** en el siguiente sondeo la pantalla pasa sola a pedir el nombre, sin recargar

### se-elige-el-nombre-de-la-lista
**WHEN** el participante escribe parte de su nombre (sin importar mayúsculas ni tildes) o despliega la lista, toca
su nombre y pulsa «Entrar»
**THEN** entra con ese nombre, tal como está escrito en la lista; los nombres ya elegidos salen en la lista sin poder
tocarse

### un-nombre-que-no-esta-en-la-lista-no-entra
**WHEN** el participante intenta entrar con un nombre que no está en la lista
**THEN** se le pide que lo elija de la lista y no entra

### un-nombre-elegido-no-lo-coge-otro-movil
**WHEN** un segundo móvil intenta entrar con un nombre que ya eligió otro
**THEN** se rechaza con «ese nombre ya está elegido: si eres tú, avisa a la organización», y el nombre sigue siendo
del primero

### el-mismo-movil-recupera-su-nombre
**WHEN** el participante recarga la página o vuelve más tarde con el mismo móvil
**THEN** sigue dentro con su nombre y lo que había jugado, sin volver a elegir, también si la respuesta al elegirlo se
perdió; sin red o con un fallo pasajero se reintenta en vez de pedir otro nombre, un móvil no puede quedarse con dos
nombres, y si el admin liberó el suyo vuelve a pedir el nombre

### el-grupo-no-viaja-al-movil
**WHEN** el móvil pide el estado, la lista de nombres o su juego
**THEN** ninguna respuesta lleva el grupo de nadie

### se-explica-como-se-juega
**WHEN** el participante está a punto de empezar la primera palabra, o pulsa «¿Cómo se juega?»
**THEN** ve las reglas del Wordle —cinco letras, seis intentos, palabras que existan— y qué significa cada color,
con un ejemplo inventado

### el-cronometro-de-cada-palabra-empieza-al-pulsar
**WHEN** el participante pulsa «Empezar» o «Siguiente palabra»
**THEN** aparece el tablero de esa palabra y su cronómetro arranca en ese momento con la hora del servidor; volver a
pulsar no lo reinicia, y el tiempo de la palabra va de ahí a resolverla o fallarla

### el-reloj-no-se-pausa
**WHEN** el participante cierra la web con una palabra empezada y vuelve más tarde
**THEN** el cronómetro sigue desde la hora en que empezó, sin descontar el rato que estuvo cerrada

### cada-palabra-tiene-seis-intentos-de-cinco-letras
**WHEN** el participante escribe un intento
**THEN** tiene que ser de cinco letras (uno más corto no se envía, uno más largo no se escribe), y al sexto sin
acertar la palabra termina sin resolver

### una-letra-se-corrige-sin-borrar-las-demas
**WHEN** el participante toca una casilla de la fila que está escribiendo y teclea una letra
**THEN** la letra va a esa casilla sin tocar las demás y el cursor pasa a la siguiente casilla vacía; borrar quita la
letra de la casilla elegida, o la de la anterior si la elegida está vacía, y las flechas mueven el cursor (como en
lapalabradeldia.com, a diferencia del Wordle original)

### los-avisos-flotan-sobre-la-pantalla
**WHEN** sale un aviso («Enviando…», una palabra que no está en la lista, falta una letra, sin conexión)
**THEN** aparece superpuesto a la pantalla, sin desplazar el tablero ni el teclado, y los de error desaparecen solos
a los pocos segundos

### una-palabra-que-no-esta-en-la-lista-no-gasta-intento
**WHEN** el participante envía una palabra que no está en la lista de palabras válidas
**THEN** se le avisa, la palabra se queda escrita para corregirla y no gasta intento; la solución de otra palabra
que no esté en el diccionario tampoco vale, para no delatarla

### los-colores-son-los-del-wordle
**WHEN** se envía un intento válido
**THEN** cada letra en su sitio sale verde, cada letra que está en la palabra pero en otro sitio sale amarilla y cada
letra que no está sale gris; las tildes no cuentan y la ñ es una letra más; el teclado nunca baja a una letra de color

### una-letra-repetida-se-colorea-como-en-el-wordle
**WHEN** un intento repite una letra
**THEN** primero salen verdes las que están en su sitio y después, de izquierda a derecha, amarillas solo mientras
queden en la solución letras así sin verde ni amarilla; el resto, gris

### se-gana-con-cinco-verdes
**WHEN** un intento sale con las cinco letras verdes
**THEN** la palabra queda resuelta, con su número de intentos y su tiempo, y no admite más intentos

### al-terminar-una-palabra-se-pasa-a-la-siguiente
**WHEN** el participante resuelve o falla una palabra que no es la última
**THEN** ve el resultado y el botón «Siguiente palabra k/N», que empieza la siguiente con su propio cronómetro; tras
la última ve el resumen de todas, sin puntos

### las-palabras-se-juegan-en-orden
**WHEN** se intenta empezar una palabra sin haber terminado la anterior
**THEN** el servidor lo rechaza: las palabras se juegan una tras otra

### cada-participante-juega-las-palabras-en-su-orden
**WHEN** varios participantes juegan la «Palabra 1/N», la «2/N»…
**THEN** cada uno juega todas las palabras del evento, una vez cada una, pero en un orden que depende de quién es: no
todos tienen la misma palabra detrás del mismo número

### el-orden-de-cada-uno-no-cambia
**WHEN** un participante recarga la web o vuelve más tarde
**THEN** detrás de cada número sigue la misma palabra que tenía

### el-orden-no-viaja-al-movil
**WHEN** el participante juega con el evento en marcha
**THEN** ninguna respuesta del servidor dice qué palabra del evento hay detrás de cada número: solo el número que ve

### los-puntos-comparan-la-misma-palabra
**WHEN** se calculan los puntos de una palabra que unos jugaron como la primera y otros como la tercera
**THEN** compiten todos los que jugaron esa palabra, sea cual sea el número que les tocó

### el-tiempo-cuenta-y-se-dice
**WHEN** el participante va a empezar o lee las reglas
**THEN** ve que acertar es lo que más cuenta (los puntos de cada palabra acertada) y que el tiempo también (hasta
cuántos puntos más por rapidez, y los segundos que suma cada intento), con las cifras del evento o sin cifras si el
servidor no las da; mientras juega una palabra, junto al reloj se le recuerda que el tiempo cuenta

### la-palabra-resuelta-se-nombra
**WHEN** el participante resuelve una palabra
**THEN** el resultado la nombra («¡CASAS! Resuelta en…») y el resumen de sus palabras también; las que falla siguen sin
nombre hasta que termina el evento

### la-solucion-no-viaja-al-movil
**WHEN** el participante falla una palabra
**THEN** no se le enseña la solución, que ninguna respuesta del servidor lleva hasta que termina el evento

### al-terminar-el-evento-no-se-admiten-palabras
**WHEN** el admin termina el evento
**THEN** no se puede empezar ninguna palabra, ni enviar intentos, ni elegir nombre, la lista de nombres deja de
entregarse y una palabra a medias se queda sin terminar

### al-terminar-el-evento-se-ven-las-soluciones
**WHEN** el evento ha terminado
**THEN** el participante ve el resumen de las suyas en su orden, cada una con la palabra que le tocó (resuelta, sin
resolver, sin terminar o sin jugar); quien no eligió nombre ve las palabras del evento

### el-texto-de-los-participantes-se-escapa
**WHEN** un nombre de la lista lleva HTML
**THEN** se pinta como texto en la lista y en la cabecera

### si-el-servidor-no-responde-el-intento-no-se-pierde
**WHEN** se envía un intento y la respuesta no llega (sin red o pasado el plazo)
**THEN** la palabra se queda escrita para reenviarla, y el reenvío lleva el mismo número de intento, así que si el
primero sí llegó no se gasta otro

### la-web-no-toca-las-tablas-del-evento
**WHEN** alguien usa la clave pública contra las tablas del evento, sus funciones internas o las del juego de frases
**THEN** se le deniega: solo las funciones públicas del juego responden

## Fuera de alcance

- Los puntos, el ranking por grupos y su exportación: `admin-del-evento`.
- Comprobar que quien elige un nombre es esa persona: el primer móvil se lo queda, y el admin puede liberarlo.

## Dependencias

- [[admin-del-evento]] activa y termina el evento.
