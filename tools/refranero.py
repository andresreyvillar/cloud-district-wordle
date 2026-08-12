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
    "Lo de {jugador} ha levantado al canal.",
    "El grupo ha hablado, y ha dicho {jugador}.",
    "{jugador} se lleva los aplausos del día.",
    "Nadie ha aplaudido más que a {jugador}.",
    "A {jugador} le han llovido las reacciones, y con motivo.",
    "{jugador} ha hecho el ruido del día.",
    "Ovación para {jugador}.",
    "Hoy el canal se ha puesto en pie por {jugador}.",
)

MAS_COMENTADO: tuple[str, ...] = (
    "{jugador} ha montado el hilo del día.",
    "Lo de {jugador} ha dado más conversación que el propio Wordle.",
    "{jugador} ha abierto debate, y el debate ha durado.",
    "El tema del día lo ha puesto {jugador}.",
    "{jugador} ha conseguido que el canal hable de otra cosa.",
    "Hoy se ha hablado sobre todo de {jugador}.",
    "{jugador} lanzó la piedra y el hilo hizo el resto.",
    "Hilo del día, cortesía de {jugador}.",
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

#: La frase que cierra el comentario, por estado.
CIERRE: dict[str, tuple[str, ...]] = {
    INCREDULIDAD: (
        "En {dato:.0f} intentos no se acierta: se recuerda.",
        "Yo esto lo dejo aquí y que cada uno piense lo que quiera.",
        "Un día alguien nos explicará cómo se hace un {dato:.0f}.",
        "Nadie resuelve en {dato:.0f} por casualidad. En fin.",
        "Que quede constancia de nuestra perplejidad colectiva.",
        "Seguiremos investigando.",
        "La comisión de investigación se reúne mañana.",
        "Y así, sin más explicaciones, se cerró la jornada.",
    ),
    EPICA: (
        "Días como hoy son los que se cuentan luego.",
        "La palabra se defendió, pero no le sirvió de nada.",
        "Hoy hubo partido de verdad.",
        "Al que ha desplazado la montaña hay que reconocérselo.",
        "Cáete siete veces, levántate ocho. Hoy alguien se levantó.",
        "De estas jornadas se sale con galones.",
        "Hoy la palabra encontró la horma de su zapato.",
        "Quien la sigue la consigue, y hoy se ha visto.",
    ),
    DERROTA: DIA_DURO,
    RUTINA: DIA_NORMAL,
    FIESTA: DIA_FACIL,
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
