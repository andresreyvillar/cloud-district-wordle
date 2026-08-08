# Diario de desarrollo — wordle-stats

> **Propósito:** registro didáctico y cronológico de cómo se construye este proyecto: qué se hizo,
> por qué, qué alternativas se descartaron y qué se aprendió. Si alguien (humano o agente) llega
> nuevo, este documento cuenta la historia que el código no cuenta.
>
> **Convención de entradas:** fecha + qué / por qué / decisión (con descartes) / aprendizaje.
> Se añade entrada en cada hito: decisión de arquitectura, slice completado, cambio de método.
> Estilo: presente atemporal, honesto con los errores.

---

## 2025-11 a 2026-05 — La v1: de un JSON a un pipeline automático

**Qué.** El proyecto nace como una web estática con los resultados escritos a mano en
`data/data.json` y evoluciona hasta el pipeline actual: un bot lee el canal de Slack cada hora,
parsea los mensajes de resultado, los sube a Supabase, y un workflow diario publica una captura del
ranking en el canal.

**Decisiones que quedaron en el código, sin documentar en su momento:**
- **La fecha se deriva del número de puzzle, no del timestamp del mensaje** (ancla: el #1485 es el
  2026-01-30). Es lo que hace que el dato sea correcto aunque alguien publique su resultado con dos
  días de retraso. Verificado: las 1530 filas son coherentes con el ancla.
- **Supabase con RLS de solo lectura** para la clave pública: la web lee directamente desde el
  navegador sin backend propio. Verificado: con la clave publicable, insert da 401 y delete no borra.
- **El almacenamiento pasó de JSON a Supabase** y `data/data.json` quedó congelado (251 registros,
  hasta el 2026-01-30) sin que el README lo reflejara.

**Aprendizaje.** El sistema funciona y lleva meses en pie, pero todo el conocimiento está implícito:
los umbrales del ranking, el mapeo de nombres, el ancla de fechas. Nada de eso es verificable ni
tiene tests, y los intentos de arreglar la identidad de jugadores dejaron el código con una migración
a medias (ver `docs/lecciones.md`).

## 2026-08-04 — Adopción del desarrollo por specs y slices

**Qué.** Antes de abrir la v2.0 se instala el método spec-driven por slices de `pga-cms`: la
constitución (`openspec/slice-system.md`), las tres capas (slice → capability spec → tests), los
change packs con deltas, los ADRs, el pipeline de contexto, el registro de lecciones y un harness
que hace los gates mecánicos.

**Por qué ahora.** La v2.0 va a tocar exactamente lo que hoy está sin especificar: identidad de
jugadores, temporadas y ranking. Hacerlo sin especificación previa repetiría el patrón de la
migración a medias. Y hay una fecha real: el grupo acordó reiniciar el marcador el 1 de septiembre.

**Decisiones (con descartes):**
- **Harness en Python** (`tools/wslice`), no el port TypeScript de `slspec`. El repo no tiene Node ni
  build y Python ya es el stack del pipeline. El escáner de `@scenarios` se hizo **multi-lenguaje**
  (Python, JS, TS) a propósito: así el harness no ata la decisión de stack de la v2.0.
  *Descartado:* copiar `slspec` tal cual — habría metido pnpm y tsc en un repo de HTML estático.
  *Descartado:* renunciar al harness y dejar los gates como checklist — es justo lo que hace que el
  método se relaje cuando aprieta el tiempo.
- **7 capabilities** inferidas del sistema en producción, separando `resultados` (el almacén) de
  `ingesta` (la captura) y sacando `identidad` como dominio propio, porque ahí están los bugs.
  *Descartado:* 4 dominios más gruesos — habrían escondido identidad dentro de ingesta.
- **Protocolo completo**, incluidos los gates de mutación (4c) y adversarial (4d). Este repo no tiene
  usuarios de pago ni datos críticos: es el sitio ideal para rodar el método completo y aprender
  dónde duele.
- **Ramas `feat/… → main`** sin `develop`: un solo desarrollador. Con una consecuencia que hay que
  tener presente — **mergear a `main` despliega** (ADR 0003).

**Aprendizaje.** El primer artefacto que produce el método es el registro de sus propias deudas: el
gate de `test-commands` solo comprueba una expresión regular, y eso queda escrito como lección
pendiente en lugar de disimulado. Un harness honesto sobre sus límites es más útil que uno que
aparenta cubrirlo todo.

**Y el método se estrenó cazando cosas en su propia instalación.** La prueba de mutación (Gate 4c)
sobre el harness dio tres hallazgos que ninguna revisión de código habría dado:

1. Un mutante **sobrevivió** — el filtro `.md` del gate `federated-untouched` no estaba cubierto por
   ningún test. Al escribir los tests que faltaban, uno falló contra el código sano y destapó un
   agujero real heredado del port: `git status --porcelain` colapsa un directorio entero sin trackear
   en una línea, así que una capability nueva completa esquivaba el gate. Arreglado con
   `--untracked-files=all`.
2. El **bytecode cacheado** falseó un veredicto: tras restaurar un mutante, los tests seguían rojos
   con el código ya correcto porque el `.pyc` del mutante tenía el mismo tamaño y el mismo mtime al
   segundo. Podría haber fallado al revés — un mutante dando el gate por bueno. De ahí que ahora todo
   comando de test lleve `-B`.
3. Un `git restore` se llevó un arreglo hecho a mitad del gate, porque el index no se había
   actualizado. Ahora el procedimiento lo dice.

Las tres son reglas codificadas, no anécdotas (`docs/lecciones.md`). El orden importa: el mutante que
sobrevive no se tapa reforzando el test a ojo — se investiga, y a veces lo que aparece es un bug.

## 2026-08-04 — Dónde vive la web: la premisa era falsa

**Qué.** Al revisar el alojamiento antes de abrir la v2.0, se descubre que la web **no está en
Cloudflare Pages**, como se creía: es un **Worker con Static Assets**. Lo demuestran tres cosas
independientes — la URL es `*.workers.dev` (Pages sería `*.pages.dev`, y ese host no resuelve),
`wrangler.jsonc` declara `assets.directory`, y no hay Worker script: solo assets desde el edge.

**Por qué importa.** La pregunta era "¿es buena práctica quedarse aquí?", y la respuesta cambia por
completo según la plataforma. Resulta que ya está en la recomendada: Cloudflare dirige todo el trabajo
nuevo a Workers y Pages solo se mantiene. No hay nada que migrar.

**Decisiones** ([ADR 0005](../openspec/decisions/0005-hosting-y-convivencia-v1-v2.md)):
- La v2.0 va a un Worker nuevo, `cloud-district-wordle-2`. La v1 **no se mueve**.
  *Descartado:* que la v2.0 heredase la URL actual y la v1 se apartase con sufijo. Suena mejor, pero
  obliga a republicar producción y coordinar dos despliegues para ahorrar el cambio de una línea.
- Una sola base de datos, con invariante dura: **mientras la v1 esté publicada, el esquema solo crece**.
  Nunca se renombra ni se borra lo que la v1 lee.

**Aprendizaje.** Dos, y ninguno es sobre Cloudflare. El primero: la premisa que nadie cuestiona es la
que conviene verificar — costó tres comandos y cambiaba la respuesta entera. El segundo: la parte
difícil de "mantener la v1 viva" no era el hosting (dos URLs son gratis) sino los datos. Las dos
versiones leen la misma tabla, así que la v1 no es un archivo histórico: es la vista antigua de datos
que siguen cambiando. Decirlo por escrito evita la sorpresa de ver la v1 con números "raros" el día que
se fusionen los jugadores duplicados.

## 2026-08-04 — "Los fines de semana no cuentan": una regla trivial que arreglaba una medalla rota

**Qué.** El grupo cierra una regla más: una temporada son sus días laborables. Antes de tocar nada se
mide el impacto, y resulta ser dos cosas a la vez. Para casi todo es un **no-op**: los fines de semana
son 13 resultados de 1533 (0,85%) en 10 jornadas, y ninguna llega a los cinco jugadores del umbral de
muestra, así que la dificultad del día y las medallas que dependen de ella no cambian de resultado. Pero
para `Pleno` **arregla un fallo que la hacía inganable**: los días de la temporada se derivan de los
datos, así que una sola persona jugando un domingo convertía ese domingo en día de la temporada y se lo
bloqueaba a todo el grupo. Medido: 0 de 123 parejas jugador-mes lo lograban. Con la regla, 6.

**Por qué importa.** La regla que parece cosmética era la que destapaba el bug. Y de paso salieron **dos
cifras falsas** del brief de medallas, las dos escritas el mismo día: `Pleno` decía 12% (era 0) y
`El día imposible` decía "2 personas, una vez" (son 4, en 2 días). Las dos venían de consultas *ad hoc*
cuya semántica no coincidía con la del código que implementa la medalla.

**Decisiones.**
- `tools/calendario.py`: **una sola** definición de día laborable para los tres dominios que la van a
  consumir (medallas, participación, figuras). *Descartado:* un helper privado en `badges.py`, que
  garantizaba una segunda definición divergente — el proyecto ya tuvo ese problema con "día difícil".
- El filtro va en **las dos entradas públicas** del cálculo, no en cada recuento: así quedan limpios de
  una vez la dificultad, el mejor del día, el número de partidas y el conjunto de días del que depende
  `Pleno`. Dos de los cuatro mutantes existen solo para comprobar que están las dos.
- Los resultados de fin de semana **se siguen capturando y guardando**. La exclusión vive en el cálculo:
  nada destructivo y reversible si el grupo cambia de opinión. *Descartado:* dejar de ingerirlos, que
  además haría irrecuperable el dato pasados los 240 días de retención de Slack.
- **Fuera de alcance a propósito:** que "ser el mejor del día" exija muestra mínima. 25 de los 447
  créditos históricos salen de días con menos de cinco jugadores y esta regla solo tapa 10. Es una regla
  distinta con el mismo síntoma, y la decide el grupo.

- **El cron pasa a lunes-viernes** (`0 17 * * 1-5`). Salió de comprobar, ya al cerrar, qué publicaría el
  resumen un sábado: `seccion_de_medallas` devuelve el **mismo texto tres veces** sobre los mismos datos,
  porque la jornada se deriva de `max(wordle_id)` y en fin de semana no llegan filas nuevas. Un cron
  dominical republicaba la jornada del viernes con sus medallas — bug preexistente, no de la regla. La
  ingesta horaria **no** se toca: sigue los siete días, que es lo que sostiene la decisión de capturar el
  fin de semana. Se quedan los dos mecanismos, cron y filtro, porque el filtro sigue haciendo falta para
  `workflow_dispatch` y para el sábado en que alguien publique.

**Aprendizaje.** Tres. El primero: **medir antes de escribir cambió el sentido del cambio** — parecía un
ajuste de coherencia y era un arreglo. Dos veces en el mismo pack: primero `Pleno`, y al cerrar, el cron. El segundo: los fixtures mentían sin que nadie lo notara. Usaban
`dia=(i % 28) + 1` sobre un agosto que empieza en sábado, así que un fixture de "quince partidas" tenía
cinco fines de semana dentro; se corrigieron *antes* de implementar y siguieron verdes con el código sin
filtrar, que es lo que demuestra que el arreglo no relajó lo que comprueban. El tercero, el que más
escuece: es la segunda vez que una cifra escrita en un documento se hereda sin volver a medirla. El
patrón repetido no es el error de medida — es que **nadie vuelve a medir lo que ya está escrito**.

## 2026-08-05 — La migración de identidad: el ensayo salvó dos partidas y el doble mintió

**Qué.** La identidad de jugador pasa de ser el nombre mostrado en Slack a ser el identificador, que no
cambia nunca. 1524 filas, 1523 con identificador. El renombre que partía a un jugador en dos queda unido
en 15 partidas bajo una sola identidad.

**Por qué importa.** Era el bloqueante del roadmap: el modelo de participación divide por días de la
temporada, y a quien está partido en dos le reparte los días entre dos jugadores, penalizando las dos
mitades. Y va **antes** del cambio del extractor: al revés, 32 de las últimas 40 filas se duplicarían.

**Decisiones, y las tres las forzó el contacto con los datos.**
- **El directorio incluye a los usuarios desactivados.** Es lo contrario de lo razonable a primera vista, y
  filtrarlos dejaba 110 filas sin resolver: tres jugadores del histórico ya salieron del workspace,
  `users.list` sigue devolviendo su nombre, y un identificador de Slack no se reasigna nunca.
- **Las filas cruzadas se reatribuyen, no se borran.** La spec decía eliminar las 8 que llevan el
  identificador de una persona y el nombre de otra, "porque no son partidas jugadas". El ensayo demostró lo
  contrario: seis duplican filas que el dueño real ya tiene, y **dos no existen en ningún otro sitio**.
  Borrarlas perdía dos partidas. *Descartado:* borrar, que era lo especificado.
- **El mapeo curado rellena, nunca pisa.** El diccionario del repo hereda un error de etiquetado; aplicado
  como override atribuía 111 partidas a otra persona.

**Aprendizaje.** Dos, y los dos duelen. El primero: **el doble en memoria era más permisivo que la tabla**.
No imponía el índice único, así que aceptaba escrituras que producción rechaza — diez tests verdes y seis
mutantes muertos, y la ejecución real reventó a mitad. Un doble imita las *restricciones* de lo que
sustituye, no solo su interfaz. El segundo: **dejar una fila intacta por prudencia no es neutral**. La fila
conflictiva del puzzle 1481 se queda donde está por diseño, y donde está es la clave que necesita su dueña
legítima. Lo prudente tiene consecuencias, y hay que declararlas en lugar de suponer que no existen.

## El clasificador de figuras: dos criterios, y el segundo tumbó al primer candidato

**Qué.** `tools/figures.py` convierte una cuadrícula de emojis en una figura —loro, flores, geométrico o
abstracto— con reglas deterministas. Acierta **24 de las 30** etiquetas humanas (80%) y el acuerdo es un gate
de la suite: `ACUERDO_MINIMO = 24`, y el conjunto dorado se parsea del source en lugar de copiarse.

**Por qué importa.** Bloqueaba el eje de figuras entero: el álbum, el resumen diario compuesto y cinco
medallas. Y era una pregunta con un no posible — el brief ya declaraba la alternativa: si el determinista no
llega, un modelo mirando el dibujo, que deja de ser gratis y no se cubre con golden tests.

**La decisión que cambia el método.** El primer candidato sacó **83% de acuerdo y 55% de flores sobre los
1521 patrones reales**, cuando el humano etiqueta el 37%. Acertaba el examen y no generalizaba: su regla
—«hay una fila verde ancha y algún amarillo»— se cumple cada vez más según crece la cuadrícula, así que se
comía las partidas largas. Se descartó por el **reparto**, no por el acierto. De ahí que la calibración se
mida contra dos criterios independientes y el informe publique los dos.

Los dos rasgos que lo resolvieron salieron de mirar qué separa las etiquetas, no de intuir: **el amarillo del
loro toca el cuerpo** (uno flotando en negro es pétalo, no pico) y **la flor necesita pétalos libres**.
Ninguno crece con el tamaño de la cuadrícula.

**Aprendizaje.** Un mutante sobrevivió, y era un hueco real: bajar el mínimo de pétalos de 3 a 1 dejaba la
suite verde porque **sube** el acuerdo a 25/30. Lo que justifica el 3 es el reparto, que necesita red y no
cabe en un test. Cuando un parámetro se elige por un criterio que la suite no puede ejecutar, hay que fijar
el **caso concreto que lo discrimina** y la **propiedad** que el criterio protege; un agregado puede mejorar
mientras el caso se rompe. Y una cifra heredada menos: la correlación entre jugar bien y acumular abstractos
baja de −0,37 a **−0,22**, sin tendencia monótona por tramos. El signo aguanta, la fuerza no.

## Tres vistas y el fallo que encontró la última

**Qué.** La ficha de jugador (`/t/<AAAA-MM>/j/<U…>`), la jornada en curso (`/hoy`) y el archivo de
temporadas (`/temporadas`). Con eso la Fase 2 queda cerrada salvo la tabla cruda.

**Por qué importa.** La ficha existe por una razón concreta: con imputación, **parte de tu media son
jornadas que no jugaste**, y el marcador no lo enseñaba. La ficha pone las dos medias juntas y publica la
diferencia con su signo —3,50 → 3,87 · +0,37 en un caso real—, que es la regla aplicada a una persona. Y
`/hoy` es la única vista de una jornada abierta, así que es la única que tiene que admitir que **hoy puede no
contar todavía**.

**Decisiones.**
- **Excepción declarada al ADR 0008.** La jornada abierta no está materializada y el cron corre cada hora, así
  que la media del día se calcula en el navegador. Lo que **no** se duplica es el umbral: la muestra mínima se
  lee de las reglas que viajan en la instantánea, y un test lo fija —mismo dato, umbral 5 no cuenta, umbral 3
  sí, sin tocar la vista—. Sin umbral publicado, la vista dice que no puede afirmarlo.
- **El enlace es comportamiento, no decoración.** La fila del marcador se extrajo a `filaDeMarcador()` y se
  exporta, así que «cada jugador enlaza a su ficha de esa temporada» se verifica con `node --test` y no con
  una captura.
- **Una temporada en curso no tiene campeón, tiene quien va ganando.** Dos mutantes distintos cazan esa
  distinción.

**Aprendizaje.** El archivo encontró un fallo que llevaba días escondido: `_de_la_temporada` filtraba con
`str(fila["date"]).startswith(temporada)`, y **ninguna fecha empieza por `0`**, así que la temporada 0 se
quedó sin una sola medalla de temporada —nadie con Fondista tras 181 jornadas— mientras las permanentes sí
aparecían. Ese contraste fue la pista. Eran **dos definiciones de pertenecer a una temporada**, una en
`seasons.temporada_de` y otra escrita a mano; ahora hay una. El medallero pasó de 6 filas a 17. La lección
general: un cambio de modelo (la temporada 0) rompe en silencio todo el código que reimplementaba el modelo
a mano, y lo que lo delata no es un test sino **una vista que enseña el agregado**.

## 2026-08-08 — El álbum de figuras: tres piezas hechas que no se tocaban entre sí

**Qué.** La instantánea de temporada pasa a publicar el **álbum**: cuántas partidas de cada categoría lleva
cada jugador, qué proporción de ellas dejó una figura reconocible y en qué puesto queda. `tools/album.py`,
puro, más una clave nueva en la carga útil.

**Por qué importa.** El patrón ya se guardaba (5.1), el histórico ya se había recuperado (5.2) y el
clasificador ya estaba calibrado (5.0) — y **ninguna de las tres piezas se tocaba con las otras**. Nadie
derivaba la categoría, así que el álbum no existía para ningún consumidor. Tres cosas terminadas pueden
sumar cero mientras falte el paso que las une, y ese paso no se ve en ninguna lista de tareas hechas.

**Decisiones.**
- **La puntuación se midió, no se eligió.** Cuatro criterios sobre los 18 jugadores con 10+ partidas: el
  recuento absoluto corona a quien más juega —un ranking de asistencia con otro nombre—; el ponderado por
  rareza corona al **segundo de la tabla de puntuación**, que anula el propósito del segundo eje; y
  solo-loros corona a quien tuvo suerte. Gana la **tasa por partida**, y se comprobó después contra los
  datos: los dos podios de la temporada 0 **no comparten a nadie**.
- **El mínimo también.** Con 3 partidas la temporada 0 la gana alguien con un 100% de tres. Con 5, 8 y 10 el
  líder es el mismo. Cinco es el umbral más bajo que mata la anomalía.
- **Una partida sin patrón no es un abstracto.** Abstracto es un veredicto sobre un dibujo, y ahí no hay
  dibujo: contarla castigaría a quien jugó cuando el pipeline aún descartaba la cuadrícula. Un fallo del
  sistema cobrado al jugador. Sale del denominador y la cobertura se publica aparte.
- **El álbum hereda los días de la temporada** en lugar de tener su propia regla. Cuesta una incoherencia
  menor —13 patrones de fin de semana cuentan en la temporada 0— y evita la que ya ha mordido dos veces.

**Aprendizaje.** Un test parametrizado sobre la constante que quiere probar deja de probarla. El fixture del
mínimo decía `[FLOR] * (MINIMO - 1)`, que es elegante y se lee bien — y hacía que bajar el umbral de 5 a 3
**siguiera pasando**, porque el fixture se ajustaba solo. Con literales (4 y 5) el mutante muere. La regla
general: el valor que la decisión fija se escribe a mano en el test; derivarlo del código convierte la
aserción en una tautología con buen aspecto.

## 2026-08-08 — El álbum a la vista, y una trampa que solo existía en producción

**Qué.** El bloque ÁLBUM DE FIGURAS en la vista de temporada y la tarjeta del álbum en la ficha. La tira va
agrupada —`🦜8 🌷60 📐3 🌀15`— y el ruido se apaga al 45%: está para que el recuento sea honesto, no para
competir con las figuras.

**Por qué importa.** El segundo eje del juego solo cumple su función si se ve al lado del primero. La frase
«los dos rankings premian a gente distinta» estaba medida y escrita en una spec; ahora el grupo la comprueba
de un vistazo, porque el podio del marcador y el del álbum están en la misma página y no comparten a nadie.

**Decisiones.**
- **La vista tiene que funcionar sin álbum antes que con él.** La web publicada lee lo que escribe el cron de
  `main`, que todavía no lo materializa, así que «instantánea sin álbum» no es un caso defensivo: es el
  estado actual de producción, y es el primer escenario del slice.
- **Un jugador sin partidas clasificadas no ve un 0%.** Un cero diría que dibujó mal; lo que pasa es que no
  hay dibujos que mirar. Quien sí tiene partidas y ninguna figura sí ve su 0%, porque eso sí es verdad.
- **El desbordamiento horizontal en móvil se reporta y no se arregla.** Lo causan las 181 barras de
  ESTADÍSTICAS, con o sin álbum —comprobado quitándolo—. Tocar esa vista sin slice es lo que el protocolo
  prohíbe, y «ya que estaba» es como se cuelan los cambios que nadie revisó.

**Aprendizaje.** **JSONB no conserva el orden de las claves.** El álbum publicaba su vocabulario como
diccionario `{loro, flores, geometrico, abstracto}`, y Postgres devuelve las claves de un `jsonb` ordenadas
por longitud y luego alfabéticamente: `abstracto` (9) habría llegado antes que `geometrico` (10), y la web
habría pintado el ruido en medio de las figuras que puntúan. Ningún test de Python podía cazarlo, porque
allí el diccionario conserva su orden de inserción — **el fallo solo existía al otro lado de la base de
datos**. Se vio porque antes de escribir la vista se miró qué devuelve de verdad una instantánea real. La
regla que queda: cuando el orden importa, se publica una lista; un diccionario en JSONB es un conjunto con
aspecto de secuencia.

## 2026-08-08 — Medallas de figuras: dos umbrales que no medían lo que decían

**Qué.** Las cinco medallas que miran el dibujo —Ornitólog@, Arquitect@, Florista, Coleccionista y
Abstract@— con sus umbrales rehechos. Con ellas el eje de figuras queda completo: clasificación, álbum y
logros.

**Por qué importa.** El brief marcaba estos umbrales como provisionales y decía por qué: se midieron con el
clasificador que luego se desmintió. Al remedirlos con el bueno, dos de los cuatro no medían nada parecido a
lo que decían. **Florista** pedía 5 flores y la lograba el **63%** de los pares jugador-mes, cuando estaba
etiquetada como «raro, 8%». **Abstract@** pedía 12 abstractos y la lograba el **0,8%**, etiquetada como
«común, 24%». Son justo los dos que dependen del reparto de categorías — y el reparto es lo que cambió al
calibrar.

**Decisiones.**
- **El recuento sale del álbum**, no de un segundo recuento en el módulo de medallas. Si la tira dice `🦜5`
  y `Ornitólog@` no salta, el logro parece roto, y esa clase de divergencia ya ha aparecido tres veces aquí.
- **La temporada 0 sale distorsionada y se acepta.** 13 de 21 jugadores son «Ornitólog@ legendario» porque
  son 181 jornadas con umbrales pensados para un mes. Es lo mismo que ya pasa con Fondista y Verdugo allí;
  darle a las figuras una regla de temporada propia sería una segunda definición de temporada.

**Aprendizaje.** **Un test puede pasar en verde con el fichero roto si mira la cadena y no la estructura.**
El símbolo nuevo del sprite se insertó dentro del comentario de la cabecera —ahí hay un `</svg>` de ejemplo
y el script cortó por el primero—, el SVG quedó mal formado y **las doce tarjetas se quedaron sin icono**,
también las siete que ya funcionaban. El test seguía verde: buscaba `id="coleccionista"` en el fichero
entero, y ahí estaba, comentado. Lo cazó abrir el navegador. Ahora quita los comentarios antes de mirar y
cuadra los `<symbol>` abiertos con los cerrados. La regla: cuando se afirma sobre un fichero estructurado,
se afirma sobre su estructura; buscar una subcadena es preguntarle al fichero si contiene unas letras, que
es otra pregunta.

Y de paso, la **tercera** aparición de la misma causa raíz: el resumen diario derivaba la temporada con
`str(fecha)[:7]`. Hoy funcionaba por casualidad —agosto de 2026 es a la vez el mes y el identificador de
temporada— y para cualquier fecha anterior calculaba las medallas sobre una temporada que no existe.

## 2026-08-08 — El resumen habla, y el mensaje real enseñó lo que ningún test veía

**Qué.** El mensaje diario pasa de tres líneas a un resumen con secciones —jugador del día, obra del día,
top 5 con el dibujo de cada uno, cabeza del álbum y comentarios de la jornada— y sigue llevando la captura.

**Por qué importa.** Todo lo que pasaba estaba en una imagen: no se lee en la notificación del móvil, no se
puede citar y no se puede buscar. Y son **dos premios y no uno** por evidencia: exigir mejor puntuación *y*
figura reconocible deja el premio vacío el 94% de los días, porque la figura sale de las partidas malas.

**Decisiones.**
- **La captura se conserva.** Sustituirla es una pregunta abierta del brief y no la decide un slice.
- **La redacción generativa queda fuera**, declarado: sin proveedor ni credencial, y cuesta dinero por
  jornada. Los detectores emiten **hechos** y no frases, así que cambiar quién redacta no los toca.
- **Los márgenes se remidieron** antes de fijarlos, como con las medallas. El del brief para «no inspirado»
  daba 0,48 por jornada con las reglas de hoy; con el margen que el propio brief pedía, 0,24.

**Aprendizaje.** **Imprimir el mensaje real encontró tres cosas que ningún test buscaba.** Un día duro
llenaba la sección con tres «se ha rajado» seguidos —la notabilidad ordenaba y la clase más notable se comía
el hueco—; la concordancia estaba rota, «Carlos, Edu Noeda **no ha** aparecido»; y se llamaba rajada a
alguien que jugó una partida en marzo, porque las ausencias se medían contra quien jugó alguna vez en lugar
de contra quien juega esta temporada. Ninguna de las tres es un fallo de lógica: son fallos de **lo que se
lee**, y la única forma de verlos es leerlo.

Y un mutante sobrevivió señalando un test que no cubría lo que decía: el de «no repetir el mismo chiste»
usaba las ausencias, que van agrupadas en un solo hecho, así que la línea salía una vez con deduplicación y
sin ella. La regla general que deja: **un test que verifica una regla tiene que usar un caso donde la regla
sea lo único que decide**; si otra parte del código ya produce el resultado esperado, el test mide esa otra
parte.
