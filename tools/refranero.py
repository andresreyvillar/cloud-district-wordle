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
MEMES: dict[str, tuple[str, ...]] = {
    # La jornada en que alguien lo clava a la primera.
    "clavada-en-una": (
        "🎯 *Meme del día:* {jugador} ha metido el código Konami y la palabra ha salido sola.",
        "🎯 *Meme del día:* {jugador} en 1. Esto o es telepatía o hay que revisar el sorteo.",
        "🎯 *Meme del día:* modo dios activado. {jugador} en 1, y sin escribir el truco dos veces.",
        "🎯 *Meme del día:* nadie. Absolutamente nadie. {jugador}: «lo he sacado en 1».",
        "🎯 *Meme del día:* {jugador} ha visto la Matrix: ni ha tenido que esquivar las balas.",
        "🎯 *Meme del día:* {jugador} ha abierto el juego, ha escrito una palabra y se ha ido a desayunar.",
        "🎯 *Meme del día:* no puedor, decía Chiquito. {jugador} sí podor: uno.",
        "🎯 *Meme del día:* un intento. Uno. {jugador}, explícate.",
        "🎯 *Meme del día:* {jugador} ha resuelto el rosco con la primera pregunta. Pasapalabra se cancela.",
        "🎯 *Meme del día:* {jugador} no ha jugado al Wordle, ha jugado a la lotería y le ha tocado.",
        "🎯 *Meme del día:* «hasta aquí puedo leer». {jugador} lo ha sacado en 1 y no cuenta más.",
        "🎯 *Meme del día:* el resto pensando la primera palabra y {jugador} ya recogiendo.",
        "🎯 *Meme del día:* {jugador} ha hecho un Iniesta: primer toque y a la red.",
        "🎯 *Meme del día:* {jugador} lo ha sacado en 1 y no piensa dar explicaciones.",
        "🎯 *Meme del día:* {jugador} entra en Super Saiyan directamente, sin la fase de gritar.",
        "🎯 *Meme del día:* {jugador}, primer intento, palabra correcta. Aquí se ha roto algo.",
        "🎯 *Meme del día:* efectividad máxima. {jugador} en 1, y encima era del tipo bueno.",
        "🎯 *Meme del día:* nos hemos levantado todos para nada. {jugador} ya lo tenía en 1.",
        "🎯 *Meme del día:* que la Fuerza os acompañe al resto, porque a {jugador} le sobra: 1.",
        "🎯 *Meme del día:* {jugador} ha acertado en 1 y el resto seguimos siendo mortales.",
        "🎯 *Meme del día:* {jugador} ya lo sabía desde el principio, como el niño de El Sexto Sentido.",
        "🎯 *Meme del día:* {jugador} ha llamado a la puerta y estaba abierta. Un intento.",
        "🎯 *Meme del día:* un poquito de por favor con ese 1, {jugador}.",
        "🎯 *Meme del día:* {jugador} ha hecho la del Rubius: entrar, ganar y grabar el final.",
        "🎯 *Meme del día:* primera papeleta y bote. {jugador} se lleva el rosco entero.",
        "🎯 *Meme del día:* {jugador} ha usado el condensador de fluzo: ha llegado a la palabra antes de escribirla.",
        "🎯 *Meme del día:* sayonara, baby. {jugador} en 1 y se va.",
        "🎯 *Meme del día:* {jugador} ha hecho un hadouken y la palabra ha caído a la primera.",
        "🎯 *Meme del día:* mosquis. {jugador} lo ha sacado en 1.",
        "🎯 *Meme del día:* {jugador}: «Juan Cuesta, presidente de esta nuestra comunidad». Y de este uno intento.",
        "🎯 *Meme del día:* IDDQD. {jugador} ha jugado con invulnerabilidad activada.",
        "🎯 *Meme del día:* {jugador} ha metido wololo y la palabra se ha convertido sola.",
        "🎯 *Meme del día:* esto es una oferta que no podíamos rechazar: {jugador}, en 1.",
        "🎯 *Meme del día:* {jugador} ha resuelto en 1. Yo no soy tonto, pero él tampoco.",
        "🎯 *Meme del día:* sul sul. {jugador} ha entrado, ha hecho su vida y ha ganado en 1.",
    ),
    # Uno resuelve y el grupo se estrella.
    "solo-uno-lo-saca": (
        "🎯 *Meme del día:* solo puede quedar uno, y hoy es {jugador}.",
        "🎯 *Meme del día:* superviviente único: {jugador}. Los demás, que descansen.",
        "🎯 *Meme del día:* {jugador} ha salido de la Fábrica. El resto seguimos dentro con el mono rojo.",
        "🎯 *Meme del día:* el grupo entero al fondo del pozo y {jugador} saludando desde el borde.",
        "🎯 *Meme del día:* {jugador} ha salido del laberinto y ha cerrado la puerta por fuera.",
        "🎯 *Meme del día:* {jugador} ha resuelto. El resto seguimos ahí abajo, gritando.",
        "🎯 *Meme del día:* el resto éramos los impostores. {jugador} ha hecho la tarea.",
        "🎯 *Meme del día:* de todos los que entraron, solo volvió {jugador}.",
        "🎯 *Meme del día:* YOU DIED para {total} menos uno. {jugador} sigue de pie.",
        "🎯 *Meme del día:* {jugador} arriba y el resto haciendo cola en el fondo.",
        "🎯 *Meme del día:* {jugador} en la tabla del Titanic. Y cabíamos todos, pero bueno.",
        "🎯 *Meme del día:* {jugador} lo saca y los demás firmamos el acta de defunción.",
        "🎯 *Meme del día:* en El Hoyo hay quien come y quien mira. Hoy comió {jugador}.",
        "🎯 *Meme del día:* uno de {total}. {jugador}, el último que quedaba en pie.",
        "🎯 *Meme del día:* {jugador} ha encontrado la salida del Laberinto del Fauno. Los demás no.",
        "🎯 *Meme del día:* {jugador} es el último superviviente. Créditos para los demás.",
        "🎯 *Meme del día:* los juegos del hambre han terminado: gana {jugador}.",
        "🎯 *Meme del día:* Chanquete ha muerto y {jugador} se ha quedado el barco.",
        "🎯 *Meme del día:* {jugador} ha desactivado la bomba en el último segundo. El resto, boom.",
        "🎯 *Meme del día:* hoy la palabra era un jefe final y solo {jugador} tenía el arma buena.",
        "🎯 *Meme del día:* {jugador} ha sobrevivido. Los demás nos hemos quedado en la paellera, riéndonos por no llorar.",
        "🎯 *Meme del día:* «soy Concha, entro» y entró solo {jugador}.",
        "🎯 *Meme del día:* {jugador} es el único que ha salido de Silent Hill. Nosotros seguimos en la niebla.",
        "🎯 *Meme del día:* el pastel era mentira para todos menos para {jugador}.",
        "🎯 *Meme del día:* {jugador} ha pasado el nivel y ha guardado partida. Los demás sin checkpoint.",
        "🎯 *Meme del día:* de la quinta del 84 solo volvió {jugador}. Los Goonies acabaron mejor.",
        "🎯 *Meme del día:* {jugador} ha desactivado la alarma; al resto nos han pillado en el pasillo.",
        "🎯 *Meme del día:* único superviviente: {jugador}. El resto, a la pantalla de continuar.",
    ),
    # Se estrella el grupo entero.
    "todos-fallan": (
        "🎯 *Meme del día:* Spain, zero points. {faltan} de {total} sin resolver.",
        "🎯 *Meme del día:* esto ya no es un juego, es una encerrona. {faltan} de {total} sin resolver.",
        "🎯 *Meme del día:* YOU DIED. {faltan} de {total}, en pantalla y con la musiquita.",
        "🎯 *Meme del día:* {faltan} de {total} fuera. Hoy ha ganado el diccionario.",
        "🎯 *Meme del día:* GAME OVER general: {faltan} de {total}. Insertad moneda.",
        "🎯 *Meme del día:* naufragio general. {faltan} de {total} sin sacarla.",
        "🎯 *Meme del día:* hoy el rosco se queda en la mesa. {faltan} de {total} nos vamos con la silla azul.",
        "🎯 *Meme del día:* {faltan} de {total} en blanco. Hoy no hemos jugado, nos han jugado.",
        "🎯 *Meme del día:* {faltan} de {total} caídos. Esto ha sido la Boda Roja de las palabras.",
        "🎯 *Meme del día:* pleno al fracaso: {faltan} de {total}. Un aplauso para la palabra.",
        "🎯 *Meme del día:* «el peor día de mi vida», y {faltan} de {total} firmamos el guion.",
        "🎯 *Meme del día:* {faltan} de {total} caídos. Ni uno. Ni uno solo.",
        "🎯 *Meme del día:* la palabra ha hecho un Chernóbil: {faltan} de {total} afectados.",
        "🎯 *Meme del día:* hoy la palabra nos ha hecho la cama a {faltan} de {total}.",
        "🎯 *Meme del día:* {faltan} de {total} eliminados. Ni con un comodín del público.",
        "🎯 *Meme del día:* hoy no ha ganado nadie. Amanece, que no es poco, y con {faltan} bajas.",
        "🎯 *Meme del día:* modo pesadilla sin avisar: {faltan} de {total} fuera.",
        "🎯 *Meme del día:* {faltan} de {total}. Hoy la banca ha ganado y encima se ha reído.",
        "🎯 *Meme del día:* esto ya no es un Wordle, es un Dark Souls. {faltan} de {total} en el suelo.",
        "🎯 *Meme del día:* {faltan} de {total} fuera. Qué follón.",
        "🎯 *Meme del día:* hoy no puedor nadie, pecadores de la pradera: {faltan} de {total}.",
        "🎯 *Meme del día:* {faltan} de {total}. Esto ha sido un apagón general y sin luz de emergencia.",
        "🎯 *Meme del día:* el rosco se queda con bote, y {faltan} de {total} a casa.",
        "🎯 *Meme del día:* {faltan} de {total}. Nos ha comido el T-Rex a todos, y sin ver la valla.",
        "🎯 *Meme del día:* hoy la palabra ha hecho un Alien: {faltan} de {total} y nadie oyó los gritos.",
        "🎯 *Meme del día:* {faltan} de {total} eliminados. Ni el comodín de la llamada.",
        "🎯 *Meme del día:* hoy hemos jugado al Buscaminas con los ojos cerrados: {faltan} de {total}.",
    ),
    # Todos coinciden en el mismo número.
    "todos-el-mismo-numero": (
        "🎯 *Meme del día:* {total} personas en {intentos}. Esto es el ataque de los clones.",
        "🎯 *Meme del día:* {total} personas, {intentos} intentos cada una. O nos copiamos o somos el mismo.",
        "🎯 *Meme del día:* {total} agentes Smith con el mismo {intentos}. Alguien ha copiado el código.",
        "🎯 *Meme del día:* {total} de {total} en {intentos}. Sospechosa unanimidad.",
        "🎯 *Meme del día:* {intentos} para {total}. Ni en Cuéntame había tanta unanimidad.",
        "🎯 *Meme del día:* todos en {intentos}. Hemos alcanzado la paz mundial.",
        "🎯 *Meme del día:* {intentos} intentos, {total} personas, cero discrepancias. Esto es un sindicato.",
        "🎯 *Meme del día:* {total} cuadrículas idénticas en {intentos}. Da un poco de miedo.",
        "🎯 *Meme del día:* {total} cuadrículas idénticas en {intentos}. Ctrl+C, Ctrl+V y buenas noches.",
        "🎯 *Meme del día:* {intentos} para todos. Hoy nadie destaca y nadie se hunde.",
        "🎯 *Meme del día:* el Consejo Jedi ha votado y sale {intentos}. Unanimidad de {total}.",
        "🎯 *Meme del día:* hoy somos un solo jugador con {total} cuentas: {intentos} todos.",
        "🎯 *Meme del día:* {total} de {total} en {intentos}. Black Mirror, capítulo del pueblo perfecto.",
        "🎯 *Meme del día:* {intentos} clavados los {total}. Esto lo ha organizado alguien.",
        "🎯 *Meme del día:* {total} personas en {intentos}. Esto es un Sims con el mismo rasgo para todos.",
        "🎯 *Meme del día:* {intentos} para los {total}. La comunidad de vecinos ha votado en bloque.",
        "🎯 *Meme del día:* {total} en {intentos}: hoy jugamos con la misma plantilla del PC Fútbol.",
        "🎯 *Meme del día:* {intentos} clavados. {total} de {total}. Nos han clonado en el laboratorio.",
        "🎯 *Meme del día:* {total} cuadrículas y un solo {intentos}. Esto es Camera Café con un solo plano.",
    ),
    # El líder de la temporada firma un desastre.
    "el-lider-se-hunde": (
        "🎯 *Meme del día:* rayo azul para {jugador}: iba primero y ha firmado un {intentos}.",
        "🎯 *Meme del día:* {jugador} lidera la temporada y hoy ha firmado un {intentos}. El pedestal resbala.",
        "🎯 *Meme del día:* {jugador}, líder de la temporada, hoy en {intentos}. Ícaro voló parecido.",
        "🎯 *Meme del día:* {jugador} manda en la tabla y hoy ha hecho {intentos}. Se avisa por megafonía.",
        "🎯 *Meme del día:* el que se sienta en el trono acaba pagándolo: {jugador} en {intentos}.",
        "🎯 *Meme del día:* el líder {jugador}, hoy en {intentos}. Todos tenemos un mal día, unos más público.",
        "🎯 *Meme del día:* Mufasa también iba primero. {jugador}, {intentos}.",
        "🎯 *Meme del día:* {jugador} arriba en la temporada, abajo en la jornada: {intentos}.",
        "🎯 *Meme del día:* {jugador} lidera y hoy ha hecho un {intentos}. La corona pesa, decía Cersei.",
        "🎯 *Meme del día:* {intentos} del líder. {jugador}, la corona pesa.",
        "🎯 *Meme del día:* {jugador} arriba en la general y hoy un {intentos}. Hasta Alonso tiene domingos malos.",
        "🎯 *Meme del día:* el líder {jugador} ha pinchado rueda a dos vueltas del final: {intentos}.",
        "🎯 *Meme del día:* boss fight perdido para {jugador}, líder y todo: {intentos}.",
        "🎯 *Meme del día:* {jugador} recordándonos que también es humano, con un {intentos}.",
        "🎯 *Meme del día:* {jugador} lidera y hoy ha firmado un {intentos}. Multiplícate por cero.",
        "🎯 *Meme del día:* hoy el líder {jugador} ha jugado como el resto. Peor: {intentos}.",
        "🎯 *Meme del día:* el líder {jugador} en {intentos}. Hasta luego, Lucas.",
        "🎯 *Meme del día:* {jugador} manda en la tabla y hoy ha hecho el ridículo con un {intentos}. Sin acritud.",
        "🎯 *Meme del día:* {jugador}, primero de la tabla, hoy un {intentos}. Se le ha caído el bote.",
        "🎯 *Meme del día:* {intentos} del líder {jugador}. Se le ha gripado el condensador de fluzo.",
        "🎯 *Meme del día:* {jugador} manda en la general y hoy ha hecho un {intentos}. Game over y a la máquina de al lado.",
        "🎯 *Meme del día:* el {intentos} de {jugador}, líder. Torrente conducía mejor.",
    ),
    # El último de la tabla clava la jornada.
    "el-ultimo-clava": (
        "🎯 *Meme del día:* {jugador} va último y hoy ha resuelto en {intentos}. Rocky se levantó igual.",
        "🎯 *Meme del día:* el farolillo rojo {jugador} en {intentos}. Empieza la remontada o el milagro.",
        "🎯 *Meme del día:* el farolillo rojo {jugador} en {intentos}. Karate Kid, primera lección.",
        "🎯 *Meme del día:* {jugador}, último de la tabla, resolviendo en {intentos} como si nada. Nos vamos a enterar.",
        "🎯 *Meme del día:* {jugador}, último de la tabla, {intentos} intentos. El Leicester empezó así.",
        "🎯 *Meme del día:* {jugador} va último y hoy ha hecho {intentos}. Cuidado con el de atrás.",
        "🎯 *Meme del día:* cuidado con {jugador}: va último y ha sacado el rayo azul. {intentos}.",
        "🎯 *Meme del día:* {intentos} del último clasificado. {jugador} ha venido a avisar.",
        "🎯 *Meme del día:* {jugador} cierra la clasificación y hoy firma un {intentos}. La Cenicienta avisó.",
        "🎯 *Meme del día:* {jugador} cierra la tabla y abre la jornada, con {intentos}.",
        "🎯 *Meme del día:* {jugador} va último y hoy en {intentos}. Dame el bote.",
        "🎯 *Meme del día:* el último de la lista, {jugador}, hoy el primero de la clase: {intentos}.",
        "🎯 *Meme del día:* último de la tabla y {intentos} intentos: {jugador} ha encontrado la espada maestra.",
        "🎯 *Meme del día:* último y en {intentos}: {jugador} ha activado el modo remontada.",
        "🎯 *Meme del día:* {jugador} cierra la clasificación y firma un {intentos}. Hadouken desde el fondo.",
        "🎯 *Meme del día:* {jugador} viene de atrás con un {intentos}. Que nadie mire el retrovisor.",
        "🎯 *Meme del día:* el farolillo rojo {jugador}, hoy en {intentos}. Pasapalabra, silla azul, y a por el rosco.",
        "🎯 *Meme del día:* el {intentos} de {jugador}, último clasificado. Aquí empieza su arco argumental.",
        "🎯 *Meme del día:* {intentos} del último, {jugador}. Modo remontada del PC Fútbol activado.",
        "🎯 *Meme del día:* {jugador} viene de atrás con un {intentos}. Esto es el arco de redención de la temporada 3.",
    ),
    # Nadie deja una figura reconocible.
    "nadie-dibuja-nada": (
        "🎯 *Meme del día:* {total} lienzos y ni una obra. Museo cerrado por inventario.",
        "🎯 *Meme del día:* {total} cuadrículas y ni una figura. Hoy el álbum es una pared en blanco.",
        "🎯 *Meme del día:* {total} cuadrículas y ni una figura. El Prado nos cierra la puerta.",
        "🎯 *Meme del día:* cero figuras en {total} cuadrículas. Hoy no somos artistas, somos oficinistas.",
        "🎯 *Meme del día:* cero obras en {total} lienzos. Bob Ross llorando en directo.",
        "🎯 *Meme del día:* {total} intentos de arte y ni un cuadro. El álbum sigue esperando.",
        "🎯 *Meme del día:* {total} cuadrículas de arte conceptual: la obra es que no hay obra.",
        "🎯 *Meme del día:* hoy nadie ha dibujado nada. {total} cuadrículas de puro trámite.",
        "🎯 *Meme del día:* ni un cuadro en {total}. Ni el Paint nos salva.",
        "🎯 *Meme del día:* hoy el álbum es una pared en blanco. {total} intentos y nada colgable.",
        "🎯 *Meme del día:* {total} cuadrículas sin figura. Museo cerrado, vuelvan mañana.",
        "🎯 *Meme del día:* cero obras en {total}. Ni con el pincel de dos pelos.",
        "🎯 *Meme del día:* arte moderno: {total} rectángulos y ninguna explicación.",
        "🎯 *Meme del día:* ni un cuadro en {total}. Se cancela la exposición y se devuelven las entradas.",
        "🎯 *Meme del día:* {total} cuadrículas y ni una figura. El Prado no coge ni una en depósito.",
        "🎯 *Meme del día:* {total} lienzos vacíos. Hoy el álbum es el Buscaminas sin destapar.",
        "🎯 *Meme del día:* hoy nadie ha dibujado nada: {total} cuadrículas de mármol gris.",
    ),
    # El grupo entero aparece.
    "el-grupo-al-completo": (
        "🎯 *Meme del día:* {total} de {total}. Vengadores, reuníos.",
        "🎯 *Meme del día:* {total} de {total}. Hoy no falta nadie, y eso también da miedo.",
        "🎯 *Meme del día:* asistencia perfecta, {total} de {total}. Esto es un Grand Prix con vaquilla.",
        "🎯 *Meme del día:* asistencia perfecta: {total} de {total}. ¿Quién ha convocado esto?",
        "🎯 *Meme del día:* {total} de {total} presentes. Junta de vecinos y no falta nadie.",
        "🎯 *Meme del día:* {total} de {total} presentes. Hoy no hay excusas que valgan.",
        "🎯 *Meme del día:* pleno de {total}. Hoy nadie se ha ido a la cama antes que la familia Telerín.",
        "🎯 *Meme del día:* pleno de asistencia, {total} de {total}. Se pasa lista y no falla nadie.",
        "🎯 *Meme del día:* {total} de {total} fichando. Ni en Gran Hermano hay tanto control.",
        "🎯 *Meme del día:* hoy hemos venido {total} de {total}. Ni una baja.",
        "🎯 *Meme del día:* {total} de {total}. Junta de vecinos, y esta vez con quórum.",
        "🎯 *Meme del día:* hoy hemos venido {total} de {total}. La banda está completa.",
        "🎯 *Meme del día:* asistencia perfecta de {total}. La familia Telerín no ha faltado ni uno.",
        "🎯 *Meme del día:* pleno de {total}. Hoy sí hay quien viva.",
        "🎯 *Meme del día:* {total} de {total} en línea. Esto es un Grand Prix con las doce vaquillas.",
        "🎯 *Meme del día:* {total} de {total}: la banda está completa y afinada.",
    ),
    # Empate multitudinario en cabeza.
    "empate-multitudinario": (
        "🎯 *Meme del día:* {cuantos} empatados arriba. Junta de vecinos, y sin presidente.",
        "🎯 *Meme del día:* {cuantos} empatados arriba. Hoy no hay rey, hay asamblea.",
        "🎯 *Meme del día:* {cuantos} en cabeza: esto es el Consejo Jedi, no un podio.",
        "🎯 *Meme del día:* {cuantos} en cabeza. Esto no es un podio, es un ascensor lleno.",
        "🎯 *Meme del día:* {cuantos} reyes a la vez. Juego de Tronos, temporada mala.",
        "🎯 *Meme del día:* {cuantos} compartiendo el primer puesto. Que alguien traiga más sillas.",
        "🎯 *Meme del día:* {cuantos} arriba. Que alguien saque el sorteo del Grand Prix.",
        "🎯 *Meme del día:* {cuantos} arriba y ninguno manda. Democracia directa.",
        "🎯 *Meme del día:* {cuantos} compartiendo el trono. Nadie manda y todos opinan.",
        "🎯 *Meme del día:* primer puesto para {cuantos}. El trofeo habrá que partirlo.",
        "🎯 *Meme del día:* {cuantos} arriba. Juan Cuesta, presidente de esta nuestra comunidad, tome nota.",
        "🎯 *Meme del día:* primer puesto para {cuantos}. Todos para uno y uno para todos.",
        "🎯 *Meme del día:* {cuantos} empatados: esto ya no es un podio, es la escalera del 21.",
        "🎯 *Meme del día:* primer puesto para {cuantos}. Que empiece la ronda de desempate del Un, Dos, Tres.",
        "🎯 *Meme del día:* {cuantos} en cabeza. Un poquito de por favor.",
        "🎯 *Meme del día:* {cuantos} compartiendo el trono. Vamos a necesitar más sillas azules.",
    ),
    # Alguien falla tanto que le sale una figura.
    "figura-imposible": (
        "🎯 *Meme del día:* {jugador} ha fallado tanto que le ha salido {figura}. Bob Ross estaría orgulloso.",
        "🎯 *Meme del día:* {jugador} ha fallado tanto que le ha salido arte. {figura} y sin querer.",
        "🎯 *Meme del día:* {figura} de {jugador}, cortesía de no dar ni una. Picasso empezó peor.",
        "🎯 *Meme del día:* {jugador} buscaba la palabra y ha encontrado {figura}. Se acepta el cambio.",
        "🎯 *Meme del día:* {jugador} iba a resolver y ha construido {figura}. Modo creativo activado.",
        "🎯 *Meme del día:* {figura} de {jugador}, cortesía de no dar ni una.",
        "🎯 *Meme del día:* el Tetris de {jugador} ha salido mal y ha quedado {figura}.",
        "🎯 *Meme del día:* {jugador} no ha resuelto, ha pintado. {figura}, y bien grande.",
        "🎯 *Meme del día:* {jugador} no ha resuelto: ha hecho arte moderno. {figura}, y con etiqueta.",
        "🎯 *Meme del día:* el fracaso de {jugador} ha quedado en {figura}. Al menos queda el cuadro.",
        "🎯 *Meme del día:* {figura} accidental de {jugador}. Se vende en subasta, sin reserva.",
        "🎯 *Meme del día:* «no hay errores, solo accidentes felices». {jugador} ha firmado {figura}.",
        "🎯 *Meme del día:* {jugador} ha fallado y le ha salido {figura}. Accidente feliz, dijo el de los pinceles.",
        "🎯 *Meme del día:* {figura} de {jugador}, hecho en modo creativo y sin querer.",
        "🎯 *Meme del día:* {jugador} iba a resolver y ha construido {figura}. Minecraft puro.",
        "🎯 *Meme del día:* {figura} accidental de {jugador}. Se cuelga en el Prado, ala de arte moderno.",
        "🎯 *Meme del día:* {jugador} no ha acertado, ha esculpido: {figura}.",
    ),
    # El catch-all: mucha distancia entre el mejor y el peor. **El que más variantes
    # necesita**: dispara en el 19% de las jornadas y era el 83% de los memes publicados.
    "dia-de-dos-mundos": (
        "🎯 *Meme del día:* {mejor} y {peor} en la misma palabra: hoy hay pastilla roja y pastilla azul.",
        "🎯 *Meme del día:* {mejor} el que más y {peor} el que menos. Un abismo de {hueco}.",
        "🎯 *Meme del día:* unos en el mundo normal ({mejor}) y otros en el del Revés ({peor}).",
        "🎯 *Meme del día:* unos en {mejor} y otros en {peor}. La misma palabra, dos realidades.",
        "🎯 *Meme del día:* {mejor} en primera clase y {peor} en tercera. El Titanic también iba así.",
        "🎯 *Meme del día:* de {mejor} a {peor} en el mismo día. ¿Jugamos todos a lo mismo?",
        "🎯 *Meme del día:* en El Hoyo los de arriba comen ({mejor}) y los de abajo miran ({peor}).",
        "🎯 *Meme del día:* {mejor} para unos, {peor} para otros. La desigualdad, en cuadrícula.",
        "🎯 *Meme del día:* unos jugaban al modo historia ({mejor}) y otros al Dark Souls ({peor}).",
        "🎯 *Meme del día:* hay quien la ha visto en {mejor} y quien la ha sufrido hasta el {peor}.",
        "🎯 *Meme del día:* {mejor} contra {peor}: hoy alguien iba en mundo 1-1 y alguien peleaba con Bowser.",
        "🎯 *Meme del día:* del {mejor} al {peor}. Hoy el grupo va en dos vagones distintos.",
        "🎯 *Meme del día:* unos han jugado en fácil y otros en pesadilla: {mejor} contra {peor}.",
        "🎯 *Meme del día:* {mejor} arriba, {peor} abajo. La misma palabra y dos experiencias.",
        "🎯 *Meme del día:* unos se han llevado el bote ({mejor}) y otros la silla azul ({peor}).",
        "🎯 *Meme del día:* {peor} menos {mejor}. Ahí caben todas nuestras diferencias.",
        "🎯 *Meme del día:* {mejor} y {peor}. En Interstellar el tiempo también pasaba distinto según dónde estabas.",
        "🎯 *Meme del día:* alguien en {mejor} y alguien en {peor}. Hoy no hay término medio.",
        "🎯 *Meme del día:* hoy había dos partidas: la del nivel 5 ({mejor}) y la del nivel 100 ({peor}).",
        "🎯 *Meme del día:* la palabra era la misma. Los resultados, de {mejor} a {peor}.",
        "🎯 *Meme del día:* unos en la tienda del Un, Dos, Tres ({mejor}) y otros con la calabaza ({peor}).",
        "🎯 *Meme del día:* {mejor} y {peor} en la misma jornada. Esto es un aula sin nivelar.",
        "🎯 *Meme del día:* de {mejor} a {peor}: el invierno ha llegado, pero solo a media tabla.",
        "🎯 *Meme del día:* {mejor} para los elegidos y {peor} para los mortales. Hoy no hay término medio.",
        "🎯 *Meme del día:* unos con el diccionario y otros con la ouija: {mejor} contra {peor}.",
        "🎯 *Meme del día:* mientras unos cerraban en {mejor}, otros seguían peleando hasta el {peor}.",
        "🎯 *Meme del día:* {mejor} y {peor} en la misma jornada. Aquí no hay quien viva, y La que se avecina.",
        "🎯 *Meme del día:* de {mejor} a {peor}: hoy el Wordle ha repartido suerte muy mal.",
        "🎯 *Meme del día:* hoy el matchmaking nos ha juntado mal: {mejor} contra {peor}.",
        "🎯 *Meme del día:* hoy hemos vivido dos jornadas distintas: la del {mejor} y la del {peor}.",
        "🎯 *Meme del día:* {mejor} en modo fácil y {peor} en modo pesadilla. Misma palabra, distinto juego.",
        "🎯 *Meme del día:* de {mejor} a {peor}. Un abismo de {hueco}, y en el medio no había nadie.",
        "🎯 *Meme del día:* unos han hecho speedrun ({mejor}) y otros el 100% con guía ({peor}).",
        "🎯 *Meme del día:* unos veían la palabra y otros veíamos manchas: {mejor} contra {peor}.",
        "🎯 *Meme del día:* {mejor} arriba, {peor} abajo: hoy el grupo se ha partido como España en Eurovisión.",
        "🎯 *Meme del día:* {mejor} y {peor}: dos partidas distintas con la misma palabra y el mismo diccionario.",
        "🎯 *Meme del día:* {mejor} y {peor}: unos jugaban al Mario y otros al Dark Souls.",
        "🎯 *Meme del día:* unos con el bote y otros con la silla azul: {mejor} contra {peor}.",
        "🎯 *Meme del día:* {mejor} y {peor} en la misma palabra. Aquí no hay quien viva, escalera A y escalera B.",
        "🎯 *Meme del día:* de {mejor} a {peor}: unos en la tienda y otros con la calabaza.",
        "🎯 *Meme del día:* unos han visto la palabra y otros la niebla de Silent Hill: {mejor} y {peor}.",
        "🎯 *Meme del día:* {mejor} contra {peor}: hoy había pastilla roja para unos y azul para otros.",
        "🎯 *Meme del día:* unos en primera clase ({mejor}) y otros en la sala de máquinas ({peor}).",
        "🎯 *Meme del día:* {mejor} y {peor}. Multiplícate por cero, dijo la palabra a media tabla.",
        "🎯 *Meme del día:* de {mejor} a {peor}: unos con condensador de fluzo y otros a pedales.",
        "🎯 *Meme del día:* {mejor} para unos y {peor} para otros. Qué follón.",
        "🎯 *Meme del día:* unos han hecho wololo y otros han perdido el aldeano: {mejor} contra {peor}.",
    ),
}


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

#: El **segundo y el tercer** empate de la misma pareja en la temporada. Llevan además `{veces}`.
#:
#: La escalada va por **recurrencia, no por duración**. Medido: los empates consecutivos casi no existen —los
#: cinco de agosto duran una sola jornada, y de las doce rachas del histórico once duran una y solo una llegó
#: a tres—. Lo que sí se repite es la misma pareja empatando en jornadas salteadas: Andrés R. y Claire cuatro
#: veces en agosto (#1678, #1681, #1685, #1687) y otras cuatro en el histórico.
RIVALIDAD_EMPATE_OTRA_VEZ: tuple[str, ...] = (
    "🔥 *Pelea por el primer puesto:* otra vez {cifra} y {cifra}. {a} y {b} llevan {veces} empates este mes.",
    "🔥 *Pelea por el primer puesto:* {a} y {b} vuelven a estar clavados a {cifra}. Van {veces}.",
    "🔥 *Pelea por el primer puesto:* y van {veces}. {a} y {b} a {cifra}, otra vez sin separarse.",
    "🔥 *Pelea por el primer puesto:* {a} y {b} empatan por {veces}ª vez a {cifra}. Esto empieza a cansar.",
    "🔥 *Pelea por el primer puesto:* {veces} empates ya entre {a} y {b}. A {cifra} otra vez.",
    "🔥 *Pelea por el primer puesto:* otra jornada, mismo {cifra} para {a} y {b}. Van {veces}.",
    "🔥 *Pelea por el primer puesto:* {a} y {b} no hay manera: {veces} veces a {cifra}.",
    "🔥 *Pelea por el primer puesto:* van {veces} empates de {a} y {b}. Alguien tendrá que ceder.",
)

#: El **cuarto empate o más** de la misma pareja: la tensión al máximo. Cuatro es el techo observado en las
#: dos temporadas (195 jornadas), así que este registro es el del caso extremo de verdad.
RIVALIDAD_EMPATE_TENSION: tuple[str, ...] = (
    "🔥 *Pelea por el primer puesto:* {veces}º empate de {a} y {b}. Esto ya no es casualidad, es un pulso.",
    "🔥 *Pelea por el primer puesto:* {a} y {b}, {veces} veces a {cifra}. Se está poniendo muy tenso esto.",
    "🔥 *Pelea por el primer puesto:* {veces} empates. {a} y {b} a {cifra}, y la cosa huele a chamusquina.",
    "🔥 *Pelea por el primer puesto:* {a} y {b} llevan {veces} empates a {cifra}. Que alguien traiga la manta.",
    "🔥 *Pelea por el primer puesto:* {veces}º empate entre {a} y {b}. Esto se decide en la última jornada.",
    "🔥 *Pelea por el primer puesto:* {a} contra {b}, {veces}ª vez en tablas a {cifra}. Aquí no cabe un alfiler.",
    "🔥 *Pelea por el primer puesto:* {veces} veces empatados {a} y {b}. Uno de los dos va a estallar.",
    "🔥 *Pelea por el primer puesto:* {a} y {b} a {cifra} por {veces}ª vez. La tensión se corta con un cuchillo.",
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


# ─────────────────────────────────────────────────────────────────────────────
# TENDENCIA DEL LIDERAZGO
#
# **No tiene línea propia.** Se enganchó al relevo después de simular la alternativa: una línea diaria de
# tendencia salía desde la tercera jornada del mes, se repetía casi idéntica varios días y llegó a publicar
# «Andrés R. lleva 7 jornadas mandando» tres días seguidos **mientras mandaba Claire** — porque «7 jornadas»
# era un total acumulado y «lleva mandando» se lee como racha. Pegada al relevo solo aparece cuando de verdad
# ha cambiado algo.
#
# Frecuencia natural, decisión del dueño: en un mes volátil como agosto sale 8 de 14 jornadas, y en uno
# tranquilo el 7%, igual que el relevo. La frecuencia **es** la señal: el mensaje habla de rivalidad cuando
# hay rivalidad.
# ─────────────────────────────────────────────────────────────────────────────

#: El contexto que se le añade al relevo. `{cambios}` y `{reparto}` (los dos que se la están jugando).
TENDENCIA_DEL_MES: tuple[str, ...] = (
    "Y van {cambios} cambios de cabeza este mes: {reparto}.",
    "{cambios} veces ha cambiado el líder en lo que va de mes. Reparto: {reparto}.",
    "Esto no se decide hasta el último día: {cambios} cambios ya, y {reparto}.",
    "Van {cambios} relevos este mes. Se lo están repartiendo: {reparto}.",
    "El mes lleva {cambios} vuelcos en la cabeza: {reparto}.",
    "Otro más: {cambios} cambios de líder este mes ({reparto}).",
    "Nadie se acomoda: {cambios} relevos y un reparto de {reparto}.",
    "{cambios} cambios de cabeza. Esto es una liga de verdad: {reparto}.",
)

#: El caso opuesto: alguien lleva jornadas **seguidas** sin soltar la cabeza. `{jugador}` y `{racha}`.
DOMINIO: tuple[str, ...] = (
    "👑 {jugador} lleva {racha} jornadas seguidas sin soltar la cabeza.",
    "👑 {racha} jornadas mandando {jugador}, y nadie se le acerca.",
    "👑 Nadie le quita la cabeza a {jugador}: {racha} jornadas ya.",
    "👑 {jugador} se ha instalado arriba: {racha} jornadas seguidas.",
    "👑 {racha} jornadas de reinado de {jugador}. Alguien tendrá que hacer algo.",
    "👑 {jugador} sigue arriba por {racha}ª jornada consecutiva.",
)
