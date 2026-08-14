"""El diccionario de frases del resumen diario. **Solo datos: ni lógica ni reloj.**

Slice: `voz-de-la-jornada` (openspec/slices/publicacion/voz-de-la-jornada.md).

Tres procedencias, y la distinción no es cosmética porque **el repositorio es público**:

1. **Refranero tradicional español** — anónimo y de dominio público por antigüedad. Se recogen los refranes
   en sí, nunca la ficha, el comentario o la selección de un refranero editado: el refrán no tiene dueño, la
   compilación sí. Verificados contra el Refranero Multilingüe del Centro Virtual Cervantes.
2. **Proverbios asiáticos tradicionales** — igual de anónimos y públicos (chinos y japoneses).
3. **Pullas propias** — escritas para este canal. Es lo que ocupa el registro de meme y cultura pop, en
   lugar de citar guiones de televisión o posts de foros, que son obra de terceros aunque la frase sea corta.

`{jugador}` es el único hueco de plantilla. Las frases que lo llevan se formatean con el nombre; las que no,
se publican tal cual.

**Quince por registro** es deliberado: con menos de diez el grupo se las sabe en dos semanas, y quince dan
más de un mes sin repetir. Editar una frase no toca datos ni migra nada — es una lista.
"""

from __future__ import annotations

# ─────────────────────────────────────────────────────────────────────────────
# El día, según lo dura que fue la palabra. El registro lo elige `dificultad()`.
# ─────────────────────────────────────────────────────────────────────────────

#: Día fácil: el grupo la resolvió pronto y en bloque.
DIA_FACIL: tuple[str, ...] = (
    "Hoy la palabra se ha dejado querer.",
    "A palabras necias, oídos sordos; y a palabra fácil, dedos rápidos.",
    "Pan comido, y encima con vino.",
    "Hoy hasta el gato la habría sacado en tres.",
    "No hay mejor salsa que el hambre, ni mejor palabra que la que se cae sola.",
    "Un viaje de diez mil kilómetros empieza por un solo paso. Hoy el viaje eran dos pasos.",
    "Quien pisa con suavidad va lejos; hoy no hizo falta ni pisar.",
    "Día de vino y rosas para el diccionario.",
    "Hoy el marcador ha sido un trámite y todos lo sabemos.",
    "A falta de dificultad, buenas son victorias.",
    "La palabra ha venido a entregarse, no a competir.",
    "Hoy no se ha ganado nada: se ha recogido.",
    "Ejecuta las cosas difíciles cuando todavía son fáciles. Hoy todas lo eran.",
    "Hoy el reto era acordarse de publicar.",
    "Nunca llueve a gusto de todos, pero hoy no ha llovido.",
)

#: Día normal: ni gloria ni sangre. Es el registro que sale la mayoría de los días.
DIA_NORMAL: tuple[str, ...] = (
    "Jornada de oficina: sin gloria ni sangre.",
    "Ni tanto ni tan calvo.",
    "Unas veces se gana y otras se pierde; hoy un poco de cada.",
    "Juntando los bienes con males, resultan todos los años iguales.",
    "Hoy la palabra ha cumplido el expediente.",
    "Yendo y viniendo vamos viviendo.",
    "Ni lo dulce ni lo amargo dura tiempo largo.",
    "Día de los de andar por casa.",
    "Hoy nadie se ha lucido y nadie se ha hundido: empate técnico con la vida.",
    "Hay que cruzar el río palpando las piedras, y hoy había piedras.",
    "Una onza de tiento vale más que una libra de talento.",
    "El polvo, si se acumula, hace montañas. Hoy toca acumular.",
    "Hoy el marcador se mueve poco y las excusas también.",
    "Cada uno estornuda como Dios le ayuda.",
    "Jornada sin titular, que también hay que saber tenerlas.",
)

#: Día duro: la palabra se ha vendido cara.
DIA_DURO: tuple[str, ...] = (
    "Hoy la palabra ha salido con navaja.",
    "En la tardanza está el peligro, y hoy ha habido mucha.",
    "A perro flaco, todo son pulgas.",
    "Las desgracias nunca vienen solas, y hoy han venido en grupo.",
    "Cáete siete veces, levántate ocho. Hoy nos hemos caído las siete.",
    "No hay mal que cien años dure, pero este ha durado seis intentos.",
    "Hoy el diccionario nos ha mirado por encima del hombro.",
    "Quien juega con fuego se quema los dedos; hoy nos hemos quemado enteros.",
    "Día de los que se recuerdan, y no para bien.",
    "Todo mi gozo en un pozo.",
    "La desgracia no es lo que puede evitarse, sino lo que no puede serlo.",
    "Hoy hemos aprendido palabras nuevas, todas a golpes.",
    "A cualquier dolencia es remedio la paciencia, y hoy hemos necesitado mucha.",
    "Hoy la palabra ha jugado sucio y encima ha ganado.",
    "Quien canta su mal espanta. Cantad, que hay motivo.",
)

# ─────────────────────────────────────────────────────────────────────────────
# Quien manda. Llevan `{jugador}`.
# ─────────────────────────────────────────────────────────────────────────────

#: Para el líder del marcador.
LIDER_DEL_MARCADOR: tuple[str, ...] = (
    "Manda quien puede y no quien quiere: hoy manda {jugador}.",
    "{jugador} arriba, y los demás mirando el escaparate.",
    "Cada gallo en su muladar, y el muladar es de {jugador}.",
    "Quien la sigue la consigue, y {jugador} no ha dejado de seguirla.",
    "{jugador} va primero y no parece que le pese.",
    "A rey muerto, rey puesto; de momento el rey es {jugador}.",
    "Genio y figura hasta la sepultura: {jugador} sigue arriba.",
    "El que algo quiere, algo le cuesta. A {jugador} le está costando poco.",
    "{jugador} manda en la tabla; en el álbum ya veremos.",
    "Más vale pájaro en mano, y {jugador} tiene la jaula llena.",
    "Quien guarda, halla; {jugador} lleva meses guardando.",
    "{jugador} lidera con la tranquilidad de quien no lee el marcador.",
    "El que ha desplazado la montaña empezó por las piedras pequeñas. {jugador} sigue en las piedras.",
    "De momento {jugador}, y que nadie se acostumbre.",
    "{jugador} en cabeza: disfrutadlo, que los meses son cortos.",
)

#: Para el líder del álbum de figuras.
LIDER_DEL_ALBUM: tuple[str, ...] = (
    "{jugador} pinta más que el resto con la mitad de las letras.",
    "Bonito el álbum de {jugador}; el resto, arte abstracto sin querer.",
    "{jugador} no juega al Wordle, expone.",
    "En el álbum manda {jugador}, que además no lo hace a propósito.",
    "{jugador} dibuja mejor perdiendo que nosotros ganando.",
    "Las apariencias engañan, pero el álbum de {jugador} no.",
    "{jugador} lidera el único ranking donde fallar tiene premio.",
    "Obras son amores, y {jugador} lleva unas cuantas.",
    "{jugador} arriba en figuras: el talento no se elige, se dibuja.",
    "El álbum es de {jugador} y no admite discusión estética.",
    "{jugador} colecciona lo que los demás tiramos.",
    "No es oro todo lo que reluce, pero el álbum de {jugador} brilla.",
    "{jugador} manda en belleza; en puntos, otra conversación.",
    "Quien no arriesga no gana, y {jugador} arriesga hasta la cuadrícula.",
    "{jugador} lidera el álbum, que es como ganar sin que cuente.",
)

# ─────────────────────────────────────────────────────────────────────────────
# Menciones que dependen de las señales del canal. Llevan `{jugador}`.
# Ocho por registro y no quince: salen en una minoría de las jornadas, así que rotan más despacio.
# ─────────────────────────────────────────────────────────────────────────────

MADRUGADOR: tuple[str, ...] = (
    "🐓 {jugador} ha publicado con el café aún caliente.",
    "🐓 A quien madruga, Dios le ayuda: {jugador} abrió la jornada.",
    "🐓 {jugador} llegó antes que nadie, como quien no quiere la cosa.",
    "🐓 {jugador} ya había jugado cuando el resto dormíamos.",
    "🐓 Primero en llegar: {jugador}.",
    "🐓 {jugador} no juega al Wordle, lo desayuna.",
    "🐓 {jugador} abrió el día y dejó el listón puesto.",
    "🐓 El gallo de hoy se llama {jugador}.",
)

REZAGADO: tuple[str, ...] = (
    "🌙 {jugador} lo ha dejado para el último minuto, como siempre.",
    "🌙 Las cosas de palacio van despacio, y {jugador} también.",
    "🌙 {jugador} ha publicado cuando ya no quedaba nadie mirando.",
    "🌙 Nunca es tarde si la dicha es buena, {jugador}.",
    "🌙 {jugador} cerró la jornada por la puerta de atrás.",
    "🌙 {jugador} juega al Wordle como quien paga los impuestos: el último día.",
    "🌙 Último en llegar: {jugador}.",
    "🌙 {jugador} llegó tarde pero llegó, que es más de lo que se puede decir de otros.",
)

MAS_APLAUDIDO: tuple[str, ...] = (
    "Lo más aplaudido del día es de {jugador}: {dato}.",
    "Nadie ha recibido más reacciones que {jugador}: {dato}.",
    "Lluvia de reacciones sobre {jugador}: {dato}.",
    "El canal se ha puesto en pie por {jugador}: {dato}.",
    "Ovación para {jugador}, con {dato}.",
    "{jugador} se lleva los aplausos del día: {dato}.",
    "Lo de {jugador} ha gustado, y se ha notado: {dato}.",
    "{dato} para {jugador}. El grupo ha votado con el dedo.",
)

MAS_COMENTADO: tuple[str, ...] = (
    "El hilo del día lo ha montado {jugador}: {dato}.",
    "Lo de {jugador} ha dado conversación: {dato} en su hilo.",
    "{jugador} ha abierto debate y ha durado: {dato}.",
    "El tema del día lo ha puesto {jugador}, con {dato}.",
    "Hoy se ha hablado sobre todo de lo de {jugador}: {dato}.",
    "{jugador} lanzó la piedra y el hilo hizo el resto: {dato}.",
    "Hilo del día, cortesía de {jugador}: {dato}.",
)

AUSENTE: tuple[str, ...] = (
    "🫥 De {jugador} no se sabe nada desde hace un rato.",
    "🫥 {jugador} hoy no se ha presentado.",
    "🫥 Donde no me llaman, para nada me querrán: hoy {jugador} no ha venido.",
    "🫥 Se echa de menos a {jugador}, o eso decimos.",
    "🫥 {jugador} se ha tomado el día libre sin avisar.",
    "🫥 Ni rastro de {jugador} en el canal.",
    "🫥 {jugador} ha decidido que hoy no era su día. Ni lo ha intentado.",
    "🫥 Falta {jugador}, y el marcador lo nota.",
)

# ─────────────────────────────────────────────────────────────────────────────
# El meme del día: **plantillas de texto, nunca imágenes.**
#
# Se nombra la forma del meme y se rellena con los datos de la jornada. No se publica ninguna imagen y no se
# cita ningún guion: subir una imagen ajena al canal desde un bot que tiene `files:write` es un problema de
# derechos y de permisos a la vez, y la plantilla en texto consigue el mismo chiste sin ninguno de los dos.
#
# Cada entrada declara la CONDICIÓN que la dispara. La implementación evalúa las condiciones en orden y usa
# la primera que se cumpla; si no se cumple ninguna, no hay meme del día y no pasa nada.
# ─────────────────────────────────────────────────────────────────────────────

#: `(condicion, plantilla)`. Las condiciones se implementan en el módulo que compone el resumen, no aquí:
#: este fichero es solo el texto. Los huecos disponibles van documentados por condición.
MEMES: tuple[tuple[str, str], ...] = (
    (
        "clavada-en-una",
        "🎯 *Meme del día:* nadie. Absolutamente nadie. {jugador}: «lo he sacado en 1».",
    ),
    (
        "solo-uno-lo-saca",
        "🎯 *Meme del día:* el grupo entero al fondo del pozo y {jugador} saludando desde el borde.",
    ),
    (
        "todos-fallan",
        "🎯 *Meme del día:* esto ya no es un juego, es una encerrona. {faltan} de {total} sin resolver.",
    ),
    (
        "todos-el-mismo-numero",
        "🎯 *Meme del día:* {total} personas, {intentos} intentos cada una. O nos copiamos o somos el mismo.",
    ),
    (
        "el-lider-se-hunde",
        "🎯 *Meme del día:* {jugador} lidera la temporada y hoy ha firmado un {intentos}. El pedestal resbala.",
    ),
    (
        "el-ultimo-clava",
        "🎯 *Meme del día:* {jugador}, último de la tabla, resolviendo en {intentos} como si nada. Nos vamos a enterar.",
    ),
    (
        "remontada-del-dia",
        "🎯 *Meme del día:* {jugador} ha pasado de comparsa a protagonista en una sola jornada.",
    ),
    (
        "empate-multitudinario",
        "🎯 *Meme del día:* {cuantos} empatados arriba. Hoy no hay rey, hay asamblea.",
    ),
    (
        "figura-imposible",
        "🎯 *Meme del día:* {jugador} ha fallado tanto que le ha salido arte. {figura} y sin querer.",
    ),
    (
        "nadie-dibuja-nada",
        "🎯 *Meme del día:* {total} cuadrículas y ni una figura. Hoy el álbum es una pared en blanco.",
    ),
    (
        "el-grupo-al-completo",
        "🎯 *Meme del día:* {total} de {total}. Hoy no falta nadie, y eso también da miedo.",
    ),
    (
        "dia-de-dos-mundos",
        "🎯 *Meme del día:* unos en {mejor} y otros en {peor}. La misma palabra, dos realidades.",
    ),
)


# ─────────────────────────────────────────────────────────────────────────────
# La pelea por el primer puesto. Llevan `{a}`, `{b}` y `{cifra}`.
#
# Solo salen cuando hay pelea de verdad —empate en cabeza o una ventaja que se remonta en una jornada—, así
# que no hace falta que sean quince: rotan despacio porque aparecen poco.
# ─────────────────────────────────────────────────────────────────────────────

#: Empate exacto en el primer puesto. Es lo que el titular de la web contaba como «le sigue a 0,00».
RIVALIDAD_EMPATE: tuple[str, ...] = (
    "🔥 *Pelea por el primer puesto:* {a} y {b} empatados a {cifra}. No se sacan ni una décima.",
    "🔥 *Pelea por el primer puesto:* {a} y {b} van clavados a {cifra}. El que falle primero, se queda.",
    "🔥 *Pelea por el primer puesto:* {a} y {b} a {cifra} los dos. La temporada se decide entre ellos.",
    "🔥 *Pelea por el primer puesto:* nadie manda. {a} y {b} comparten el primer puesto a {cifra}.",
    "🔥 *Pelea por el primer puesto:* {a} y {b}, {cifra} cada uno. Esto lo desempata una sola jornada.",
    "🔥 *Pelea por el primer puesto:* {a} contra {b}, y de momento tablas a {cifra}.",
    "🔥 *Pelea por el primer puesto:* {a} y {b} empatados a {cifra}. Que no pestañee ninguno.",
    "🔥 *Pelea por el primer puesto:* {cifra} y {cifra}. {a} y {b} no se despegan.",
)

#: Ventaja tan corta que se remonta en una jornada.
RIVALIDAD_PELEA: tuple[str, ...] = (
    "🔥 *Pelea por el primer puesto:* {a} lidera, pero {b} le respira en el cuello a {cifra}.",
    "🔥 *Pelea por el primer puesto:* {a} va primero por {cifra}. Una jornada mala y cambia el orden.",
    "🔥 *Pelea por el primer puesto:* {b} está a {cifra} de {a}. Eso se remonta en un día.",
    "🔥 *Pelea por el primer puesto:* {a} manda por {cifra} sobre {b}, que es no mandar mucho.",
    "🔥 *Pelea por el primer puesto:* {cifra} separan a {a} de {b}. Nada, básicamente.",
    "🔥 *Pelea por el primer puesto:* {a} delante, {b} pegado a {cifra}. Sin distancia para relajarse.",
    "🔥 *Pelea por el primer puesto:* {a} aguanta arriba por {cifra} sobre {b}.",
    "🔥 *Pelea por el primer puesto:* {b} a {cifra} de {a}: esto no está decidido.",
)

#: Empate a tres o más. **No se nombran todos**: por encima de dos, la lista hace crecer el mensaje con el
#: grupo, que es la propiedad que un test de otro slice protege.
RIVALIDAD_MONTON: tuple[str, ...] = (
    "🔥 *Pelea por el primer puesto:* {cuantos} empatados en cabeza a {cifra}. Hoy no hay rey.",
    "🔥 *Pelea por el primer puesto:* {cuantos} comparten el primer puesto a {cifra}. Asamblea.",
    "🔥 *Pelea por el primer puesto:* {cuantos} a {cifra} y ninguno se despega.",
    "🔥 *Pelea por el primer puesto:* {cuantos} personas empatadas arriba. Esto es un pelotón, no un podio.",
)


# ─────────────────────────────────────────────────────────────────────────────
# Las líneas del bloque de la jornada. Formato de lista, contenido de comentario: se leen de un vistazo en la
# notificación del móvil y a la vez cuentan lo que pasó, en vez de rotular un dato.
#
# `{cifra}` es la dificultad del día y `{media}` la de la temporada. Los cortes están medidos sobre 166
# jornadas: ±0,40 deja el 55% de los días en «normal», y decir «más difícil de lo habitual» pasa una de cada
# cinco jornadas — con ±0,20 pasaría casi siempre y dejaría de informar.
# ─────────────────────────────────────────────────────────────────────────────

DIFICULTAD_MUCHO_MAS_DURA: tuple[str, ...] = (
    "Hoy la palabra ha sido mucho más difícil de lo habitual: {cifra} de media frente a {media}.",
    "Hoy nos ha pasado por encima: {cifra} de media contra los {media} de la temporada.",
    "Palabra de las que se recuerdan: {cifra} de media, y la temporada va en {media}.",
)

DIFICULTAD_MAS_DURA: tuple[str, ...] = (
    "Hoy la palabra ha sido algo más difícil de lo habitual: {cifra} de media frente a {media}.",
    "Hoy se ha vendido un poco más cara: {cifra} de media, contra {media} de la temporada.",
    "Día cuesta arriba, sin drama: {cifra} de media frente a {media}.",
)

DIFICULTAD_NORMAL: tuple[str, ...] = (
    "Hoy la palabra ha ido como suele: {cifra} de media, y la temporada va en {media}.",
    "Jornada de las de siempre: {cifra} de media frente a {media}.",
    "Hoy sin sorpresas: {cifra} de media, lo normal en esta temporada ({media}).",
)

DIFICULTAD_MAS_FACIL: tuple[str, ...] = (
    "Hoy la palabra se ha dejado querer: {cifra} de media frente a {media}.",
    "Día amable: {cifra} de media, por debajo de los {media} de la temporada.",
    "Hoy ha ido rodada: {cifra} de media contra {media}.",
)

DIFICULTAD_MUCHO_MAS_FACIL: tuple[str, ...] = (
    "Hoy la palabra ha venido a entregarse: {cifra} de media frente a {media}.",
    "Regalo del diccionario: {cifra} de media, y la temporada va en {media}.",
    "Hoy no ha habido partido: {cifra} de media contra {media}.",
)

#: Los mejores del día. `{jugador}` puede ser más de un nombre y `{intentos}` su nota.
MEJORES_DEL_DIA: tuple[str, ...] = (
    "Los mejores del día: {jugador}, en {intentos}.",
    "Lo han bordado {jugador}: {intentos} intentos.",
    "Arriba del todo hoy, {jugador}, con {intentos}.",
    "{jugador} se lleva la jornada con {intentos} intentos.",
)

#: El dibujo del día. `{emoji}` la figura y `{intentos}` lo que costó.
DIBUJO_DEL_DIA: tuple[str, ...] = (
    "El dibujo más bonito es de {jugador}: un {emoji} que le costó {intentos} intentos.",
    "Premio de belleza para {jugador}, con un {emoji} de {intentos} intentos.",
    "{jugador} ha dejado el mejor dibujo del día: {emoji}, en {intentos}.",
    "Lo más presentable de hoy lo firma {jugador}: {emoji} ({intentos} intentos).",
)

#: Quien abrió la jornada **con costumbre demostrada**: ha abierto la mayoría de las que se han leído.
APERTURA_HABITUAL: tuple[str, ...] = (
    "Como de costumbre, {jugador} ha madrugado: ha abierto {veces} de las últimas {total} jornadas.",
    "{jugador} otra vez el primero — {veces} de {total} jornadas lleva abriendo.",
    "El madrugador de siempre: {jugador}, {veces} aperturas en {total} jornadas.",
)

#: Quien abrió la jornada sin que sea costumbre.
APERTURA_SUELTA: tuple[str, ...] = (
    "{jugador} ha abierto la jornada.",
    "El primero en publicar hoy, {jugador}.",
    "Hoy ha dado el pistoletazo {jugador}.",
)

#: Quien la cerró tarde **y además con una nota muy por encima del grupo**. Es otro chiste que el de llegar
#: tarde, y mejor: el de haber visto lo que hacían los demás antes de jugar.
#:
#: Vivía en `comentarios.py` apoyado en `created_at`, que es la hora en que el cron escribió la fila y no la
#: de publicación: por lotes cada hora, con solo el 34% de los resultados de una jornada en minutos
#: distintos. Sobre ese dato, «el último en publicar» era casi ruido. Ahora se mide con la hora real del
#: canal, que es la que sostiene la insinuación.
CIERRE_TARDIO_CON_SUERTE: tuple[str, ...] = (
    "{jugador} la ha cerrado {horas} después, y con un {dato:.0f}. Habiendo visto los demás, claro.",
    "Curioso: {jugador} llega {horas} tarde y clava un {dato:.0f}. Nada que declarar.",
    "El último en publicar es {jugador}, {horas} después, y con un {dato:.0f}. Cosas del azar.",
    "{jugador} aparece {horas} más tarde con un {dato:.0f} debajo del brazo.",
)

#: Quien la cerró, cuando tardó lo suyo. `{horas}` es cuánto después del primero.
CIERRE_TARDIO: tuple[str, ...] = (
    "{jugador} la ha cerrado {horas} después.",
    "{jugador} apareció {horas} más tarde, como quien no quiere la cosa.",
    "El último, {jugador}, con {horas} de retraso sobre el primero.",
)

#: Los ausentes. `{jugador}` son hasta tres nombres y `{resto}` la coleta de «y otros N».
AUSENTES_DEL_DIA: tuple[str, ...] = (
    "{jugador}{resto} ni se han presentado hoy.",
    "Sin noticias de {jugador}{resto}.",
    "Hoy faltan {jugador}{resto}.",
    "{jugador}{resto} se han tomado el día libre.",
)


# ─────────────────────────────────────────────────────────────────────────────
# El berrinche: la pulla al sospechoso en tono de rabieta.
#
# **Van sobre el resultado, nunca sobre la persona.** El grupo es real, el canal es de trabajo y estos
# nombres son de compañeros identificables: la broma es «no me creo ese 2», no nada sobre quien lo hizo.
#
# Y están escritas **sin concordancia de número** —impersonales, o con el nombre suelto— a propósito: así la
# misma frase sirve para un sospechoso y para tres sin necesidad de una variante en plural, que es donde este
# diccionario ya se había equivocado una vez.
# ─────────────────────────────────────────────────────────────────────────────

BERRINCHE: tuple[str, ...] = (
    "Un {dato:.0f} de {jugador}. UN {dato:.0f}. Y el resto aquí sufriendo 🤨",
    "No me creo el {dato:.0f} de {jugador}. No me lo creo y no me lo vais a hacer creer 🤨",
    "Exijo repetir la jornada. Y que se revise el diccionario de {jugador} 🤨",
    "{jugador} otra vez arriba. Alguien tendría que hacer algo 🤨",
    "Pues yo digo que el {dato:.0f} de {jugador} no vale. Lo digo yo y ya está 🤨",
    "Un {dato:.0f} de {jugador}, y encima con esa cara de no haber roto un plato 🤨",
    "Que conste en acta mi protesta por el {dato:.0f} de {jugador} 🤨",
    "Reclamación formal al {dato:.0f} de {jugador}. Se admite a trámite 🤨",
    "Yo también quiero un {dato:.0f} como el de {jugador}. ¿Dónde se pide? 🤨",
    "El {dato:.0f} de {jugador}: aquí hay tongo y lo sabéis 🤨",
    "Al VAR con el {dato:.0f} de {jugador} 🤨",
    "Me niego a aceptar el {dato:.0f} de {jugador}. Y lo digo pataleando 🤨",
)


# ─────────────────────────────────────────────────────────────────────────────
# ESTADO DE ÁNIMO DE LA JORNADA
#
# El problema que resuelve: cada bloque del mensaje elegía su frase de su propio registro sin saber qué
# habían elegido los demás, así que un día salía una línea sarcástica, otra celebratoria y un cierre
# resignado. El mensaje sonaba a tres personas distintas. Ahora **una jornada tiene un estado de ánimo** y
# todas las piezas con tono se sacan de él.
#
# **Solo las piezas con tono varían por estado.** Sub-agrupar los quince registros por cinco estados serían
# setenta y cinco grupos y unas mil frases: no es realista y envejecería mal. Los hechos —mejores, dibujo,
# horarios, ausentes— se quedan neutros, y el tono lo pone el conector que los encadena.
#
# Tres estados reutilizan los registros de día que ya existían, porque su tono coincide.
# ─────────────────────────────────────────────────────────────────────────────

INCREDULIDAD = "incredulidad"
EPICA = "epica"
DERROTA = "derrota"
RUTINA = "rutina"
FIESTA = "fiesta"

#: La frase que cierra el comentario, por estado de ánimo.
#:
#: **Cultura pop, no refranero.** Los proverbios siguen llevando la viñeta de dificultad, que es informativa;
#: el cierre es el remate y tiene que tener gancho. Videojuegos, series, cine, televisión de aquí, deporte y
#: tono de prensa rosa — el registro con el que este grupo habla de verdad.
#:
#: Y hay un beneficio de rebote: antes el cierre reutilizaba los registros de día, que comparten frase base
#: con las de la viñeta de dificultad, así que el mismo día podía publicar «Hoy la palabra se ha dejado
#: querer» dos veces, arriba con cifras y abajo sola. Con registros propios eso no puede pasar.
#:
#: **Son alusiones escritas para esto, no citas.** Referenciar un fenómeno cultural o un título es libre;
#: copiar el diálogo de un guion no lo es, y este repositorio es público. Tampoco se nombra a personas
#: reales: el tono de prensa rosa se consigue con el registro —exclusiva, portada, tertulia— sin meter a
#: nadie de verdad en una frase que se publica sola cada tarde.
CIERRE: dict[str, tuple[str, ...]] = {
    INCREDULIDAD: (
        "{jugador}, esta palabra es tu padre. Y aun así la has sacado en {dato:.0f}.",
        "Hay dos pastillas y {jugador} se ha tomado las dos.",
        "La palabra estaba en otro castillo, y {jugador} tenía el mapa.",
        "Ni con el comodín del público se saca eso en {dato:.0f}.",
        "El rosco entero en {dato:.0f} intentos. Hasta aquí puedo leer.",
        "{jugador} lo llevaba escrito en la mano. ¿Qué no? Te digo yo a ti que sí.",
        "Un {dato:.0f} de {jugador}. Ahora vas y lo cascas.",
        "Aquí hay impostor, y no ha publicado su cuadrícula.",
        "El pastel es mentira, y el {dato:.0f} de {jugador} también.",
        "Un poquito de por favor con ese {dato:.0f}, {jugador}.",
        "{jugador} ha resuelto en {dato:.0f} y se ha quedado tan ancho. Me mina la moral.",
        "Sayonara, dificultad: {jugador} en {dato:.0f}.",
        "Esto no lo aclara una tertulia de tarde entera.",
        "Que se sepa: {jugador} ha hecho un {dato:.0f} y no lo vamos a dejar pasar.",
        "Modo dios activado, y sin que nadie haya escrito el código.",
        "{jugador} la ha liado parda, pero de las buenas.",
        "Un {dato:.0f} limpio. Demasiado limpio, señoría.",
        "Yo he visto cosas que no creeríais: un {dato:.0f} de {jugador}.",
        "{jugador} le ha hecho al diccionario una oferta que no ha podido rechazar.",
        "Aquí hay gato encerrado, y el gato se llama {jugador}.",
        "{jugador} ha hecho un {dato:.0f}. ¿Pero qué pasa, qué invento es este?",
    ),
    EPICA: (
        "{jugador} ha sacado la espada de la piedra delante de todos.",
        "Este es mi momento y quiero vivirlo, ha dicho {jugador}.",
        "No pasarás, dijo la palabra. Y {jugador} pasó.",
        "Sayonara, baby: {dato:.0f} intentos y a casa.",
        "Que la fuerza le acompañe, que hoy le ha acompañado.",
        "Solo puede quedar uno, y hoy ha sido {jugador}.",
        "{jugador} ha vuelto del futuro con la respuesta puesta.",
        "El rosco completo, y con tiempo de sobra.",
        "{jugador} es el rey del mundo, y lo ha dicho en {dato:.0f}.",
        "Jefe final al primer intento y sin gastar una vida.",
        "{jugador} se ha pasado el nivel del agua sin rechistar.",
        "Corre, {jugador}, corre: {dato:.0f} intentos y a la meta.",
        "Épica de las de Iniesta en el 116, con el estadio en pie.",
        "Es peligroso ir solo, y {jugador} ha ido igual.",
        "Esto va directo al vídeo de mejores momentos del año.",
        "Hoy {jugador} nos ha salvado a todos. Bella ciao, palabra.",
        "Palabra dura, {dato:.0f} intentos, cero excusas.",
        "Siempre nos quedará esta jornada.",
        "Boss derrotado, y sin gastar pociones.",
        "Un pequeño paso para {jugador}, un gran salto para el marcador.",
        "La palabra ha pedido la hora y {jugador} no se la ha dado.",
    ),
    DERROTA: (
        "Game over, y sin monedas para otra.",
        "La palabra estaba en otro castillo, y el castillo estaba cerrado.",
        "You died. Y otra vez. Y otra.",
        "Spain, zero points.",
        "Chanquete no ha muerto: nos ha ganado.",
        "La vaquilla nos ha pasado por encima.",
        "El rosco entero en blanco.",
        "Hoy la palabra nos ha minado la moral.",
        "Para dentro, Romerales: de esta no salimos.",
        "Un poquito de por favor, diccionario.",
        "El pastel era mentira.",
        "Hasta luego, Mari Carmen: nos vamos sin puntuar.",
        "Si me queréis, irse. Hoy no hay nada que ver.",
        "La hemos liado parda, y no de las buenas.",
        "Vuelta al último punto de guardado. Otra vez.",
        "Fuera de la cocina, todos. Hoy no se salva ni uno.",
        "Ni dando cera ni puliendo cera.",
        "Houston, hemos tenido un problema de cinco letras.",
        "Hoy no había ni modo fácil ni piedad.",
        "Hemos venido a sufrir, y la palabra ha cumplido.",
        "Yo divinamente, dijo nadie hoy.",
    ),
    RUTINA: (
        "Iguales.",
        "Capítulo de relleno, de los que no pasa nada.",
        "Hoy sin exclusiva: portada tranquila.",
        "Hoy sin tomate: todos correctos y aburridos.",
        "Episodio de transición. La temporada sigue.",
        "Nivel de tutorial, sin sobresaltos.",
        "Ni drama ni gloria. Un, dos, tres, responda otra vez mañana.",
        "Partido de media tabla, con poca gente en la grada.",
        "Elemental: hoy no hay caso.",
        "Empate a cero y a casa.",
        "Hoy la trama principal no ha avanzado.",
        "Jornada que no sale ni en el resumen del año.",
        "Día de los de repetir capítulo sin enterarte.",
        "El diccionario ha cumplido el expediente.",
        "Hoy nadie ha subido y nadie ha bajado.",
        "Capítulo de los que se ven en diagonal y sin sonido.",
        "Trámite. Siguiente.",
        "Hoy el guionista estaba de baja.",
        "Nada que declarar, señoría.",
        "Y hasta aquí puedo leer: no ha pasado nada.",
        "Hoy la palabra ha venido a fichar.",
    ),
    FIESTA: (
        "Modo fácil con vidas infinitas.",
        "Rosco resuelto antes del primer anuncio.",
        "Sayonara, dificultad.",
        "La palabra venía con las instrucciones puestas.",
        "Este es mi momento y quiero vivirlo, dice el grupo entero.",
        "Hoy no hacía falta ni el comodín.",
        "Nivel bonus, y con monedas de regalo.",
        "Hoy hasta el tutorial nos ha aplaudido.",
        "Esto ha sido el chupito que invita la casa.",
        "Hoy la palabra se ha entregado sin resistencia.",
        "Día redondo: portada en color y sin tertulia.",
        "Victoria cómoda, de las de cambiar de canal en el minuto ochenta.",
        "Pan comido. Y de los de nadie es perfecto, pero hoy casi.",
        "Hoy jugábamos con el marcador a favor desde el principio.",
        "Fin de fiesta, con confeti incluido.",
        "Hoy el diccionario tenía el día bueno.",
        "Vine, vi y la palabra se rindió.",
        "Palabra de las que se sacan entre dos pisos del ascensor.",
        "Día de vino y rosas para el vocabulario.",
        "Hoy la dificultad estaba de vacaciones.",
        "Se cierra la jornada con abrazo de grupo y confeti de Eurovisión.",
    ),
}

#: Conectores para encadenar la segunda línea con la primera cuando hablan de lo mismo. Es lo que convierte
#: una lista de datos en un narrador con una idea en la cabeza.
CONECTORES: dict[str, tuple[str, ...]] = {
    INCREDULIDAD: ("Y encima", "Y por si faltaba algo", "Y ya que estamos", "Faltaba decir que"),
    EPICA: ("Y además", "Y no solo eso", "Para colmo", "Y encima"),
    DERROTA: ("Y aun así", "Al menos", "Eso sí", "Por lo menos"),
    RUTINA: ("Además", "Y", "También", "Por cierto"),
    FIESTA: ("Y encima", "Y además", "Y de paso", "Y para redondearlo"),
}


# ─────────────────────────────────────────────────────────────────────────────
# EL RELEVO EN CABEZA
#
# Cambiar de líder es lo que de verdad enciende una liga, y hasta ahora el mensaje no lo decía: publicaba el
# marcador nuevo como si nada hubiera pasado. Se detecta **comparando el marcador con y sin la jornada de
# hoy**, así que no hace falta guardar historia: es cálculo, y da lo mismo cuantas veces se repita.
#
# Registro de rivalidad y competición, con la misma técnica que el cierre: la referencia se reescribe para el
# juego en lugar de citarse. `{nuevo}` es quien pasa a mandar y `{anterior}` quien se queda.
# ─────────────────────────────────────────────────────────────────────────────

CAMBIO_DE_LIDER: tuple[str, ...] = (
    "👑 *Relevo en cabeza:* {nuevo} desbanca a {anterior}. Solo puede quedar uno.",
    "👑 *Relevo en cabeza:* {anterior} ha perdido el trono y {nuevo} ya se ha sentado.",
    "👑 *Relevo en cabeza:* {nuevo} adelanta a {anterior} en la última curva.",
    "👑 *Relevo en cabeza:* se cae {anterior}, sube {nuevo}. Esto es una liga, no un paseo.",
    "👑 *Relevo en cabeza:* {nuevo} le ha quitado el cinturón a {anterior}.",
    "👑 *Relevo en cabeza:* {anterior} fuera, {nuevo} dentro. El clásico cambia de dueño.",
    "👑 *Relevo en cabeza:* {nuevo} manda ahora, y {anterior} tendrá algo que decir mañana.",
    "👑 *Relevo en cabeza:* {nuevo} ha hecho el adelantamiento del año sobre {anterior}.",
    "👑 *Relevo en cabeza:* {anterior} llevaba la corona prestada. {nuevo} ha venido a recogerla.",
    "👑 *Relevo en cabeza:* {nuevo} gana el pulso a {anterior}. Segunda vuelta mañana.",
    "👑 *Relevo en cabeza:* golpe de estado limpio de {nuevo} contra {anterior}.",
    "👑 *Relevo en cabeza:* {anterior} ha aguantado lo que ha podido. Ahora manda {nuevo}.",
)

#: Cuando quien manda **aguanta** un intento de adelantamiento, que también es rivalidad.
LIDER_AGUANTA: tuple[str, ...] = (
    "👑 *Sigue mandando {nuevo}*, que ha aguantado el asalto de {anterior}.",
    "👑 *{nuevo} defiende el trono* de {anterior} por muy poco.",
    "👑 *{nuevo} aguanta arriba*: {anterior} se ha quedado a las puertas.",
    "👑 *Nada que hacer, {anterior}*: {nuevo} sigue mandando.",
)


# ─────────────────────────────────────────────────────────────────────────────
# EL DÍA DE ALGUIEN
#
# Cada bloque elige a su mejor candidato por separado, y cuando coincide la misma persona en varios el mensaje
# la nombra una y otra vez: medido en la jornada 1681, alguien salía **siete veces** y leído junto parecía un
# monográfico. Cada línea era correcta; el conjunto, no.
#
# Cuando alguien es **protagonista único** de dos o más reconocimientos, sus líneas se fusionan en una. No se
# reparten los premios a otra gente: eso sería falsear quién ganó qué.
# ─────────────────────────────────────────────────────────────────────────────

DIA_DE: tuple[str, ...] = (
    "Día de {jugador}: {logros}.",
    "{jugador} se lo ha llevado casi todo: {logros}.",
    "Pleno de {jugador}: {logros}.",
    "{jugador} firma la jornada: {logros}.",
    "Hoy todo apunta a {jugador}: {logros}.",
    "{jugador} arrasa: {logros}.",
    "La jornada tiene dueño, {jugador}: {logros}.",
    "{jugador} no ha dejado nada para los demás: {logros}.",
)

#: Cómo se nombra cada reconocimiento dentro de una línea fusionada. Cortos a propósito: la gracia de fundir
#: tres líneas en una se pierde si la línea resultante es más larga que las tres.
LOGROS_DEL_DIA: dict[str, str] = {
    # `{dato}` es opcional: solo la mejor nota tiene una cifra que aporte. Fusionar no puede costar
    # información — la línea decía con cuántos intentos se ganó la jornada y hay un test que lo exige.
    "mejores": "la mejor nota (en {dato})",
    "dibujo": "el mejor dibujo",
    "aplaudido": "la ovación del canal",
    "comentado": "el hilo del día",
}
