---
slice: frase-del-evento
status: shipped
kind: action
actor: participante del evento
trigger:
  type: ui
  surface: web
  detail: "ruta oculta /evento: entrar con un nombre, empezar una frase liberada y destaparla con palabras de cinco letras"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - resultados
  - ranking
tests_root: tests/slices/frase-del-evento/
blocked: null
---

# En el evento, cada participante destapa la frase con palabras, contra el reloj

**Actor:** quien participa en el evento de la empresa, desde su móvil
**Trigger:** entrar en `/evento` con un nombre, pulsar «Empezar» en una frase liberada y enviar palabras

## Contexto

La empresa organiza un evento de una mañana y quiere un juego para todos, con **las reglas de «La frase del día»
de lapalabradeldia.com** (decisión del dueño). Cada frase está oculta en casillas, como en el ahorcado. Se juega con
**palabras válidas de cinco letras**, cinco como mucho. Cada letra de una palabra que está en la frase y no había
salido antes se pinta de verde y **se destapa en todos los sitios donde aparece**. **Se gana al destapar todas las
letras de la frase**: no hace falta escribirla, sino encontrar palabras que cubran las letras que faltan. Se juega
desde el móvil, sin cuenta: cada uno escribe su nombre al entrar.

Las frases se **liberan** de una en una cada cierto tiempo, para que todo el mundo juegue la misma a la vez.
**No hay tiempo máximo** (decisión del dueño): una frase liberada se puede jugar hasta que el presentador termina el
evento. **La solución no viaja al móvil**: el servidor guarda la frase y devuelve solo las letras que cada uno se ha
ganado. La frase entera se enseña al terminar el evento.

**El cronómetro empieza en cero al pulsar «Empezar»** y cuenta lo que se tarda hasta destapar la frase o gastar las
cinco palabras. **No se pausa** (decisión del dueño): cerrar la web no para el reloj, porque cerrar, pensarlo y
volver convertiría el tiempo en lo que se tarda en teclear. Durante el evento nadie ve su posición: el ranking se
publica al terminar.

## Trigger técnico

Ruta `/evento` de la v2 (bajo `/2/`), que **no aparece en la navegación**: se llega por enlace o QR. La web
llama a funciones de la base de datos (`unirse_al_evento`, `estado_del_evento`, `mi_partida_del_evento`,
`empezar_frase`, `intentar_palabra`, `ranking_del_evento`) y no lee ni escribe ninguna tabla del evento. El
identificador del móvil es un token aleatorio que la web genera la primera vez y guarda en el navegador. La lista de
palabras válidas viaja a la web (`assets/evento/palabras.txt`) para avisar al momento; quien decide es el servidor.

## Comportamiento observable

### la-ruta-del-evento-no-sale-en-el-menu
**WHEN** se abre `/evento`
**THEN** se ve el juego del evento sin la cabecera ni la navegación de la web de estadísticas, y ninguna pestaña
de la navegación lleva a `/evento`

### el-evento-tiene-su-propia-apariencia
**WHEN** se cambia el tema del evento —colores, tipografía, logo—
**THEN** solo se toca la hoja de estilos del evento, que los declara como variables; el juego no cambia y la web
de estadísticas tampoco. Parte con la marca de Cloud District y se adapta al tema del evento cuando esté decidido

### se-entra-con-un-nombre
**WHEN** alguien escribe su nombre y pulsa Entrar
**THEN** queda apuntado en el evento con ese nombre, y al recargar la página sigue dentro sin volver a escribirlo

### un-evento-con-contrasena-solo-deja-entrar-a-quien-la-sabe
**WHEN** el evento tiene contraseña de acceso (una demo para la organización) y alguien intenta entrar
**THEN** la web la pide junto al nombre, y el servidor rechaza a quien no la da o la da mal sin apuntarlo; un móvil
ya apuntado no la vuelve a necesitar, y un evento sin contraseña no la pide

### un-nombre-no-se-repite
**WHEN** desde otro móvil alguien intenta entrar con un nombre que ya está apuntado, aunque cambien las
mayúsculas, los acentos, los espacios de los extremos o lleve caracteres invisibles
**THEN** se rechaza y se le pide otro nombre

### un-movil-entra-con-un-solo-nombre
**WHEN** un móvil que ya está apuntado intenta entrar con otro nombre
**THEN** sigue dentro con el primero: un móvil no juega dos veces la misma frase con nombres distintos

### se-explica-como-se-juega
**WHEN** el participante espera a que empiece el evento, o pulsa «¿Cómo se juega?» en cualquier momento
**THEN** ve una explicación breve —palabras de cinco letras, cinco por frase, qué significa cada color, que se gana
al destapar todas las letras y cómo cuenta el tiempo— con un ejemplo inventado, no una frase del evento

### antes-de-liberar-se-ve-la-cuenta-atras
**WHEN** queda alguna frase por liberar
**THEN** se ve cuánto falta para la siguiente, contado con la hora del servidor; si el evento no ha empezado, no hay
hora que contar y se dice que la primera frase sale en cuanto lo empiece el presentador

### una-frase-liberada-se-juega-hasta-el-final
**WHEN** una frase se ha liberado y el evento no ha terminado
**THEN** el participante la ve en su lista y la puede empezar o seguir, aunque ya se hayan liberado otras después

### el-tablero-sale-al-pulsar-empezar
**WHEN** el participante pulsa Empezar en una frase liberada
**THEN** aparece la frase en casillas tapadas —cuántas letras tiene cada palabra y dónde van los signos— y un tablero
de cinco palabras; antes de pulsar, la forma no se ve

### el-cronometro-empieza-en-cero
**WHEN** el participante pulsa Empezar
**THEN** su cronómetro empieza en 0:00 con la hora del servidor y cuenta hacia arriba, sin tiempo máximo

### el-reloj-no-se-pausa
**WHEN** el participante cierra la web a mitad de una frase y vuelve a abrirla
**THEN** sigue en la misma partida, con sus palabras, y el cronómetro marca el tiempo real desde que pulsó Empezar

### cada-intento-es-una-palabra-de-cinco-letras
**WHEN** el participante envía una palabra de cinco letras que está en la lista de palabras válidas
**THEN** se acepta y se colorea

### una-palabra-que-no-esta-en-la-lista-no-gasta-intento
**WHEN** el participante envía cinco letras que no forman una palabra de la lista
**THEN** se le dice que la palabra no está en la lista y el intento no se gasta

### un-intento-incompleto-no-se-envia
**WHEN** el participante pulsa Enviar con letras por rellenar
**THEN** no se envía nada y el intento no se gasta

### verde-destapa-la-letra-en-toda-la-frase
**WHEN** una letra de la palabra está en la frase y no había salido en una palabra anterior
**THEN** se pinta de verde y se destapa en todas las casillas de la frase donde aparece; si se repite en la misma
palabra, sale verde las dos veces

### amarilla-si-ya-estaba-destapada
**WHEN** una letra de la palabra está en la frase pero ya se destapó con una palabra anterior
**THEN** se pinta de amarillo y no destapa nada nuevo

### gris-si-no-esta
**WHEN** una letra de la palabra no está en la frase
**THEN** se pinta de gris

### los-acentos-no-cuentan-y-la-ene-si
**WHEN** la frase o la palabra llevan tildes o diéresis
**THEN** se comparan sin ellas, y la ñ es una letra distinta de la n

### se-gana-al-destapar-todas-las-letras
**WHEN** una palabra destapa las últimas letras que quedaban de la frase
**THEN** la partida termina resuelta, su tiempo queda guardado y se ve «¡Resuelta en m:ss!», sin puesto ni puntos

### cinco-palabras-sin-destaparla-se-pierde
**WHEN** el participante envía la quinta palabra y aún quedan letras tapadas
**THEN** la partida termina sin resolver, su tiempo queda guardado y no se admiten más palabras

### tras-terminar-se-pasa-a-la-siguiente
**WHEN** el participante termina una frase, resuelta o perdida
**THEN** ve un botón para ir a la siguiente; si aún no se ha liberado, el botón está apagado y cuenta lo que falta,
con la hora del servidor, y se enciende solo al llegar a cero; tras la última, se le dice que el ranking sale al
terminar el evento

### la-solucion-no-viaja-al-movil
**WHEN** se juega una frase antes de que termine el evento
**THEN** ninguna respuesta del servidor contiene su texto completo: solo las letras que el participante ha destapado,
y la clave pública no puede leerla de ninguna tabla

### la-solucion-se-ve-al-terminar-el-evento
**WHEN** el presentador termina el evento
**THEN** el participante ve la frase entera de cada ronda; antes, ni siquiera tras resolverla o perderla

### una-partida-por-frase
**WHEN** el participante recarga la página o vuelve a pulsar Empezar en una frase ya empezada
**THEN** sigue en la misma partida, con sus palabras y con la hora de inicio de la primera vez

### al-terminar-el-evento-no-se-admiten-palabras
**WHEN** el presentador termina el evento con la partida de alguien a medias
**THEN** el servidor rechaza sus palabras y esa partida no cuenta: ni frase resuelta ni tiempo

### durante-el-evento-no-se-ve-la-posicion
**WHEN** el evento está en curso
**THEN** el participante no ve su puesto ni el de nadie, y el servidor no entrega el ranking

### al-terminar-se-ve-el-ranking
**WHEN** el presentador termina el evento
**THEN** el participante ve el ranking final, con su fila destacada

### el-teclado-trae-la-ene
**WHEN** se juega desde el móvil
**THEN** hay un teclado en pantalla con la Ñ; las letras destapadas se ven en verde y las que no están, en gris

### el-texto-de-los-participantes-se-escapa
**WHEN** un nombre contiene HTML
**THEN** se pinta como texto, no como marcado

### la-base-de-datos-valida-lo-que-entra
**WHEN** llega una palabra de un móvil que no está apuntado, a una frase que no está liberada o que no ha
empezado, con un número de letras distinto de cinco, con caracteres que no son letras o que no está en la lista, un
número de intento que no cuadra, o un nombre vacío, de más de 30 caracteres, con caracteres invisibles o de otro
alfabeto, o cuando el evento ya tiene 500 participantes
**THEN** se rechaza y no se guarda nada

### la-web-no-toca-las-tablas-del-evento
**WHEN** se intenta leer, insertar, cambiar o borrar directamente en las tablas del evento con la clave pública
**THEN** se rechaza: todo pasa por las funciones

### si-el-servidor-no-responde-el-intento-no-se-pierde
**WHEN** el envío de una palabra falla por la red, se queda colgado o se pierde su respuesta
**THEN** se dice que no se ha podido enviar, la palabra sigue escrita, el teclado sigue respondiendo y al reenviarla
el servidor no la cuenta dos veces

## Estado después

Una fila en `event_players` por participante, una en `event_plays` por frase empezada (con `empezada_en`, las
letras destapadas y, al terminar, `terminada_en` y `resuelta`) y una en `event_guesses` por palabra con sus colores.
No se toca `wordle_results` ni ninguna otra tabla de la web de estadísticas.

## Edge cases

- **Incógnito**: otra pestaña de incógnito es otro móvil para el servidor. Puede entrar con **otro** nombre, que
  aparecerá en el ranking y se ve; sin cuentas no se puede blindar más.
- **Hora del móvil desajustada**: el cronómetro y las cuentas atrás usan la hora del servidor.
- **Corregir un nombre mal escrito**: lo hace el dueño desde Supabase.
- **Abandonar en vez de fallar**: una partida sin terminar no suma tiempo y una fallada sí (decisión del dueño, con
  el incentivo a la vista: a quien va a fallar le conviene no gastar la quinta palabra).

## Slices compañeros

- [[pantalla-del-evento]] — el presentador empieza y termina el evento, y enseña el ranking final.
- [[debate-de-reglas]] — el mismo patrón: la web no escribe en las tablas, llama a funciones que validan.
