# Glosario de wordle-stats

Vocabulario común del proyecto: qué significa cada palabra cuando aparece en una spec, un slice, un ADR, un
mensaje del bot o una conversación sobre las reglas. Existe para que «jornada», «día», «nivel» o «media»
quieran decir lo mismo en el código, en la web y en el canal.

**Cómo usarlo.** Los términos están agrupados por dominio —las siete capabilities de
[`openspec/README.md`](../openspec/README.md), más el SuperWordleBros, el debate de reglas, los indicadores de
juego y el método— y ordenados alfabéticamente dentro de cada grupo. Cada entrada da una definición corta y,
cuando hay ambigüedad real, los *sinónimos aceptados* y lo que conviene *evitar*. La línea *Código* apunta a
donde la definición se cumple de verdad (`ruta:línea`); si el glosario y el código discrepan, **manda el
código** y se corrige el glosario. Cuando un umbral sale de una constante, se nombra la constante y su valor.

**Dónde encaja.** En la jerarquía de verdad del proyecto, **specs + slices > ADRs / glosario > briefs >
sources** (`docs/context/INDEX.md:11`). El glosario no crea reglas: nombra las que ya están en las specs, los
slices y el código.

**Convenciones.** El repositorio es público y los datos son de compañeros identificables: los ejemplos usan
roles («un jugador», «la jornada N»), nunca nombres, ids de Slack ni palabras del día. Los identificadores se
escriben como en el código (`slack_user_id`, `media_temporada`).

---

## Resultados

**Cambio aditivo** — Mientras la v1 siga publicada, todo cambio de esquema añade columnas o tablas y nunca
renombra ni elimina las que lee la v1 (`player_name`, `wordle_id`, `score`, `date`).
· *Código*: `openspec/decisions/0005-hosting-y-convivencia-v1-v2.md:90` · *Dominio*: resultados

**Fallo** — Partida no resuelta, marcada `X/6` en el mensaje. Se guarda y se computa como 7 intentos
(`FALLO = 7`), que es también el tope de cualquier nota imputada: ninguna ausencia cuesta más que fallar.
· *Sinónimos aceptados*: X, partida fallada · *Evitar*: «0» o «sin nota»
· *Código*: `tools/patterns.py:63`, `tools/badges.py:31`, `tools/standings.py:92` · *Dominio*: resultados

**Fecha del puzzle** — La fecha (`date`) de un resultado, derivada del número de jornada con el ancla
`ANCHOR_ID = 1485` ↔ `ANCHOR_DATE = 2026-01-30`; nunca del reloj ni de cuándo se publicó.
· *Sinónimos aceptados*: fecha · *Evitar*: confundirla con `created_at` (cuándo escribió el cron la fila) o
con la hora de publicación en Slack
· *Código*: `tools/add_results.py:29`, `tools/add_results.py:60` · *Dominio*: resultados

**Intentos** — La nota de una partida (`score`): de 1 a 6, o 7 si es un fallo. Cuanto más baja, mejor.
· *Sinónimos aceptados*: nota, puntuación (solo en la tabla de resultados) · *Evitar*: «puntos», que se
reserva al álbum de figuras y al SuperWordleBros
· *Código*: `tools/patterns.py:63`, `tools/add_results.py:86` · *Dominio*: resultados

**Jornada** — Un puzzle de «La palabra del día», identificado por su número (`wordle_id`), que es el índice
del propio juego sin desplazamiento. El grupo juega ese juego, no el Wordle del NYT.
· *Sinónimos aceptados*: `wordle_id`, número de puzzle, «la jornada N» · *Evitar*: «día» (un día natural
puede no tener jornada válida) y «nivel» (el escenario del SuperWordleBros que se construye con una jornada)
· *Código*: `tools/palabra.py:5`, `tools/seasons.py:92` · *Dominio*: resultados

**Patrón** — La cuadrícula de colores de una partida, guardada en `pattern` como filas de cinco celdas
separadas por `/`: `G` letra en su sitio, `Y` presente en otra posición, `.` ausente (las dos variantes de
celda vacía de Slack se normalizan igual). Puede faltar en resultados antiguos.
· *Sinónimos aceptados*: cuadrícula, dibujo · *Evitar*: «figura», que es la categoría derivada del patrón
· *Código*: `tools/patterns.py:6`, `tools/patterns.py:18` · *Dominio*: resultados

**Resultado** — Una fila de `wordle_results`: un jugador en una jornada, con su nota, su fecha, su nombre
mostrado, el texto original (`raw_text`) y el patrón. Hay como mucho uno por par (`slack_user_id`, `wordle_id`).
· *Sinónimos aceptados*: partida, fila · *Evitar*: «puntuación» para la fila entera
· *Código*: `tools/add_results.py:81`, `openspec/decisions/0005-hosting-y-convivencia-v1-v2.md:101`
· *Dominio*: resultados

## Ingesta

**Bloque de resultado** — Un mensaje de resultado junto con las filas de cuadrícula que le siguen. Un mensaje
nuevo, tenga o no resultado, cierra el bloque anterior. Un bloque sin autor se descarta y se informa: la
ingesta no inventa identidad.
· *Código*: `tools/patterns.py:69`, `tools/patterns.py:88`, `tools/add_results.py:78` · *Dominio*: ingesta

**Mensaje de resultado** — Texto del canal que contiene «La palabra del día #N X/6»; es lo único que se
ingiere como resultado. El extractor lo entrega en líneas `USER_START|<id>|<nombre>|<hora>|<texto>`, con el
id primero porque es lo que identifica.
· *Código*: `tools/patterns.py:33`, `tools/patterns.py:32`, `tools/extract_slack.py:130` · *Dominio*: ingesta

**Reingesta idempotente** — Cada ejecución reprocesa la ventana entera y escribe con `upsert` sobre la clave
`CLAVE_DE_CONFLICTO = ("slack_user_id", "wordle_id")`: repetir actualiza, no duplica.
· *Sinónimos aceptados*: upsert · *Código*: `tools/add_results.py:34`,
`openspec/decisions/0005-hosting-y-convivencia-v1-v2.md:102` · *Dominio*: ingesta

**Ventana de ingesta** — Los mensajes que lee cada ejecución, medidos **en días** (`VENTANA_EN_DIAS = 14`) y
no en número de mensajes, para que la cobertura no dependa de lo hablador que esté el grupo.
· *Evitar*: «los últimos 50 mensajes» (criterio antiguo)
· *Código*: `tools/extract_slack.py:39` · *Dominio*: ingesta

## Identidad

**Apodo** — Sustituto de presentación que la web pinta en lugar del nombre de un jugador. Solo existe en la
web (el bot nombra a todos por su nombre) y nunca cambia la identidad: rutas, selector del juego y marcas
siguen usando el id de Slack.
· *Evitar*: usar el apodo para cruzar datos o como clave
· *Código*: `v2/js/domain/apodos.js:18`, `v2/js/domain/apodos.js:24` · *Dominio*: identidad

**Canonización de identidad** — Proceso manual y puntual que convirtió las filas históricas identificadas
por nombre en filas identificadas por id de Slack: fusiona renombres y declara, sin forzarlos, los casos
cruzados o con la clave ocupada. Tiene ensayo obligatorio (`--dry-run`).
· *Código*: `tools/canonical_identity.py:69` · *Dominio*: identidad

**Etiqueta acordada** — Nombre mostrado fijado a mano para los pocos jugadores cuyo nombre en Slack es un
handle; gana al nombre de Slack. Añadir una cambia lo que ve el grupo.
· *Código*: `tools/add_results.py:44`, `tools/add_results.py:51` · *Dominio*: identidad

**Forma gramatical** — La terminación (masculina, femenina o la neutra `@`) con la que el mensaje concuerda
adjetivos con cada persona. Es una tabla declarada por el dueño e indexada por nombre mostrado; quien no
figura sale con la neutra.
· *Sinónimos aceptados*: concordancia de género · *Evitar*: deducir el género a partir del nombre
· *Código*: `tools/personas.py:63`, `tools/personas.py:66` · *Dominio*: identidad (lo consume publicacion)

**Identificador de Slack** — `U` seguido de mayúsculas, dígitos o guiones bajos. Es la identidad estable de
un jugador: columna `slack_user_id`, rutas de la web (`/t/<AAAA-MM>/j/<id>`), marcas del juego y votos.
· *Sinónimos aceptados*: id de Slack, `slack_user_id` · *Evitar*: dar por id cualquier cadena que empiece por
`U` (un nombre también puede)
· *Código*: `tools/canonical_identity.py:31`, `v2/js/router.js:62` · *Dominio*: identidad

**Jugador** — Una persona del grupo, identificada por su id de Slack; en los cálculos es la clave `jugador`.
Un renombre en Slack no crea un jugador nuevo: solo cambia el nombre mostrado de las filas nuevas.
· *Sinónimos aceptados*: persona, miembro del grupo · *Evitar*: identificar a alguien por su nombre o su apodo
· *Código*: `tools/standings.py:116`, `v2/js/router.js:19`,
`openspec/slices/ingesta/ingesta-por-id-de-slack.md:58` · *Dominio*: identidad

**Nombre mostrado** — `player_name`: cómo se nombra a un jugador. Se resuelve como etiqueta acordada > nombre
de Slack > id; en las clasificaciones se toma el de la fila más reciente. La v1 lee esta columna, así que no
se renombra.
· *Sinónimos aceptados*: nombre · *Evitar*: «usuario»; usarlo como clave
· *Código*: `tools/add_results.py:51`, `tools/juego.py:65` · *Dominio*: identidad

## Estadísticas

**Categoría de figura** — Las cinco etiquetas del clasificador: `loro` 🦜, `flores` 🌷, `geometrico` 📐,
`culo` 🍑 y `abstracto` 🌀. Las cuatro primeras son figura reconocible; `abstracto` es su ausencia, se
registra y no puntúa. No existe la categoría «ambiguo».
· *Código*: `tools/figures.py:40`, `tools/figures.py:56` · *Dominio*: estadisticas

**Dificultad del día** — Media de intentos del grupo en una jornada válida de la temporada. Rige la
imputación y dos umbrales: día difícil (`UMBRAL_DIA_DIFICIL = 4.5`) y día imposible
(`UMBRAL_DIA_IMPOSIBLE = 5.5`).
· *Evitar*: calcularla sobre días sin la muestra mínima
· *Código*: `tools/standings.py:72`, `tools/badges.py:33`, `tools/badges.py:34`, `tools/badges.py:113`
· *Dominio*: estadisticas

**Espejo** — Rasgo de una cuadrícula cuyo **cuerpo** (la cuadrícula sin la banda verde final) es palíndromo
fila a fila y con las cinco columnas; una sola celda rota lo niega. Clasifica como geométrico con
`CUERPO_MINIMO_DEL_ESPEJO = 2` filas de cuerpo; el logro «Espejo perfecto» pide
`CUERPO_MINIMO_DEL_LOGRO = 3`.
· *Sinónimos aceptados*: simetría · *Código*: `tools/figures.py:99`, `tools/figures.py:197`,
`tools/badges.py:69` · *Dominio*: estadisticas

**Ficha de jugador** — Vista de un jugador dentro de una temporada (`/t/<AAAA-MM>/j/<id>`): su fila del
marcador, su álbum, sus medallas, su **palmarés** (puesto en cada temporada materializada) y sus indicadores
de juego.
· *Código*: `v2/js/data/ficha.js:84`, `v2/js/data/ficha.js:41`, `v2/js/ui/jugador.js:376`
· *Dominio*: estadisticas

**Figura** — Categoría que el clasificador asigna a un patrón. Se deriva en cada cálculo y **no se
almacena**, así que recalibrar un umbral reclasifica el histórico. Sin banda verde final o con el cuerpo vacío
(un 1/6) es abstracto.
· *Sinónimos aceptados*: dibujo (coloquial) · *Evitar*: «patrón», que es el dato crudo
· *Código*: `tools/figures.py:335` · *Dominio*: estadisticas

**Medalla** — Logro calculado a partir de los resultados, nunca guardado. Tiene clave, nombre, emoji,
**nivel de rareza** (`legendario`, `raro`, `comun`; se presentan en ese orden) y **alcance** (`temporada`:
se puede ganar cada mes; `permanente`: una vez para siempre).
· *Sinónimos aceptados*: logro, insignia · *Evitar*: «nivel» a secas para la rareza (choca con el nivel del
juego) · *Código*: `tools/badges.py:83`, `tools/badges.py:91`, `tools/badges.py:110` · *Dominio*: estadisticas

**Medallas de rendimiento y constancia** — De temporada: Superviviente (`MINIMO_SUPERVIVIENTE = 3` días
difíciles resueltos en `RESOLVER_RAPIDO = 4` o menos), Metrónom@ (todas las jornadas del mes, con al menos
`MINIMO_DIAS_PARA_METRONOMO = 10`), Verdugo (mejor del día `MINIMO_VERDUGO = 5` veces), Impecable
(`MINIMO_IMPECABLE = 10` partidas sin fallo), Fondista (`MINIMO_FONDISTA = 15` partidas). Permanentes:
Suertud@ (resolver en 1), El día imposible (4 o menos un día imposible), Espejo perfecto.
· *Código*: `tools/badges.py:35`, `tools/badges.py:37`, `tools/badges.py:214`, `tools/badges.py:272`
· *Dominio*: estadisticas

**Medallas de figura** — De temporada, según el recuento del álbum: Ornitólog@ (`MINIMO_ORNITOLOGO = 5`
loros), Arquitect@ (`MINIMO_ARQUITECTO = 4` geométricos), Florista (`MINIMO_FLORISTA = 11` flores), Abstract@
(`MINIMO_ABSTRACTO = 7` abstractos) y Coleccionista (una de cada categoría que **haya salido** en la temporada).
· *Código*: `tools/badges.py:60`, `tools/badges.py:77`, `tools/badges.py:148`, `tools/badges.py:197`
· *Dominio*: estadisticas

**Orden nuevo de figuras** — Corte de reglas del clasificador desde `PRIMERA_JORNADA_DEL_ORDEN_NUEVO = 1694`:
a partir de esa jornada se decide espejo, culo, geométrico, loro y flor, en ese orden. **No es retroactivo**:
las cuadrículas anteriores conservan la categoría que tenían.
· *Sinónimos aceptados*: corte de reglas de figuras · *Código*: `tools/figures.py:86`, `tools/figures.py:112`,
`tools/figures.py:364` · *Dominio*: estadisticas

## Ranking

**Álbum de figuras** — El segundo ranking de la temporada, independiente del marcador. Cada figura da
`PUNTOS` (geométrico 3, culo 3, loro 2, flores 1, abstracto 0) y la media se divide entre las jornadas de la
temporada (en la temporada 0, entre las partidas jugadas), así que faltar no la mejora. Tiene puesto quien
llega a `minimo_de_la_temporada`: tantas partidas como jornadas lleve el mes, con tope
`MINIMO_PARA_EL_ALBUM = 5` (fijo en la temporada 0). A igualdad desempata la media del marcador y luego
el número de figuras.
· *Sinónimos aceptados*: ranking de figuras, ranking de belleza · *Evitar*: «clasificación» a secas
· *Código*: `tools/album.py:32`, `tools/album.py:56`, `tools/album.py:95`, `tools/album.py:99`,
`tools/album.py:199` · *Dominio*: ranking

**Archivo de temporadas** — La vista `/temporadas`: las temporadas materializadas de la más reciente a la más
antigua, cada cerrada con su campeón o campeones, y el **medallero**, que cuenta los títulos por competición
de todas las temporadas.
· *Código*: `v2/js/data/archivo.js:51`, `v2/js/data/archivo.js:130` · *Dominio*: ranking

**Cadencia de sincronización** — Requisito medible sobre el cron horario: al menos `MINIMO_DIARIO = 12`
ejecuciones por día completo y ningún hueco mayor que `HUECO_MAXIMO_EN_HORAS = 2.0`.
· *Código*: `tools/cadencia.py:18`, `tools/cadencia.py:21` · *Dominio*: ranking

**Clasificación** — La tabla de puntuación de la temporada: media de temporada ascendente; a igualdad, más
días jugados y luego el nombre. En las temporadas numeradas clasifica cualquiera con una partida; en la
temporada 0 hace falta `MINIMO_PARA_CLASIFICAR = 5`. Quien no clasifica sale en la tabla, sin puesto.
· *Sinónimos aceptados*: marcador, tabla, clasificación general · *Evitar*: «ranking» sin apellido (hay tres
competiciones) · *Código*: `tools/standings.py:65`, `tools/standings.py:95`, `tools/standings.py:173`
· *Dominio*: ranking

**Día de temporada** — Jornada que forma parte de una temporada numerada: **laborable** y con al menos
`MUESTRA_MINIMA_DEL_DIA = 5` resultados. En la temporada 0 cuenta toda jornada con algún resultado. La web
repite la constante y un test exige que coincidan.
· *Sinónimos aceptados*: día válido, jornada que cuenta · *Evitar*: «día jugado» (eso es por jugador) y
«día» a secas · *Código*: `tools/seasons.py:30`, `tools/seasons.py:99`, `v2/js/domain/superbros.js:79`
· *Dominio*: ranking

**Día laborable** — De lunes a viernes según la fecha de la fila (`ULTIMO_DIA_LABORABLE = 5` en
`isoweekday`). Una fecha ilegible no es laborable; los festivos no se conocen y los absorbe la muestra mínima.
· *Código*: `tools/calendario.py:25`, `tools/calendario.py:42`, `v2/js/data/dia.js:70` · *Dominio*: ranking

**Empate** — La misma cifra publicada da el mismo puesto, y el siguiente salta tantos números como gente
lleve delante (1, 1, 3). El desempate interno solo fija el orden de la lista. Vale para el marcador, el
álbum (cuando ni su desempate separa) y el SuperWordleBros.
· *Código*: `tools/standings.py:185`, `tools/album.py:261`, `tools/juego.py:51`,
`openspec/slices/ranking/empates-comparten-puesto.md:41` · *Dominio*: ranking

**Estado de temporada** — `en curso` (la más reciente con datos) o `cerrada`. Se deriva de los datos, no del
reloj, y viaja dentro de la instantánea.
· *Código*: `tools/seasons.py:32`, `tools/seasons.py:131` · *Dominio*: ranking

**Imputación** — La nota que se pone a un jugador en una jornada válida que no jugó:
`min(max(dificultad, media_personal) + margen(n), 7)`, con `margen(n) = MARGEN + PASO_DEL_MARGEN × (n − 1)`,
`MARGEN = 0.5`, `PASO_DEL_MARGEN = 0.15` y `n` la enésima ausencia del mes en orden de jornada. Faltar nunca
mejora la media. La temporada 0 no imputa.
· *Sinónimos aceptados*: día imputado, ausencia imputada, margen creciente
· *Código*: `tools/standings.py:40`, `tools/standings.py:54`, `tools/standings.py:90`, `tools/seasons.py:81`
· *Dominio*: ranking

**Media de temporada** — `media_temporada`: media de los intentos de **todas** las jornadas de la temporada,
jugadas e imputadas. Es la cifra que ordena el marcador y la que se publica.
· *Evitar*: llamarla «media» a secas donde también aparezca la media jugada
· *Código*: `tools/standings.py:151` · *Dominio*: ranking

**Media jugada** — `media_jugada`: media solo de las partidas que el jugador jugó; es la `media_personal` que
usa la imputación. No ordena nada.
· *Evitar*: presentarla como la nota del mes · *Código*: `tools/standings.py:122`, `tools/standings.py:162`
· *Dominio*: ranking

**Podio** — Los tres primeros puestos (`DEL_PODIO = 3`), cortando **por puesto** y no por filas: un empate
en el tercero sube entero. El **campeón** es quien ocupa el primer puesto de una temporada cerrada; con
empate, todos.
· *Código*: `tools/podio.py:25`, `tools/podio.py:55`, `tools/podio.py:65`, `v2/js/data/archivo.js:34`
· *Dominio*: ranking

**Temporada** — Un mes natural desde `INICIO_TEMPORADAS = "2026-08"`, identificado como `AAAA-MM`; el
marcador se reinicia el día 1. Su número de orden se deriva del límite (el mes del límite es la temporada 1).
· *Sinónimos aceptados*: mes, «Temporada N» · *Código*: `tools/seasons.py:39`, `tools/seasons.py:51`,
`tools/seasons.py:61` · *Dominio*: ranking

**Temporada cero** — Todo lo jugado antes del límite, con identificador `"0"`. Se rige por las reglas del
legacy: no imputa, no filtra días y exige 5 partidas para clasificar. No se celebra con podio de cierre.
· *Sinónimos aceptados*: temporada 0, el histórico · *Código*: `tools/seasons.py:43`, `tools/seasons.py:81`,
`tools/podio.py:31` · *Dominio*: ranking

**Tres competiciones** — Desde `DESDE_TRES_COMPETICIONES = "2026-10"` cada temporada corona tres campeones:
marcador, SuperWordleBros y figuras. Antes, solo el marcador. Python y la web declaran la misma constante.
· *Código*: `tools/podio.py:22`, `v2/js/data/archivo.js:21` · *Dominio*: ranking

## Publicación

**Captura del ranking** — Imagen de la web que el bot sube cada tarde laborable con el título
«Ranking Wordle del Día 🏆 · #N»; buscar ese título en el canal hace la publicación idempotente. Qué web se
fotografía lo decide el interruptor `CAPTURA_OBJETIVO` (por defecto `v1`).
· *Código*: `tools/post_ranking.py:112`, `tools/post_ranking.py:546`, `tools/post_ranking.py:567`
· *Dominio*: publicacion

**Comentario de la jornada** — Un `Hecho` detectado en la jornada que el mensaje convierte en broma con
frases fijas. Como mucho `MAXIMO_COMENTARIOS = 3`, uno por tipo; sin azar: la variedad sale del número de
jornada.
· *Sinónimos aceptados*: hecho · *Código*: `tools/comentarios.py:44`, `tools/comentarios.py:73`
· *Dominio*: publicacion

**Jugador del día** — Quien mejor puntuó la jornada (el **mejor del día**, la nota más baja); con empate se
nombran todos. Es un premio distinto de la obra del día.
· *Evitar*: fundirlo con la obra del día · *Código*: `tools/resumen.py:58`, `tools/badges.py:125`
· *Dominio*: publicacion

**Momento del mes** — Bloque del resumen que dice si el mes arranca (las primeras
`JORNADAS_DE_ARRANQUE = 3`), si está en la recta final (quedan como mucho `LABORABLES_DE_RECTA_FINAL = 4`
laborables) o si es la última jornada. Vacío a mitad de mes y en la temporada 0.
· *Código*: `tools/resumen.py:1099`, `tools/resumen.py:1103`, `tools/resumen.py:1194` · *Dominio*: publicacion

**Obra del día** — La figura más rara dibujada en la jornada, con su autor. Desempata por rareza en la
temporada, simetría, más intentos y nombre.
· *Código*: `tools/resumen.py:86` · *Dominio*: publicacion

**Palabra del día** — (1) El juego que juega el grupo. (2) El bloque del mensaje que abre con la solución de
la jornada que se resume y su primera acepción. Solo se publica una palabra ya jugada y nada se persiste.
· *Evitar*: llamar «Wordle» al juego en textos del grupo cuando importe la fuente de las soluciones
· *Código*: `tools/palabra.py:5`, `tools/palabra.py:147`, `openspec/slices/publicacion/palabra-del-dia.md:61`
· *Dominio*: publicacion

**Podio de cierre de mes** — Mensaje que celebra la temporada recién cerrada: podio del marcador,
felicitación al campeón con sus medallas y, desde octubre de 2026, los podios del juego y de figuras. Sale
la noche del último laborable del mes **en lugar del resumen**, y el cron de los días 1 a 3 lo publica si
faltara; el título «Podio del mes 🏆 · AAAA-MM» impide repetirlo. Los podios se dibujan en ASCII dentro de un
bloque de código, sin emojis, con tres nombres por escalón.
· *Sinónimos aceptados*: victoria, podio del mes · *Evitar*: «victorias» (son los niveles ganados en el juego)
· *Código*: `tools/podio.py:28`, `tools/podio.py:129`, `tools/post_ranking.py:688`, `tools/podios.py:81`
· *Dominio*: publicacion

**Resumen diario** — El mensaje compuesto de la tarde: palabra, jugador y obra del día, podios, momento del
mes, voz y comentarios. Es puro y no recalcula: usa los mismos módulos que la instantánea. Está tras el
interruptor `RESUMEN_COMPUESTO`, apagado por defecto.
· *Sinónimos aceptados*: resumen compuesto · *Código*: `tools/resumen.py:1`, `tools/post_ranking.py:115`
· *Dominio*: publicacion

**Señales** — Números y horas de una jornada sacados del canal al publicar (hora de publicación, reacciones,
respuestas, aperturas). No llevan texto y no se persisten.
· *Código*: `tools/senales.py:69`, `tools/senales.py:88` · *Dominio*: publicacion

**Tono del hilo** — Clasificación cerrada (casillas, sin texto libre) que un modelo externo devuelve sobre el
hilo del día. El repositorio escribe la frase; el modelo nunca.
· *Código*: `tools/tono.py:101`, `tools/post_ranking.py:263` · *Dominio*: publicacion

## Dashboard

**Escala fija** — Los gráficos de intentos usan siempre la escala 1–7 (`ESCALA_DE_INTENTOS`), para que dos
gráficos del mismo tipo se puedan comparar a simple vista.
· *Código*: `v2/js/data/escala.js:12` · *Dominio*: dashboard

**Ruta** — Dirección de una vista de la v2: `/`, `/t/<AAAA-MM>`, `/t/<AAAA-MM>/j/<id>`, `/temporadas`, `/hoy`,
`/datos`, `/info`, `/debate`. Una temporada es `AAAA-MM` con mes real o `0`. La v2 se sirve bajo `/2/`.
· *Código*: `v2/js/router.js:4`, `v2/js/router.js:32`, `v2/js/router.js:59` · *Dominio*: dashboard

**Tabla de datos** — La vista `/datos`: los resultados crudos leídos de `wordle_results`, sin pasar por la
instantánea.
· *Código*: `v2/js/data/tabla.js:25`, `openspec/decisions/0008-donde-vive-el-calculo.md:86`
· *Dominio*: dashboard

**Titular** — Frase de cabecera de la temporada que describe la pelea por el primer puesto; por debajo de
`VENTAJA_MINIMA = 0.15` de diferencia no se habla de «liderar». Mira el puesto, no el orden de la lista.
· *Código*: `v2/js/ui/temporada.js:144`, `v2/js/ui/temporada.js:155` · *Dominio*: dashboard

**v1 / v2** — La v1 es la web original, que lee `wordle_results` directamente; la v2 es la web nueva, que pinta
las instantáneas. Conviven sobre la misma base de datos y por eso el esquema solo crece.
· *Evitar*: «la web» cuando importe cuál · *Código*: `openspec/decisions/0005-hosting-y-convivencia-v1-v2.md:90`,
`v2/js/router.js:23` · *Dominio*: dashboard

**Vista Hoy** — `/hoy`: el día en curso leído de `wordle_results`, con quién ha jugado y las figuras de la
jornada.
· *Sinónimos aceptados*: día en curso · *Código*: `v2/js/data/dia.js:81`, `v2/js/data/dia.js:48`
· *Dominio*: dashboard

## El juego (SuperWordleBros)

**Clasificación del juego** — El tercer ranking de la temporada: cada nivel que puntúa reparte puntos por
puesto (`ESCALA = (10, 8, 6, 5, 4, 3, 2)` y `PUNTOS_DESDE_EL_OCTAVO = 1`) y el mes los suma; a igualdad se
comparte puesto, y las **victorias** (primeros puestos en niveles) solo ordenan la lista. Solo puntúan niveles
de días de temporada, y el del último laborable del mes puntúa en el mes siguiente.
· *Código*: `tools/juego.py:25`, `tools/juego.py:33`, `tools/juego.py:78`, `tools/juego.py:90`,
`tools/juego.py:108` · *Dominio*: juego (capability ranking)

**Coleccionable** — Estrella colocada en el nivel, una por tramo, sobre la plataforma más alta. Las
**estrellas** de una marca son los coleccionables recogidos y no pueden superar los del nivel.
· *Sinónimos aceptados*: estrella · *Código*: `v2/js/domain/superbros.js:173`,
`supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql:58` · *Dominio*: juego

**Marca** — Fila de `game_times`: el mejor tiempo (en segundos con centésimas) y las estrellas de un jugador
en un nivel. Solo se escribe a través de `registrar_tiempo`, que la sobrescribe solo si mejora (más estrellas,
o las mismas en menos tiempo) y rechaza tiempos imposibles: por debajo de
`tramos × 8 × 32 / (300 × 1,5)` segundos o desde 3600.
· *Sinónimos aceptados*: tiempo, récord · *Código*:
`supabase/migrations/20260925120000_create_game_times.sql:10`,
`supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql:62`,
`supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql:71` · *Dominio*: juego

**Nivel** — Escenario de plataformas construido con las cuadrículas de una jornada: un **tramo** de
`COLUMNAS_POR_JUGADOR = 8` columnas por jugador con patrón, los bloques verdes y amarillos de abajo arriba,
una etiqueta por tramo y los coleccionables.
· *Evitar*: «jornada» (el nivel de la jornada N se juega después de ella) y «nivel» para la rareza de una
medalla · *Código*: `v2/js/domain/superbros.js:19`, `v2/js/domain/superbros.js:173` · *Dominio*: juego

**Nivel cerrado** — Un nivel congelado deja de admitir marcas en cuanto se congela el siguiente: solo el
último congelado está abierto. El del viernes sigue abierto el fin de semana.
· *Código*: `supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql:54` · *Dominio*: juego

**Nivel congelado** — El nivel guardado en `game_levels` por el cron. Desde `HORA_DE_CONGELAR = "02:00"`
(Madrid) se congela la última jornada asentada —la de ayer— si cuenta para la temporada; la de hoy, nunca.
Un trigger impide cambiarlo o borrarlo.
· *Código*: `v2/js/domain/superbros.js:67`, `v2/js/domain/superbros.js:112`, `tools/juego.py:30`,
`supabase/migrations/20260925140000_create_game_levels.sql:41` · *Dominio*: juego

**Ranking del nivel** — El orden de las marcas de un nivel: más estrellas primero y, con las mismas, menos
tiempo. Mismas estrellas y mismo tiempo en centésimas comparten puesto.
· *Código*: `v2/js/domain/superbros.js:313`, `tools/juego.py:45`, `tools/juego.py:51` · *Dominio*: juego

**SuperWordleBros** — El juego de plataformas de la web que convierte las cuadrículas de una jornada en un
nivel. Su puntuación se comparte pegando en el canal «Super Wordle Bros. #N ⏱ m:ss ⭐ e/t». Es la tercera
competición desde octubre de 2026.
· *Sinónimos aceptados*: el juego · *Evitar*: «el juego» cuando pueda confundirse con La palabra del día
· *Código*: `v2/js/domain/superbros.js:2`, `v2/js/domain/superbros.js:245`, `tools/juego.py:1`
· *Dominio*: juego

## Debate de reglas

**Opción** — Respuesta posible de una votación: `{id, texto}` dentro de `rule_polls.opciones`, que exige al
menos dos.
· *Código*: `supabase/migrations/20261014120000_create_rule_debate.sql:21` · *Dominio*: debate

**Propuesta** — Regla que plantea un jugador (`rule_proposals`): título de 3 a 120 caracteres, explicación
de 10 a 2000 y estado `pendiente` (por defecto), `aprobada` o `rechazada`. Pendientes y aprobadas son públicas
y votables; la rechazada deja de verse y de admitir votos. Como mucho 3 pendientes por autor.
· *Evitar*: confundirla con una **votación** (pregunta cerrada que abre el dueño) o con una **regla** (lo que
el cálculo aplica) · *Código*: `supabase/migrations/20261014120000_create_rule_debate.sql:35`,
`supabase/migrations/20261014120000_create_rule_debate.sql:105`,
`supabase/migrations/20261015090000_public_votable_proposals.sql:11` · *Dominio*: debate

**Quién eres** — Selector de jugador sin cuentas ni contraseñas, compartido con el SuperWordleBros y
recordado en el navegador (`superbros:jugador`). Por eso los votos se enseñan con nombre: si alguien vota por
otro, el otro lo ve y lo cambia.
· *Código*: `v2/js/ui/juego.js:193`, `v2/js/ui/debate.js:1` · *Dominio*: debate

**Regla** — Entrada del catálogo que la web explica: id, eje (`EJES`), título, qué hace, por qué, estado
(`aplicada`, `acordada-sin-aplicar`, `sin-decidir`), si fue votada y sus parámetros, leídos de la constante que
el cálculo usa de verdad. Viaja en cada instantánea.
· *Evitar*: llamar «regla» a una propuesta todavía no aplicada · *Código*: `tools/rules.py:37`,
`tools/rules.py:39`, `tools/rules.py:59`, `tools/seasons.py:217` · *Dominio*: debate (capability dashboard)

**Votación** — Pregunta que abre el dueño (`rule_polls`) con dos o más opciones. Está abierta por defecto y se
cierra con `abierta = false`; cerrada, rechaza votos y se ve con su resultado.
· *Sinónimos aceptados*: encuesta · *Código*: `supabase/migrations/20261014120000_create_rule_debate.sql:16`,
`supabase/migrations/20261014120000_create_rule_debate.sql:75` · *Dominio*: debate

**Voto** — Elección de una opción por un jugador que ha jugado alguna vez. Uno por persona y votación (clave
`(votacion, votante)`), cambiable mientras esté abierta: cuenta el último.
· *Código*: `supabase/migrations/20261014120000_create_rule_debate.sql:26`,
`supabase/migrations/20261014120000_create_rule_debate.sql:92`, `v2/js/domain/debate.js:10` · *Dominio*: debate

**Voto de propuesta** — `a_favor` o `en_contra`, uno por persona y propuesta (clave `(propuesta, votante)`),
cambiable. Los **apoyos** de una propuesta son quiénes están a favor y quiénes en contra.
· *Código*: `supabase/migrations/20261015090000_public_votable_proposals.sql:14`, `v2/js/domain/debate.js:22`
· *Dominio*: debate

## Indicadores de juego

**Acierto más milagroso** — La partida resuelta con más candidatas en el intento que acertó; a igualdad, la
jornada más antigua.
· *Sinónimos aceptados*: milagro · *Código*: `tools/indicadores.py:128` · *Dominio*: indicadores (capability
estadisticas)

**Apertura** — Mediana de candidatas que quedan tras el primer y tras el segundo intento; una partida resuelta
antes no cuenta para ese intento.
· *Código*: `tools/indicadores.py:119` · *Dominio*: indicadores

**Candidatas** — Soluciones aún posibles antes de cada intento. Como no se conocen las palabras probadas,
solo sus colores, se estiman sorteando palabras que den esos colores contra la respuesta (`SORTEOS = 15`,
mediana) sobre el **universo** de soluciones ya jugadas. Una cuadrícula incompatible descarta la partida.
· *Código*: `tools/indicadores.py:38`, `tools/indicadores.py:74`, `tools/indicadores.py:161`
· *Dominio*: indicadores

**Eficiencia** — La media de un jugador comparada con la del grupo y con la de un solucionador óptimo
(`MEDIA_DEL_SOLUCIONADOR = 3.41`).
· *Código*: `tools/indicadores.py:35`, `openspec/slices/estadisticas/indicadores-de-juego.md:51`
· *Dominio*: indicadores

**Lista de soluciones** — El fichero de soluciones del propio juego, descargado y descifrado en el borde.
Solo se lee hasta la última jornada de la tabla (`palabra_de`); si no se puede leer, la instantánea se
materializa sin indicadores. Lo que sale nunca lleva palabras.
· *Código*: `tools/palabra.py:33`, `tools/palabra.py:63`, `tools/materialize_seasons.py:87`,
`tools/seasons.py:239` · *Dominio*: indicadores

**Mínimo de partidas** — `MINIMO_DE_PARTIDAS = 5` partidas con cuadrícula legible en la temporada; con menos,
la ficha dice cuántas faltan en lugar de dar cifras.
· *Código*: `tools/indicadores.py:30`, `tools/indicadores.py:196` · *Dominio*: indicadores

**Suerte** — Por cada intento, 1 si acierta (0 si no) menos 1/candidatas; se suma por partida. Acertar con una
sola candidata suma cero: es saber la palabra. No es un medidor de trampas.
· *Código*: `tools/indicadores.py:111`, `tools/indicadores.py:10` · *Dominio*: indicadores

## El método

El método trabaja con **specs vivas**: las capability specs de `openspec/specs/<capability>/spec.md` se editan
directamente en la rama de cada cambio, junto al slice, el código y los tests. De cada cambio queda su
`runs.yaml`; los change packs con deltas anteriores están en `openspec/changes/archive/`. Lo decide el
[ADR 0009](../openspec/decisions/0009-specs-vivas.md) (`openspec/slice-system.md:121`, §5).

**Borde** — El CLI, el cron y la carga de la página: el único sitio donde se lee el reloj, la red o git. Todo
lo demás recibe la fecha y los datos por parámetro, y eso hace posibles los golden tests.
· *Sinónimos aceptados*: frontera determinista · *Código*: `openspec/slice-system.md:309`,
`tools/materialize_seasons.py:241` · *Dominio*: método

**Capability** — Uno de los siete dominios bajo los que cuelgan specs y slices: `resultados`, `ingesta`,
`identidad`, `estadisticas`, `ranking`, `publicacion`, `dashboard`. Las temporadas no son capability propia:
son un recorte de `ranking`.
· *Sinónimos aceptados*: dominio · *Código*: `openspec/README.md:20`, `openspec/README.md:35` · *Dominio*: método

**Capability spec** — `openspec/specs/<capability>/spec.md`: el contrato técnico de un dominio, hecho de
Requirements. Es **spec viva**: se edita en la misma rama que el código y el diff del PR es el cambio de spec.
· *Sinónimos aceptados*: spec viva, spec del dominio · *Evitar*: «spec consolidada» (término del modelo
anterior) · *Código*: `openspec/slice-system.md:18`, `openspec/slice-system.md:121` · *Dominio*: método

**Change pack** — `openspec/changes/<change-id>/`: el registro mínimo de un cambio, con `runs.yaml` obligatorio
y `proposal.md` / `tasks.md` opcionales. Ya no lleva deltas de spec; los packs anteriores quedan en
`openspec/changes/archive/` como historia.
· *Evitar*: «delta» para hablar de un cambio nuevo · *Código*: `openspec/slice-system.md:132`
· *Dominio*: método

**Escenario** — `### <slug>` con **WHEN/THEN** atómicos dentro de un slice. Su slug es estable y único en el
slice, y es la clave de trazabilidad con los tests (`@scenarios <slug>`).
· *Código*: `openspec/slice-system.md:54`, `openspec/slices/_template.md:34` · *Dominio*: método

**Gate** — Comprobación que bloquea avanzar de fase: 1a `slice validate`, 1b gates mecánicos
(specs-coverage, checks-probe), 2 `slice coverage` con tests en rojo, 4a `verify slice`, 4b cobertura de
Requirements, 4c **prueba de mutación**, 4d **auditoría adversarial**, 4e revisión de seguridad. Máximo tres
intentos; al tercero se escala.
· *Código*: `openspec/slice-system.md:151`, `tools/wslice/cli.py:81` · *Dominio*: método

**Instantánea** — La fila de `season_snapshots` de una temporada: un `payload` JSONB con todo lo calculado
(días, clasificación, dificultad, logros, álbum, juego, reglas, indicadores y el commit `calculado_con`). La
web la lee y la pinta; no recalcula.
· *Sinónimos aceptados*: snapshot, carga útil · *Código*: `tools/seasons.py:156`, `tools/seasons.py:206`,
`openspec/decisions/0008-donde-vive-el-calculo.md:75` · *Dominio*: método (capability ranking)

**Lección** — Regla permanente que nace de un fallo con causa raíz, registrada en `docs/lecciones.md` y
codificada en el punto más fuerte posible (mecánico > protocolo > skill > CLAUDE.md). Una lección `pendiente`
es deuda.
· *Código*: `openspec/slice-system.md:334`, `docs/lecciones.md:9` · *Dominio*: método

**Materialización** — Escribir la instantánea con `upsert` por `temporada`. El cron horario rematerializa la
temporada en curso y `RECIEN_CERRADAS = 1` cerrada; el resto, solo a mano (`--todas`). Lo que vive en la
instantánea no cambia con el push, sino en la siguiente materialización.
· *Código*: `tools/materialize_seasons.py:38`, `tools/materialize_seasons.py:228`, `CLAUDE.md:25`
· *Dominio*: método

**Requirement** — Invariante verificable de una capability spec; debe tener `checks:` (probes mecánicos) o
`verified-by:` (tests), y lleva un comentario `<!-- origen: <change-id> -->`.
· *Código*: `openspec/slice-system.md:87`, `openspec/slice-system.md:145` · *Dominio*: método

**Run record** — Entrada de `runs.yaml` por cada fase ejecutada sobre un cambio: `run`, `fase`, `actor`,
`gates` y `rondas_correccion`. `wslice metrics` agrega el histórico.
· *Código*: `openspec/slice-system.md:317` · *Dominio*: método

**Slice** — Comportamiento observable de punta a punta (actor → trigger → efectos), en
`openspec/slices/<capability>/<slug>.md`, con frontmatter (`status`, `kind`, `actor`, `trigger`, `specs`,
`tests_root`). Cruza todas las capabilities que declara. Su `status` es monotónico: `proposed`, `shipped`,
`deprecated`, `blocked`.
· *Código*: `openspec/slice-system.md:21`, `openspec/slice-system.md:34`, `openspec/slices/_template.md:1`
· *Dominio*: método

**Surface** — Dónde vive el entry point de un slice: `web` (el dashboard estático) o `pipeline` (los scripts
Python, por GitHub Actions o a mano).
· *Código*: `openspec/README.md:40` · *Dominio*: método

**Trigger** — Qué dispara un slice: `ui` (solo en `web`), `cron` y `command` (en `pipeline`). `http` y `event`
no tienen surface válida todavía. Nunca un trigger `ui` sobre un módulo interno.
· *Código*: `openspec/slice-system.md:61` · *Dominio*: método
