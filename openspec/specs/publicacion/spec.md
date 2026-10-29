# Spec de `publicacion`

Spec **viva** del dominio `publicacion` (ver `openspec/README.md`). Se edita directamente en la rama de cada cambio,
junto al código y los tests que la cumplen ([ADR 0009](../../decisions/0009-specs-vivas.md)). Cada Requirement
lleva en un comentario los change packs de los que sale, archivados en `openspec/changes/archive/`.

## Requirement: El resumen anuncia las medallas nuevas de la jornada, no el estado acumulado

<!-- origen: feat-medallas-resumen (added), feat-solo-dias-laborables (modified) -->

El texto que acompaña al resumen lleva una sección con las medallas que alguien ha **ganado en esa
jornada**: las de temporada que no tenía antes y las permanentes conseguidas ese día.

No lleva el estado acumulado del mes. Medido sobre julio, el acumulado produce líneas de diez nombres que
se repetirían idénticas veinte días seguidos, porque las tres medallas comunes las tiene entre el 34% y el
48% del grupo. El estado completo es información de la ficha de jugador, no del mensaje diario.

La sección **solo aparece si hay al menos una medalla nueva**. Una sección vacía ocupa espacio y no dice nada.

**En sábado y domingo nunca hay sección**, porque en un día que no cuenta no se gana nada.

Dos mecanismos independientes, y hacen falta los dos. El cron pasa a **lunes-viernes**, así que en fin de
semana no se publica resumen: sin él, un cron dominical republicaría la jornada del viernes con sus
medallas, porque la jornada se deriva de `max(wordle_id)` y en fin de semana no llegan filas nuevas. Y el
cálculo filtra igualmente, para el caso en que el workflow se dispare a mano (`workflow_dispatch`) o alguien
publique un resultado en sábado.

```yaml
checks:
  - type: slack-api
    method: files_upload_v2
    describe: el initial_comment incluye la sección de medallas cuando hay alguna
```

#### Scenario: una medalla ganada hoy se anuncia
- GIVEN un jugador que alcanza el umbral de una medalla en la jornada que se publica
- WHEN se compone el texto del resumen
- THEN el texto contiene el nombre de la medalla y del jugador

#### Scenario: una medalla que ya tenía no se repite
- GIVEN un jugador que alcanzó el umbral en una jornada anterior
- WHEN se compone el texto de hoy
- THEN el texto no menciona esa medalla

#### Scenario: sin novedades, no hay sección
- GIVEN una jornada en la que nadie gana ninguna medalla nueva
- WHEN se compone el texto del resumen
- THEN el texto no menciona las medallas

#### Scenario: una jornada de fin de semana no anuncia medallas
- GIVEN una jornada que cae en sábado o domingo, con resultados publicados
- WHEN se compone el texto del resumen
- THEN el texto no incluye sección de medallas, y conserva el saludo y el enlace

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

## Requirement: Una medalla permanente se anuncia una sola vez

<!-- origen: feat-medallas-resumen (added) -->

Una medalla permanente se anuncia en el resumen de la jornada en la que se consigue, y no vuelve a
anunciarse. El resto de jornadas el mensaje no la repite.

#### Scenario: la gesta del día se anuncia
- GIVEN un jugador que resuelve en un intento en la jornada que se publica
- WHEN se compone el texto
- THEN el mensaje anuncia su medalla permanente

#### Scenario: una gesta antigua no se repite
- GIVEN un jugador que resolvió en un intento en una jornada anterior
- WHEN se compone el texto de hoy
- THEN el mensaje no vuelve a anunciarla

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

## Requirement: El resumen conserva lo que ya publicaba

<!-- origen: feat-medallas-resumen (added) -->

Añadir las medallas no altera el resto del mensaje: la captura se sigue adjuntando y el enlace a la web
sigue estando. La sección se añade, no sustituye.

#### Scenario: el enlace sigue en el mensaje
- GIVEN cualquier composición del texto del resumen
- WHEN se compone
- THEN el texto sigue conteniendo el enlace a la web

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

## Requirement: El nombre que se publica sale del catálogo, y renombrar reescribe el pasado

<!-- origen: chore-nombres-de-logros (modified) -->

El texto del resumen usa **el nombre del catálogo**, no una cadena escrita en el mensaje. Renombrar una
medalla cambia por tanto lo que lee el canal, sin tocar la composición del mensaje.

Y tiene una consecuencia que conviene decir: como el palmarés **se calcula y no se guarda**, renombrar
reescribe el pasado. Quien ganó `Pleno` en febrero, ahora ganó `Metrónom@`. Aquí no hay daño —la rama no está
mergeada, así que nunca se publicó— pero la propiedad es permanente: **cada renombrado futuro reescribe todo
el histórico de esa medalla**. Es el precio de no almacenarlas, y se paga en cada bautizo.

#### Scenario: el nombre anunciado es el del catálogo
- GIVEN una medalla ganada en la jornada que se publica
- WHEN se compone el texto del resumen
- THEN el nombre que aparece es el que declara el catálogo

#### Scenario: dos medallas nunca comparten nombre
- GIVEN el catálogo de medallas
- WHEN se listan sus nombres
- THEN no hay dos iguales, porque el canal no podría distinguirlas

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py

## Requirement: El objetivo de la captura diaria es configurable, y va entero

<!-- origen: feat-captura-apunta-a-la-v2 (added) -->

De qué web se saca la captura sale de la configuración del entorno, no de una constante en el código. Y lo
configurable es **el objetivo completo** —URL, el selector que confirma que hay datos y el que se
fotografía—, porque son tres datos de la misma decisión: los de la v1 no sirven para la v2.

Cambiar solo la URL dejaba el workflow esperando quince segundos un elemento inexistente y el resumen sin
publicar. Yendo juntos, ese estado roto deja de ser expresable.

El enlace del mensaje es el del **mismo** objetivo capturado: una foto de una web con un enlace a otra es la
forma más rápida de que nadie se fíe de ninguna de las dos.

#### Scenario: el objetivo sale del entorno
- GIVEN la configuración pide un objetivo concreto
- WHEN se prepara la publicación
- THEN se usa ese, con su URL y sus selectores

#### Scenario: sin configuración se usa lo que está desplegado
- GIVEN ninguna configuración
- WHEN se prepara la publicación
- THEN el objetivo es la v1

#### Scenario: el enlace apunta a donde la captura
- GIVEN un objetivo
- WHEN se compone el texto
- THEN el enlace es el de ese objetivo

#### Scenario: un objetivo desconocido aborta
- GIVEN una configuración que pide un objetivo inexistente
- WHEN se prepara la publicación
- THEN la ejecución falla, en lugar de usar el objetivo por defecto

verified-by:
  - tests/slices/captura-apunta-a-la-v2/test_captura.py
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py


## Requirement: Una publicación fallida termina en error

<!-- origen: feat-captura-apunta-a-la-v2 (added) -->

Si la captura o la subida fallan, la ejecución termina con código distinto de cero.

Hasta ahora cualquier fallo se imprimía y la ejecución terminaba bien: el grupo dejaba de recibir el
resumen y en Actions estaba todo verde. Un fallo silencioso en la única salida visible del sistema es peor
que un fallo ruidoso.

#### Scenario: una captura fallida sale en rojo
- GIVEN que la captura lanza
- WHEN termina la ejecución
- THEN el código de salida no es cero

#### Scenario: una subida fallida sale en rojo
- GIVEN que la subida a Slack no publica
- WHEN termina la ejecución
- THEN el código de salida no es cero

verified-by:
  - tests/slices/captura-apunta-a-la-v2/test_captura.py

## Requirement: El resumen diario cuenta la jornada en texto

<!-- origen: feat-resumen-diario-compuesto (added), feat-resumen-con-podios (modified) -->

El mensaje que el bot publica cada tarde incluye, además de las medallas y el enlace, estas secciones
derivadas de los datos del día y de la temporada:

1. **Jugador del día** — la mejor puntuación de la jornada, con todos los empatados.
2. **Obra del día** — la figura **más rara de la temporada** entre las dibujadas ese día.
3. **Tres podios**, en este orden: el **marcador general**, el **SuperWordleBros** y las **figuras**.

Cada podio es un **podio ASCII de bloques macizos** (`█`) dentro de un bloque de código, con su título
encima: el 1º en el centro y más alto, el 2º a la izquierda y el 3º a la derecha; encima de cada escalón, su
puesto, su nombre y su cifra (la media en el marcador, los puntos en el juego, la puntuación media en las
figuras). Los puestos son los de la clasificación —un empate comparte escalón—; en un escalón con más de tres
nombres se nombran tres y se dice cuántos más hay. **Ninguna línea de un podio pasa de 32 caracteres**, y un
nombre de más de 10 se acorta, para que se lea en el móvil sin desplazarse.

Antes del podio del juego va una línea con el ganador del nivel que se jugó ese día —el último nivel
congelado anterior a la jornada del resumen—, su tiempo con centésimas y cuántos lo terminaron. El podio del
juego es el de la clasificación del juego del mes de la jornada del resumen.

Son **dos premios y no uno** por evidencia: exigir mejor puntuación *y* figura reconocible deja el premio
vacío el 94% de las jornadas, porque la figura sale de las partidas que salen mal.

Ninguna sección se inventa: un ranking sin nadie no pinta podio, y los demás salen igual. Y el texto **no
recalcula nada**: el marcador, el álbum y el juego salen de las mismas funciones que la instantánea que
publica la web.

#### Scenario: el marcador sale como podio
- GIVEN una temporada con al menos tres clasificados
- WHEN se compone el resumen
- THEN hay un bloque de código con bloques `█`, el 1º en la columna central y con el escalón más alto, y sus
  tres nombres con su media

#### Scenario: los podios van en su orden
- GIVEN datos para el marcador, el juego y las figuras
- WHEN se compone el resumen
- THEN el podio del marcador va antes que el del juego, y el del juego antes que el de figuras

#### Scenario: el juego lleva el ganador del día
- GIVEN un nivel congelado anterior a la jornada, con marcas
- WHEN se compone el resumen
- THEN antes del podio del juego hay una línea con el número del nivel, el ganador, su tiempo con centésimas y
  cuántos lo terminaron

#### Scenario: el empate comparte escalón
- GIVEN dos jugadores empatados en el 1º y cinco empatados en el 3º
- WHEN se pinta el podio
- THEN los dos primeros van en el escalón central, y en el 3º se nombran tres y se dice «y 2 más»

#### Scenario: el podio cabe en el móvil
- GIVEN nombres de más de 10 caracteres
- WHEN se pinta el podio
- THEN ninguna línea pasa de 32 caracteres

#### Scenario: un ranking vacío no pinta podio
- GIVEN una temporada sin marcas del juego
- WHEN se compone el resumen
- THEN no hay podio del juego, y el del marcador y el de figuras salen en su orden

```yaml
checks:
  - type: regex
    file: tools/resumen.py
    pattern: 'bloque_top\(resultados, temporada, jornada\),[\s\S]*?bloque_juego\(resultados, temporada, jornada, niveles or \(\), marcas or \(\)\),\s+bloque_album\(resultados, temporada\),'
    describe: "los podios en orden — marcador, juego, figuras"
  - type: regex
    file: tools/post_ranking.py
    pattern: 'niveles, marcas = leer_juego\(\) if resumen_activo\(\) else'
    describe: el publicador lee el juego para el resumen
```

verified-by:
  - tests/slices/resumen-diario-compuesto/test_podios.py

## Requirement: El resumen comenta los hechos notables de la jornada

<!-- origen: feat-comentarios-de-la-jornada (added) -->

El mensaje diario termina con una sección de comentarios sobre lo que ha pasado: quién resolvió un día
imposible, quién quedó muy por encima o por debajo de la media, y quién no apareció el día duro.

**Los hechos se detectan de forma determinista y la frase sale de un catálogo.** Los detectores emiten
hechos, no texto, de modo que cambiar quién redacta —una plantilla hoy, un modelo mañana— no toca la
detección.

Los umbrales están **calibrados por frecuencia**: un chiste que sale a diario deja de ser chiste. El de día
difícil se **reutiliza** del catálogo de medallas en lugar de declarar uno propio.

Una persona aparece **una sola vez** por jornada, la sección se limita a unos pocos comentarios, y una
jornada sin hechos no produce sección.

El texto es **reproducible**: dos ejecuciones sobre la misma jornada dan exactamente el mismo mensaje, sin
azar y sin reloj.

#### Scenario: resolver rápido un día duro se señala
- GIVEN una jornada de media alta y alguien que resuelve en dos intentos o menos
- WHEN se componen los comentarios
- THEN se comenta ese hecho

#### Scenario: quedarse muy por encima de la media se comenta
- GIVEN alguien cuyo resultado está muy por encima de la media del día
- WHEN se componen los comentarios
- THEN se comenta, con el margen calibrado y no con uno menor

#### Scenario: la ausencia en día difícil usa el umbral de las medallas
- GIVEN un día difícil y alguien de la temporada que no publica
- WHEN se componen los comentarios
- THEN se comenta la ausencia, con el mismo umbral de día difícil que usan las medallas

#### Scenario: una persona no sale dos veces
- GIVEN alguien que dispara más de un detector el mismo día
- WHEN se componen los comentarios
- THEN aparece una sola vez

#### Scenario: la sección se limita
- GIVEN una jornada que dispara muchos detectores
- WHEN se componen los comentarios
- THEN se publican como mucho unos pocos

#### Scenario: sin hechos no hay sección
- GIVEN una jornada sin ningún hecho notable
- WHEN se compone el resumen
- THEN no aparece la sección de comentarios

#### Scenario: el mismo día produce el mismo texto
- GIVEN una jornada concreta
- WHEN se compone el resumen dos veces
- THEN el texto es idéntico

#### Scenario: sin dificultad calculable no se comenta
- GIVEN una jornada con menos jugadores de los que hacen falta para calibrar la media
- WHEN se componen los comentarios
- THEN no se comenta nada, porque no hay contra qué comparar

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py

## Requirement: El resumen comenta también a qué hora se juega

<!-- origen: feat-comentarios-por-la-hora (added) -->

Además de las notas, el resumen mira **cuándo** se publicó cada resultado: quién llega el último con el día
ya vencido, y quién llega el último **y además** con una nota muy por encima de lo que ha hecho el grupo —
que es el chiste de haber visto antes los resultados de los demás.

La hora sale de cuándo se registró la fila, que aproxima la publicación con un margen de hasta una hora
—lo que tarda el cron—: suficiente para distinguir «por la mañana» de «a media tarde», que es lo único que
estos comentarios necesitan.

**Solo se usa si esa marca cae el mismo día que el puzzle.** Las filas recuperadas en el backfill se
insertaron todas de golpe en otra fecha: ahí el margen no es de una hora sino de meses, y el comentario
señalaría a alguien por algo que no hizo.

Y se añade el caso más raro de todos: **acertar a la primera**.

#### Scenario: el último en publicar con mucho hueco se comenta
- GIVEN una jornada en la que el último publica muy por detrás del resto y con el día avanzado
- WHEN se componen los comentarios
- THEN se comenta su retraso

#### Scenario: publicar a la vez que los demás no es llegar tarde
- GIVEN una jornada en la que todos publican seguidos
- WHEN se componen los comentarios
- THEN no se comenta ningún retraso

#### Scenario: sin hora utilizable no se comenta el retraso
- GIVEN resultados cuya marca de registro es de otro día
- WHEN se componen los comentarios
- THEN no se comenta el retraso, porque esa hora no dice cuándo se publicó

#### Scenario: llegar tarde y además clavarla es otro chiste
- GIVEN alguien que publica el último y con una nota muy por encima de la media del día
- WHEN se componen los comentarios
- THEN se comenta la sospecha, no el simple retraso

#### Scenario: acertar a la primera se señala
- GIVEN alguien que resuelve en un solo intento
- WHEN se componen los comentarios
- THEN es lo primero que se comenta

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py

## Requirement: La imagen del resumen es el titular, no la página entera

<!-- origen: feat-captura-del-titular (modified) -->

La captura que acompaña al mensaje diario es **el titular de la temporada y el podio**: quién lidera, por
cuánta diferencia, y las tiras de los tres primeros.

Antes se fotografiaba la vista completa —marcador, logros, álbum y estadísticas—. Con el resumen en texto
eso **dice dos veces lo mismo**, y además llega a Slack como una tira larguísima que se ve en miniatura.

El objetivo **espera al mismo selector que fotografía**. Esperar a uno y capturar otro deja la puerta
abierta a fotografiar algo a medio pintar.

Y si el elemento no está, el fallo **dice cuál y en qué URL**: antes daba un error de objeto nulo que no
identificaba ni el selector ni la página.

#### Scenario: se fotografía el titular y el podio
- GIVEN el objetivo de la v2
- WHEN se prepara la captura
- THEN el elemento que se fotografía es el titular, no el contenedor de toda la vista

#### Scenario: se espera a lo que se va a fotografiar
- GIVEN el objetivo de la v2
- WHEN se compara lo que espera con lo que captura
- THEN son el mismo elemento

#### Scenario: un selector que no encaja se declara
- GIVEN un objetivo cuyo elemento no existe en la página
- WHEN se intenta capturar
- THEN el error nombra el selector y la URL

verified-by:
  - tests/slices/captura-apunta-a-la-v2/test_captura.py

## Requirement: El resumen diario siempre tiene algo que decir

<!-- origen: feat-voz-de-la-jornada (added) -->

El mensaje de la tarde lleva **siempre** una frase que resume la jornada, aunque no haya ninguna señal del
canal ni ningún hecho notable. Es lo que separa un marcador de un informe: medido sobre la jornada en que se
propone esto —nueve jugadores, dificultad 3,89— los detectores encontraron **cero** hechos y el mensaje salió
sin una sola línea con tono.

El **registro** de la frase sale de la dificultad de la jornada, que ya se calcula: día fácil, día normal, día
duro. Así el tono lo elige el dato y no una decisión escrita a mano.

Además de la frase del día, el mensaje lleva **una pulla para quien manda en el marcador y otra para quien
manda en el álbum**, cuando hay líder. Sin líder de álbum —nadie llega al mínimo de partidas— esa frase no
sale: no se nombra a quien no tiene puesto.

Las frases salen de un **diccionario de refranes tradicionales y pullas escritas para el grupo**, con **quince
por registro**. Menos de diez y el grupo se las sabe en dos semanas; quince dan más de un mes sin repetir. No
se copia ninguna compilación ajena: el refrán tradicional es de dominio público, pero la selección y las
fichas de un refranero editado tienen dueño y el repositorio es público.

La frase se elige **derivándola del número de jornada**, no del reloj ni del azar. El proyecto es determinista
por contrato (§10), y es lo que permite comprobar el mensaje entero en un test y que dos ejecuciones del mismo
cron publiquen lo mismo. El precio declarado: el orden es cíclico y por tanto predecible si alguien se pone a
mirar.

Las frases de un mismo mensaje **no se repiten entre sí**, y las menciones del canal van **encima** de la
frase, no en su lugar: el día raro conserva su titular y el día corriente tiene voz.

```yaml
checks:
  - type: cli-command
    command: python3 tools/preview_resumen.py
    note: compone el mensaje de una jornada sin publicarlo, para revisarlo antes de que lo lea el grupo
```

#### Scenario: el día sin nada que contar tiene frase
- GIVEN una jornada sin hechos notables y sin señales del canal
- WHEN se compone el resumen
- THEN el mensaje lleva una frase que resume el día

#### Scenario: el registro lo elige la dificultad
- GIVEN una jornada que el grupo resolvió con muchos intentos
- WHEN se compone el resumen
- THEN la frase es de las del registro duro

#### Scenario: dos jornadas seguidas no repiten frase
- GIVEN dos jornadas consecutivas del mismo registro
- WHEN se componen sus resúmenes
- THEN las frases son distintas

#### Scenario: la misma jornada da el mismo mensaje
- GIVEN una jornada
- WHEN se compone su resumen dos veces
- THEN el texto es idéntico

#### Scenario: quien manda se lleva su pulla
- GIVEN una temporada con líder de marcador y líder de álbum
- WHEN se compone el resumen
- THEN el mensaje nombra a los dos, con frases distintas

#### Scenario: sin líder de álbum no se inventa la pulla
- GIVEN una temporada en que nadie llega al mínimo de partidas del álbum
- WHEN se compone el resumen
- THEN no sale frase de álbum

verified-by:
  - tests/slices/voz-de-la-jornada/test_voz.py


## Requirement: El mensaje no crece sin límite

<!-- origen: feat-voz-de-la-jornada (added) -->

El mensaje publica **como mucho tres añadidos** sobre los bloques que ya tenía. Sin tope, una jornada movida
encadenaría doce bloques —jugador del día, obra, marcador, figuras, tres comentarios, cinco menciones, frase,
dos pullas y meme— y eso es un muro de texto que **nadie lee en un canal de Slack**. El efecto sería el
contrario del que persigue este slice.

La prioridad, de más peso a menos:

1. **el meme del día**, si la jornada tiene una forma reconocible — es lo que describe lo que pasó;
2. **las menciones con más evidencia** — más reacciones, más respuestas, más distancia en la hora;
3. **la frase del día**, que cede el sitio cuando hay algo mejor.

Que la frase sea la última no la contradice: existe para el día que **no tiene nada que contar**, y ese día es
la única que hay, así que sale siempre que hace falta. Tope decidido por el dueño al implementar, después de
ver que lo especificado sin límite empeoraba el mensaje.

#### Scenario: la jornada con mucho material no encadena todo
- GIVEN una jornada con meme, cinco menciones y frase disponible
- WHEN se compone el resumen
- THEN se publican como mucho tres añadidos

#### Scenario: la frase cede el sitio cuando hay algo mejor
- GIVEN una jornada con meme y menciones suficientes para llenar el tope
- WHEN se compone el resumen
- THEN la frase del día no sale

#### Scenario: el día sin nada conserva su frase
- GIVEN una jornada sin meme y sin menciones
- WHEN se compone el resumen
- THEN la frase del día sale

verified-by:
  - tests/slices/voz-de-la-jornada/test_menciones.py
  - tests/slices/voz-de-la-jornada/test_senales.py
  - tests/slices/voz-de-la-jornada/test_voz.py


## Requirement: El meme del día describe la jornada, y si no la describe no sale

<!-- origen: feat-voz-de-la-jornada (added) -->

El mensaje puede llevar un **meme del día**: una plantilla de texto que nombra una forma reconocible de
jornada y se rellena con sus datos. Las formas son de la jornada, no del jugador: uno solo resuelve, todos
fallan, todos empatan en el mismo número, el líder de la temporada se hunde, el último de la tabla clava,
nadie dibuja nada.

**Es texto, nunca una imagen.** Subir una imagen ajena al canal desde un bot que tiene `files:write` sería un
problema de derechos y de permisos a la vez, y la plantilla en texto consigue el mismo chiste sin ninguno de
los dos. Por la misma razón las plantillas son **escritas para este canal** y no citas de guiones de
televisión ni de posts de foros: el refrán tradicional es de dominio público, un guion no.

Las condiciones se evalúan **en orden** y se usa la primera que se cumple, de modo que la forma más llamativa
gana sobre la genérica. Si no se cumple ninguna, **no hay meme**: forzar uno que no describe lo que pasó es
peor que no ponerlo, porque un chiste que no encaja delata que lo pone una máquina.

#### Scenario: la jornada con forma reconocible tiene meme
- GIVEN una jornada en que solo una persona resolvió la palabra
- WHEN se compone el resumen
- THEN el mensaje lleva el meme correspondiente a esa forma, con su nombre

#### Scenario: la jornada corriente no tiene meme
- GIVEN una jornada que no encaja en ninguna forma reconocida
- WHEN se compone el resumen
- THEN no sale ningún meme

#### Scenario: el meme no sube imágenes
- GIVEN una jornada con meme
- WHEN se publica el mensaje
- THEN el meme viaja como texto y no se adjunta ninguna imagen

#### Scenario: los comentarios no los sustituye la frase
- GIVEN una jornada con hechos notables
- WHEN se compone el resumen
- THEN los comentarios se publican y la frase también

verified-by:
  - tests/slices/voz-de-la-jornada/test_voz.py

## Requirement: El resumen diario cuenta cómo va la pelea por la cabeza del mes

<!-- origen: feat-tendencia-del-liderazgo (modified) -->

El mensaje diario, además de anunciar el relevo de la jornada, sitúa ese relevo en el mes: cuántas veces ha
cambiado la cabeza y cómo se reparten las jornadas **los dos que se la juegan**. Cuando no hay relevo pero
alguien lleva varias jornadas seguidas sin soltarla, se dice eso en su lugar.

La tendencia **no tiene línea propia**: acompaña al relevo o no aparece. Una línea diaria de tendencia se
simuló sobre un mes real y salía casi todos los días, repitiéndose, y llegaba a atribuir el liderazgo a quien
ya no lideraba.

#### Scenario: la tendencia del mes acompaña al relevo
- **WHEN** el relevo se anuncia y la cabeza ya había cambiado antes ese mes
- **THEN** se añade cuántas veces ha cambiado y el reparto de jornadas de los dos que se la juegan
- **AND** con un solo cambio no se añade nada

#### Scenario: el dominio en cabeza se cuenta
- **WHEN** nadie le quita la cabeza al líder desde varias jornadas seguidas
- **THEN** se dice cuántas lleva, en el mismo hueco que el relevo
- **AND** no se dice de dos empatados, porque un empate no es dominio de nadie

verified-by:
  - tests/slices/resumen-diario-compuesto/test_tendencia.py


## Requirement: La tensión del empate sube cuando el empate se repite

<!-- origen: feat-tendencia-del-liderazgo (modified) -->

Cuando la misma pareja vuelve a compartir el primer puesto, la frase no se repite igual: sube de tono con las
veces que llevan y dice cuántas son.

La escalada va por **recurrencia y no por duración**, y eso lo decide la medida: los empates consecutivos casi
no existen —los cinco de agosto de 2026 duran una sola jornada, y de las doce rachas del histórico once duran
una y solo una llegó a tres—, mientras que la misma pareja llega a empatar cuatro veces en jornadas salteadas.

#### Scenario: la tensión sube cuando el empate se repite
- **WHEN** la misma pareja vuelve a empatar en cabeza en la temporada
- **THEN** la frase es neutra la primera vez, insistente a partir de la segunda y tensa a partir de la cuarta
- **AND** dice cuántas veces llevan empatados

verified-by:
  - tests/slices/resumen-diario-compuesto/test_tendencia.py


## Requirement: El meme del día no repite la misma frase

<!-- origen: fix-variedad-de-frases (modified) -->

Cada forma de jornada tiene **varias** plantillas, y la que sale la elige el número de jornada. Con una sola
plantilla por forma el catch-all `dia-de-dos-mundos` era el 83% de los memes publicados en 199 jornadas, y en
un mes real salió cuatro veces en diez jornadas.

Toda forma declarada tiene su condición implementada: escribir plantillas sin condición daba la falsa
impresión de variedad y era texto que nunca se ejecutaba.

#### Scenario: la misma forma no publica siempre la misma frase
- **WHEN** la misma forma de jornada se repite en jornadas distintas
- **THEN** el texto rota entre las variantes de esa forma

#### Scenario: no se afirma que nadie dibujó cuando no hay cuadrículas
- **WHEN** no se guardó ningún patrón de la jornada
- **THEN** no se dice que no hubo figuras, porque no saberlo no es lo mismo que no haberlas

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py
  - tests/slices/resumen-diario-compuesto/test_resumen.py
  - tests/slices/voz-de-la-jornada/test_memes.py


## Requirement: La sospecha no repite el molde

<!-- origen: fix-variedad-de-frases (modified) -->

Las frases de sospecha no comparten todas la misma forma: unas citan la nota y otras la insinúan, y no todas
llevan el mismo emoji. Con 🤨 en las 24 frases y la nota en 22 de 24, veinticuatro textos distintos se leían
como un solo chiste repetido.

#### Scenario: la sospecha no repite el molde
- **WHEN** la sospecha se comenta en varias jornadas
- **THEN** una parte de las frases sale sin el emoji y sin citar la nota

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py
  - tests/slices/resumen-diario-compuesto/test_resumen.py
  - tests/slices/voz-de-la-jornada/test_memes.py


## Requirement: La jornada no se publica dos veces

<!-- origen: fix-publicacion-idempotente (added) -->

Antes de publicar, se comprueba si el canal ya tiene la captura de la jornada que toca. Si la tiene, la
ejecución termina con éxito sin publicar y **sin sacar la captura**.

La jornada viaja en el título de la captura, que es lo que hace la comprobación posible sin guardar estado en
ninguna parte ni consultar el reloj. Se prefirió a comparar fechas porque una publicación muy retrasada puede
cruzar la medianoche UTC.

Existe porque el grupo recibió el mismo resumen dos veces: el cron no se disparó por una caída de Actions, se
lanzó a mano, y el programado llegó dos horas tarde y publicó de nuevo.

#### Scenario: la jornada no se publica dos veces
- **WHEN** el canal ya tiene la captura de la jornada que toca publicar
- **THEN** no se vuelve a publicar y la ejecución termina bien
- **AND** no se saca la captura, porque es el paso caro

#### Scenario: solo cuenta lo que publicó el bot
- **WHEN** un mensaje de una persona lleva un fichero con ese mismo título
- **THEN** no bloquea la publicación

#### Scenario: si el canal no se puede leer se publica
- **WHEN** no se puede comprobar si ya se publicó porque el canal no responde
- **THEN** se publica igualmente, porque un canal caído no puede dejar al grupo sin mensaje

verified-by:
  - tests/slices/captura-apunta-a-la-v2/test_captura.py


## Requirement: El meme del día remite a algo reconocible

<!-- origen: feat-memes-con-referencias (modified) -->

El registro de memes está poblado con referencias de cine, series, videojuegos, televisión e internet,
**adaptadas al juego** en lugar de citadas literalmente. Un meme que no remite a nada no es un meme.

Las plantillas con referencia van **intercaladas** con las genéricas, no añadidas al final: la variante se
elige por número de jornada, así que apiladas al final los índices bajos seguirían dando siempre las
genéricas y las referencias no llegarían a publicarse.

#### Scenario: el meme cita algo reconocible
- **WHEN** se publica el meme del día
- **THEN** una parte sustancial del registro de cada forma remite a algo identificable
- **AND** las referenciadas están repartidas por el ciclo, no agrupadas al final

verified-by:
  - tests/slices/resumen-diario-compuesto/test_tendencia.py
  - tests/slices/voz-de-la-jornada/test_memes.py


## Requirement: Los ausentes se nombran por orden de clasificación

<!-- origen: feat-memes-con-referencias (modified) -->

Cuando faltan más personas de las que caben, los nombrados son los **mejor clasificados** de entre los
ausentes: la ausencia de quien va segundo es más noticia que la de quien va decimoquinto. Antes se ordenaba
por nombre, así que salía nombrado quien tuviera la inicial más baja.

#### Scenario: los ausentes se nombran por orden de clasificación
- **WHEN** faltan más personas de las que se pueden nombrar
- **THEN** se nombran los mejor clasificados, en ese orden
- **AND** no se nombran por orden alfabético

verified-by:
  - tests/slices/resumen-diario-compuesto/test_tendencia.py
  - tests/slices/voz-de-la-jornada/test_memes.py


## Requirement: La guarda de duplicados no depende de cómo Slack guarde el título

<!-- origen: fix-marca-de-jornada (modified) -->

Para saber si la jornada ya se publicó se busca **la marca de la jornada** dentro del título de la captura, no
el título completo.

Comparar el título entero falló en producción: Slack convierte el emoji a su código corto, así que el texto
que devuelve el canal nunca es igual al que se envió, la guarda no detectaba nada y el grupo recibió el
resumen por triplicado dos días seguidos.

La marca va anclada para que no coincida por prefijo con una jornada de más cifras.

#### Scenario: la guarda reconoce el título tal como lo devuelve Slack
- **WHEN** el canal devuelve el título con el emoji convertido a su código corto
- **THEN** la jornada se reconoce como ya publicada

#### Scenario: la marca no confunde jornadas que comparten dígitos
- **WHEN** el título lleva una jornada cuyo número empieza por el de la buscada
- **THEN** no se da por publicada

verified-by:
  - tests/slices/captura-apunta-a-la-v2/test_captura.py


## Requirement: El mensaje abre con la palabra de la jornada y su significado

<!-- origen: feat-palabra-del-dia (added) -->

El resumen empieza con la palabra que el grupo ha jugado, en mayúsculas, y su primera acepción. Es el único
dato que el mensaje puede aportar que el grupo no tenga ya: cada uno conoce su resultado, pero nadie ve la
palabra escrita ni lo que significa.

Sin acepción se publica la palabra sola. Sin palabra el mensaje sale igual, sin esa línea, y la ejecución no
falla: es un adorno, no un requisito.

La palabra entra en el compositor **por parámetro**: averiguarla es red, y la red vive en el borde, así que el
mensaje entero sigue fijándose en un test.

#### Scenario: la palabra abre el mensaje
- **WHEN** se conoce la palabra de la jornada
- **THEN** es la primera línea del mensaje, en mayúsculas y con su primera acepción

#### Scenario: sin acepción se publica la palabra sola
- **WHEN** la palabra no tiene definición disponible
- **THEN** se publica la palabra sin acepción

#### Scenario: sin palabra el mensaje sale igual
- **WHEN** no se puede averiguar la palabra
- **THEN** el mensaje se publica sin esa línea y la ejecución no falla

verified-by:
  - tests/slices/palabra-del-dia/test_palabra.py


## Requirement: El sistema no entrega palabras de partidas sin jugar

<!-- origen: feat-palabra-del-dia (added) -->

Pedir la palabra de una jornada posterior a la última que existe en la tabla **no devuelve nada**, aunque esté
disponible en el origen.

El origen trae dos mil entradas, así que sin esta condición bastaría cambiar un número para leer meses por
delante. El repositorio es público y la liga es competitiva: la propiedad de no poder mirar por delante tiene
que estar en el código y defendida por un test, no en la buena voluntad de quien lo ejecute.

#### Scenario: nunca una palabra sin jugar
- **WHEN** se pide la palabra de una jornada posterior a la última jugada
- **THEN** no se devuelve, ni por la función que la busca ni por el flujo completo

#### Scenario: nada de la palabra se guarda
- **WHEN** se publica el mensaje
- **THEN** ni la palabra ni la lista de soluciones se escriben en ningún sitio

verified-by:
  - tests/slices/palabra-del-dia/test_palabra.py


## Requirement: Al empezar el mes se publica el podio del que cierra

<!-- origen: feat-podio-de-cierre-de-mes (added) -->

Una vez al mes, el canal recibe el podio de la temporada cerrada con su imagen, la felicitación al campeón y
el ánimo para la que empieza.

**Qué mes se celebra sale de los datos, no del reloj**: es el anterior al del último resultado de la tabla, y
tiene que ser consecutivo. Si el mes nuevo aún no tiene resultados no se celebra nada, porque «el anterior»
sería un mes ya celebrado. La temporada histórica no se celebra: no cerró un mes.

El podio lleva los empates enteros, igual que el marcador diario. Con empate en el primer puesto se felicita a
todos los empatados y no se atribuyen medallas a uno solo.

La imagen es **la captura del podio de esa temporada en la web**, para que el mensaje y la página no puedan
decir cosas distintas.

El mensaje es idempotente: el título de la imagen lleva el mes celebrado, y si el canal ya lo tiene no se
repite. Eso es lo que permite que el cron corra varios días seguidos sin duplicar, y lo que hace que una
ventana descartada no pierda el cierre.

#### Scenario: el mes que cierra sale de los datos
- **WHEN** se decide qué mes celebrar
- **THEN** es el anterior al del último resultado, y consecutivo con él

#### Scenario: sin mes nuevo no se celebra nada
- **WHEN** el mes nuevo todavía no tiene resultados
- **THEN** no se publica nada, no se saca la captura y la ejecución termina bien

#### Scenario: el podio lleva los empates enteros
- **WHEN** varias personas comparten un puesto del podio
- **THEN** suben todas

#### Scenario: el cierre no se publica dos veces
- **WHEN** el canal ya tiene el podio de ese mes
- **THEN** no se vuelve a publicar

verified-by:
  - tests/slices/captura-apunta-a-la-v2/test_captura.py
  - tests/slices/podio-de-cierre-de-mes/test_podio.py


## Requirement: La comprobación de duplicados alcanza los días que el disparador corre

<!-- origen: fix-historial-del-podio (modified), fix-podio-historial-por-fecha (modified) -->

Cuánto historial hay que leer para saber si algo ya se publicó **depende de qué se busca**: un mensaje diario
se reconoce minutos después de publicarse, pero uno mensual puede llevar días en el canal cuando se comprueba.

El cierre de mes lee el canal **por fecha**: todo lo publicado desde una semana antes del arranque del mes
nuevo, sin tope de mensajes. Contando mensajes se republicó dos veces, porque la ventana se quedaba corta cada
vez que el canal crecía.

#### Scenario: la comprobación alcanza los días que el cron corre
- **WHEN** se comprueba si el mes ya se celebró y el mensaje original quedó más atrás de 150 mensajes
- **THEN** se lee desde una fecha anterior al arranque del mes nuevo, se encuentra y no se republica

verified-by:
  - tests/slices/podio-de-cierre-de-mes/test_podio.py
  - tests/slices/podio-de-cierre-de-mes/test_victoria.py


## Requirement: Las frases concuerdan en género con una forma declarada

<!-- origen: feat-concordancia-de-genero (added) -->

Los adjetivos y participios de las frases concuerdan con la forma gramatical de la persona nombrada, y esa
forma **está declarada en una tabla**: no se deduce del nombre en tiempo de ejecución.

El motivo es que equivocarse aquí no es un fallo de concordancia — es dirigirse mal a un compañero
identificable delante de todo el grupo. Una tabla concentra el dato en un sitio, así que un error se corrige
una vez, y hace explícito quién lo declaró.

Con varias personas se usa la forma femenina solo si todas la tienen declarada así, y la masculina en
cualquier grupo mixto. **Con alguien sin declarar se usa la forma neutra**: el sistema no supone nada de quien
no consta, así que un jugador nuevo no hereda la suposición de nadie.

#### Scenario: la frase concuerda en género
- **WHEN** una frase lleva un participio que cambia con el género
- **THEN** concuerda con la forma declarada de esa persona

#### Scenario: quien no está declarado sale en neutro
- **WHEN** se nombra a alguien que no está en la tabla
- **THEN** se usa la forma neutra en lugar de suponer una

#### Scenario: un grupo mixto va en masculino
- **WHEN** se nombra a varias personas con formas distintas
- **THEN** se usa la masculina; y la femenina solo si todas lo son

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py


## Requirement: El meme del día de varios culos se apoya en el refranero

<!-- origen: feat-memes-de-culo-con-refranero (modified) -->

Las frases de ese registro se construyen sobre **expresiones hechas reales**, cada una usada con su
significado: el chiste ya está en el refranero que el grupo tiene en la cabeza, así que la frase solo tiene que
traerlo al marcador. Una frase inventada tiene que ser graciosa por sí sola; una que se apoya en una expresión
conocida ya lo es.

Ninguna expresión se repite más de dos veces en el registro: uno que gira sobre una sola suena a una sola
broma, que es el defecto que ya tuvo el registro de la sospecha con su molde repetido.

El registro es coloquial y vulgar, y **habla de la jornada y no de nadie**: usa el recuento y el total, nunca
un nombre. Los sujetos son personas identificables y el mensaje se publica en un canal del trabajo.

#### Scenario: el registro de culos va sobre expresiones hechas
- **WHEN** se publica el meme de un día de varios culos
- **THEN** la frase se apoya en una expresión hecha usada con su significado
- **AND** ninguna expresión domina el registro

verified-by:
  - tests/slices/resumen-diario-compuesto/test_tendencia.py
  - tests/slices/voz-de-la-jornada/test_memes.py


## Requirement: El comentario de la obra del día usa el registro de su categoría

<!-- origen: feat-memes-de-culo-con-refranero (modified) -->

Cuando la obra del día es de una categoría con material propio, el comentario sale de ese registro y no del
genérico, con el nombre de quien la firmó. Los comentarios de dibujo llevan nombre desde siempre, así que es
ahí donde el chiste tiene sentido.

Todas las frases de un registro de categoría llevan **la palabra de esa categoría**: si el chiste está solo en
el emoji, el registro no aporta nada sobre el genérico.

Y ninguna comenta **el cuerpo de quien juega**. La broma va sobre el dibujo, la suerte y la palabra: los
sujetos son personas identificables, el mensaje lo publica un bot en un canal del trabajo, y una expresión
sobre la mala suerte y una que atribuye un acto sexual a alguien con nombre no cuestan lo mismo.

#### Scenario: el comentario del dibujo lleva la broma de su categoría
- **WHEN** la obra del día es de una categoría con registro propio
- **THEN** el comentario sale de ese registro, con el nombre de quien la firmó
- **AND** todas sus frases llevan la palabra de la categoría
- **AND** ninguna comenta el cuerpo de quien juega

verified-by:
  - tests/slices/resumen-diario-compuesto/test_tendencia.py
  - tests/slices/voz-de-la-jornada/test_memes.py


## Requirement: La obra del día se comparte cuando hay empate

<!-- origen: feat-obra-del-dia-compartida (modified) -->

El mérito de un dibujo lo deciden la rareza de su categoría en la temporada, la simetría y los intentos. **Gana
todo el que empate en los tres**, y el mensaje los nombra a todos.

El nombre ordena la lista para que el resultado no dependa del orden en que llegaron los datos, pero no decide
quién gana: usándolo como último criterio, un cuarto de los premios se repartía por orden alfabético —medido,
52 de 204 jornadas con obra tienen empate—.

El comentario concuerda con cuántos lo comparten, con registros propios en plural.

#### Scenario: la obra del día se comparte en caso de empate
- **WHEN** varios dibujos empatan en categoría, simetría e intentos
- **THEN** el premio es de todos y se nombran todos
- **AND** la lista va ordenada por nombre, pero el nombre no decide
- **AND** el comentario va en plural

#### Scenario: con un solo ganador no cambia nada
- **WHEN** un dibujo gana sin empate
- **THEN** se nombra solo a esa persona, con el registro en singular

verified-by:
  - tests/slices/resumen-diario-compuesto/test_tendencia.py


## Requirement: El resumen dice de qué iba el hilo del día, no solo cuánto midió

<!-- origen: feat-tono-del-hilo (added) -->

Contar respuestas no distingue una ovación de un juicio. El mensaje ya sabía decir que alguien «armó el hilo
del día», y el día que un hilo se llenó de acusaciones lo publicó como un mérito. La mención del hilo lleva
por tanto **de qué iba la conversación**, y no solo su tamaño.

De qué iba lo decide una clasificación cerrada del hilo —el tono dominante, si hubo acusación, si hubo
defensa, si se propuso cambiar alguna regla, y cuánta temperatura tuvo—, no el recuento.

#### Scenario: la mención del hilo incorpora su tono
- GIVEN el hilo más comentado de la jornada, con su clasificación
- WHEN se compone el resumen
- THEN el texto refleja de qué iba la conversación además de cuántas respuestas tuvo

```yaml
checks:
  - type: regex
    file: tools/tono.py
    pattern: 'class Tono'
    describe: la clasificación es un objeto cerrado y sin campos de texto
```

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py

## Requirement: La frase que comenta el hilo sale del registro del repositorio

<!-- origen: feat-tono-del-hilo (added) -->

La frase publicada es **una de las del refranero**, elegida por la clasificación y por el número de jornada,
igual que el resto de la voz del mensaje. Ninguna palabra redactada por el modelo aparece en el canal.

La razón no es de estilo. En este canal la gente **ya le escribe al bot**, así que publicar prosa de un modelo
que acaba de leer el canal permitiría a cualquiera dictar lo que el bot dice sobre un compañero identificable
delante de todo el grupo. Con la frase saliendo del registro, una instrucción colada en el hilo como mucho
cambia una casilla del esquema, y la casilla no redacta.

Por lo mismo, del objeto que devuelve el modelo **solo se leen los campos del esquema**: cualquier campo
adicional se ignora en lugar de abrirse camino hasta el mensaje. Dos consecuencias que parecen detalles y no
lo son:

- **De quién es el hilo lo decide el repositorio, no el modelo.** Es el dato que determina a quién nombra el
  mensaje delante de todo el canal, así que no puede venir de fuera ni deducirse del recuento de respuestas
  —ese recuento incluye la charla, y respondiendo muchas veces a un mensaje intrascendente de otra persona se
  conseguía que el bot la señalara a ella por una conversación que no era la suya—.
- **Las cifras que se publican también tienen tope.** Cuántas personas dudan sale interpolado en la frase, así
  que una cifra sin límite serían dígitos publicados que no ha escrito el repositorio, y además empujaría el
  mensaje por encima de lo que Slack acepta.

**El registro es de cachondeo, no de sentencia.** Las frases se burlan como se burla el canal —amistosas y
con guasa— y **el bot no dictamina nada**: ni declara culpable a nadie, ni anuncia medidas, ni habla como un
juzgado. Las decisiones sobre el juego las toma el dueño cuando las pide; el mensaje de la tarde solo cuenta
lo que pasó y se ríe un rato. Hay un test que prohíbe el vocabulario judicial en el registro, porque la
primera versión derivó justo ahí.

#### Scenario: la frase publicada pertenece al registro
- GIVEN una clasificación del hilo
- WHEN se elige la frase que lo comenta
- THEN esa frase es una de las del registro del repositorio

#### Scenario: el texto que venga del modelo no se publica
- GIVEN una clasificación que trae además campos de texto libre
- WHEN se compone el resumen
- THEN ese texto no aparece en el mensaje

#### Scenario: la misma jornada da la misma frase
- GIVEN la misma clasificación y la misma jornada
- WHEN se compone el resumen dos veces
- THEN la frase del hilo es la misma

```yaml
checks:
  - type: regex
    file: tools/refranero.py
    pattern: 'TONO_DEL_HILO'
    describe: las frases del hilo viven en el registro del repositorio
```

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py

## Requirement: Sin clasificación válida, el resumen se publica sin esa frase

<!-- origen: feat-tono-del-hilo (added) -->

La clasificación es un adorno, no un requisito. Si la llamada falla, tarda de más, se queda sin cuota o
devuelve algo que no encaja en el esquema, el resumen sale con todo lo demás y sin la frase del hilo.

Es la misma regla que ya gobierna la lectura del canal: un servicio de fuera no puede impedir que el grupo vea
su marcador.

La credencial que se usa para preguntar tampoco puede escaparse por el camino: el destino se exige por TLS,
y una redirección **no se sigue**, porque al cambiar de host la cabecera de autorización viajaría con ella.
El plazo que se le da es **total y no por operación de red**: un servidor que gotee bytes no dispara el
tiempo de espera de un socket, y el marcador del día se publica después de esto.

#### Scenario: la clasificación no llega
- GIVEN que la clasificación del hilo no está disponible
- WHEN se compone el resumen
- THEN el mensaje se publica con el resto de sus menciones y sin la frase del hilo

#### Scenario: la clasificación no encaja en el esquema
- GIVEN una respuesta que no cumple el esquema esperado
- WHEN se interpreta
- THEN se descarta entera, en lugar de usar los campos que sí se entiendan

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py

## Requirement: Un hilo templado no se publica como juicio

<!-- origen: feat-tono-del-hilo (added) -->

La frase de tono solo sale cuando la clasificación llega a una temperatura mínima. Un hilo de felicitaciones,
o de tres respuestas sueltas, no se comenta: dramatizar una conversación que no lo fue es la forma más rápida
de que el mensaje deje de ser creíble.

#### Scenario: un hilo tranquilo no genera frase
- GIVEN una clasificación por debajo de la temperatura mínima
- WHEN se compone el resumen
- THEN no se publica frase de tono

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py

## Requirement: La sospecha se lanza a la mejor nota del día, y solo si nadie la comparte

<!-- origen: fix-sospecha-de-la-mejor-nota (modified) -->

La pulla de la sospecha salía para **cualquiera** que bajara de tres intentos, sin mirar qué había hecho el
resto. Eso produce dos mensajes que no se sostienen leídos por alguien del grupo:

- **Dudar de quien lo hizo peor.** Con un 1 en la mesa, quejarse de un 2 es poner en duda al segundo mientras
  se deja pasar al primero. Medido sobre 194 jornadas, esto había ocurrido **una sola vez**, porque una nota
  de 1 aparece en 3 jornadas de 194 — y ocurrió el día en que más se notaba.
- **Dudar de una coincidencia.** Cuando la mejor nota la firman varias personas, lo que dice el dato es que la
  palabra era fácil, no que nadie hiciera nada raro. Son 16 jornadas de 194.

La pulla va por tanto a quien firma la mejor nota del día, con dos intentos o menos, **y solo si la firma
solo**. El chiste sigue saliendo en una de cada cuatro jornadas (24%, antes 32%).

#### Scenario: con una nota mejor en la mesa, la sospecha no va al segundo
- GIVEN una jornada donde alguien resuelve en 1 y otras personas en 2
- WHEN se eligen los hechos comentables
- THEN la sospecha señala a quien resolvió en 1
- AND no se comenta la nota de quienes resolvieron en 2

#### Scenario: una mejor nota compartida no levanta sospecha
- GIVEN una jornada donde dos personas comparten la mejor nota, de dos intentos
- WHEN se eligen los hechos comentables
- THEN no se lanza la pulla de la sospecha a ninguna de las dos

#### Scenario: la mejor nota en solitario sigue teniendo su pulla
- GIVEN una jornada donde una sola persona firma la mejor nota, de dos intentos
- WHEN se eligen los hechos comentables
- THEN esa persona recibe la pulla de la sospecha

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py

## Requirement: El podio de cierre felicita en plural a quienes comparten el título

<!-- origen: fix-empate-en-cabeza (added) -->

Si el primer puesto del mes que cierra está compartido, el mensaje del podio felicita a todos los empatados con
una frase **escrita para varios**, que dice que comparten el primer puesto, elegida por jornada como las demás.
Nunca usa una frase escrita para un campeón solo: «Cata y Joel se lleva el mes» es un error de concordancia
delante de todo el grupo. Con un único campeón, el mensaje no cambia.

#### Scenario: dos campeones, frase en plural
- GIVEN un mes cerrado con dos jugadores empatados en el primer puesto
- WHEN se compone el podio
- THEN la felicitación nombra a los dos y dice que comparten el primer puesto, para cualquier jornada

#### Scenario: un campeón, frase de siempre
- GIVEN un mes cerrado con un único primero
- WHEN se compone el podio
- THEN la felicitación es una de las frases de campeón único

verified-by:
  - tests/slices/podio-de-cierre-de-mes/test_podio.py

## Requirement: El resumen sabe en qué momento del mes está

<!-- origen: feat-resumen-con-podios (added) -->

El resumen se sitúa en el mes con **la fecha de la jornada y el calendario**, sin leer el reloj (§10):

- **Arranque** — la jornada es una de las tres primeras que cuentan en la temporada: justo antes de los podios
  va una línea de arranque de mes, sin hablar de ventajas.
- **Mitad** — ni arranque ni recta final: no hay bloque de tensión; el resumen es el de siempre.
- **Recta final** — quedan cuatro días laborables o menos en el mes después de la jornada: justo antes de los
  podios va el bloque de recta final, con cuántas jornadas quedan, quién manda y a qué distancia —en media
  publicada— está el segundo, y que un empate a final de mes **comparte el primer puesto**. Si hay
  clasificación del juego, dice cuántos puntos quedan en juego —10 por cada nivel del mes que queda por
  cerrar: el que está abierto, si es del mes, y uno por cada laborable desde la jornada del resumen— y si el
  segundo todavía puede alcanzar al primero.
- **Última jornada** — el último día laborable del mes: el bloque de recta final lo anuncia como la última
  jornada.

Los festivos no se conocen: cuentan como laborables, así que en un mes con festivo al final la recta final
puede anunciar una jornada de más.

#### Scenario: el mes arranca
- GIVEN la segunda jornada que cuenta en la temporada
- WHEN se compone el resumen
- THEN antes de los podios hay una línea de arranque de mes y no hay bloque de recta final

#### Scenario: la recta final cuenta lo que queda
- GIVEN una jornada con tres días laborables por delante en el mes y los dos primeros a 0,05 de media
- WHEN se compone el resumen
- THEN el bloque de recta final dice que quedan 3 jornadas, nombra al primero y al segundo, dice la distancia
  y que un empate comparte el primer puesto

#### Scenario: la recta final dice si el juego sigue abierto
- GIVEN el primero del juego con 12 puntos más que el segundo y dos niveles por cerrar en el mes
- WHEN sale el bloque de recta final
- THEN dice que quedan 20 puntos en juego y que el segundo todavía puede alcanzarle

#### Scenario: con el juego decidido se dice
- GIVEN el primero del juego con 32 puntos más que el segundo y dos niveles por cerrar en el mes
- WHEN sale el bloque de recta final
- THEN dice que el segundo ya no puede alcanzarle

#### Scenario: la última jornada se anuncia
- GIVEN la jornada del último laborable del mes
- WHEN se compone el resumen
- THEN el bloque lo anuncia como la última jornada, sin «quedan 0»

#### Scenario: a mitad de mes no hay tensión
- GIVEN una jornada que no está entre las tres primeras ni en la recta final
- WHEN se compone el resumen
- THEN no hay línea de arranque ni bloque de recta final

#### Scenario: el momento del mes no depende del reloj
- GIVEN la misma jornada compuesta con el reloj del sistema en dos fechas distintas
- WHEN se compone el resumen
- THEN el bloque del momento del mes es el mismo

```yaml
checks:
  - type: regex
    file: tools/resumen.py
    pattern: 'bloque_momento_del_mes\(resultados, temporada, jornada, niveles or \(\), marcas or \(\)\),\s+bloque_top\('
    describe: el momento del mes va justo antes de los podios
```

verified-by:
  - tests/slices/resumen-diario-compuesto/test_momento_del_mes.py

## Requirement: Lo que publica el bot se escapa para Slack

<!-- origen: feat-resumen-con-podios (added) -->

Los nombres de jugador son los nombres de perfil de Slack, que cualquier miembro puede cambiar. Antes de
publicar, **todo el texto** que sube el bot —el resumen diario y el podio de cierre de mes— se escapa como pide
la API de Slack: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`. Así `<!channel>`, `<@U…>` o `<https://…|texto>` en un
nombre salen como texto y no avisan a nadie ni crean enlaces. Ningún texto del bot usa esos caracteres a
propósito, así que el escapado no cambia nada más del mensaje.

Si falla la lectura del juego, el log del workflow —público, como el repositorio— dice el tipo de error y no el
error completo.

#### Scenario: un nombre con una mención especial no avisa a nadie
- GIVEN un jugador llamado `<!channel>` en el podio del marcador
- WHEN el bot sube el mensaje
- THEN el texto enviado a Slack lleva `&lt;!channel&gt;` y no `<!channel>`

#### Scenario: el resto del mensaje no cambia
- GIVEN un mensaje sin caracteres especiales
- WHEN se escapa
- THEN sale idéntico

```yaml
checks:
  - type: regex
    file: tools/post_ranking.py
    pattern: 'initial_comment=para_slack\(texto\)'
    describe: "todo lo que sube el bot pasa por el escapado"
```

verified-by:
  - tests/slices/resumen-diario-compuesto/test_podios.py

## Requirement: La noche del último día laborable se publica la victoria en lugar del resumen

<!-- origen: feat-victoria-el-ultimo-dia (added) -->

Cuando la jornada que resume el bot es la del **último día laborable del mes** (calendario, no reloj: el mismo
día que la recta final anuncia como «última jornada»), el job del resumen diario no publica el resumen: publica
el **mensaje de la victoria** del mes —el que hasta ahora salía el día 1 a las 11:00— con el título del podio del
mes («Podio del mes 🏆 · AAAA-MM»). Debajo del podio y de la felicitación va, en corto, la última jornada: la
palabra, el mejor del día y la obra del día.

El cron del día 1 sigue como red: busca ese título en el canal y, si ya está, no repite; si esa noche no se
publicó, lo publica él. Y las reintentonas del resumen esa misma noche también buscan el título del podio, así
que la victoria no sale dos veces.

Se calcula con lo que hay esa noche: una cuadrícula del último día que llegue después de que se publique no
entra en el podio (medido en 60 días: 2 de 490 llegaron después de medianoche).

#### Scenario: el último laborable sale la victoria
- GIVEN la jornada del último día laborable del mes
- WHEN corre el job del resumen
- THEN publica un mensaje con el título del podio del mes, el podio, la felicitación y la última jornada, y no el
  resumen diario

#### Scenario: no se repite
- GIVEN la victoria del mes ya publicada en el canal
- WHEN vuelve a correr el job del resumen esa noche, o el cron del día 1
- THEN no publican nada

#### Scenario: un día cualquiera sigue saliendo el resumen
- GIVEN una jornada que no es el último día laborable del mes
- WHEN corre el job del resumen
- THEN publica el resumen diario de siempre

```yaml
checks:
  - type: regex
    file: tools/post_ranking.py
    pattern: 'if temporada != TEMPORADA_CERO and es_ultimo_laborable_del_mes\(fecha\):'
    describe: "el último laborable el job del resumen publica la victoria"
  - type: regex
    file: tools/post_ranking.py
    pattern: 'if ya_celebrado\(leer_mensajes\(paginas=PAGINAS_DE_HISTORIA\), temporada\):'
    describe: "la victoria no se repite"
```

verified-by:
  - tests/slices/podio-de-cierre-de-mes/test_victoria.py

## Requirement: Desde octubre la victoria corona a los tres campeones

<!-- origen: feat-victoria-el-ultimo-dia (added) -->

Si la temporada que cierra es de octubre de 2026 en adelante, el mensaje de la victoria dibuja, además del
podio del marcador, **el podio del SuperWordleBros y el de figuras** —el mismo podio ASCII del resumen diario,
en ese orden— y corona a sus campeones: el del juego por puntos y el de figuras por puntos por partida. Los empates se
comparten en una frase en plural; una competición sin nadie clasificado no corona a nadie. Antes de octubre, el
mensaje no cambia.

#### Scenario: octubre corona a los tres
- GIVEN una temporada 2026-10 cerrada con campeón en las tres competiciones
- WHEN se compone la victoria
- THEN hay tres podios —marcador, SuperWordleBros y figuras— y una línea que corona al campeón de cada uno

#### Scenario: septiembre corona solo el marcador
- GIVEN la temporada 2026-09 con juego y figuras
- WHEN se compone la victoria
- THEN no hay líneas del SuperWordleBros ni de figuras

```yaml
checks:
  - type: regex
    file: tools/podio.py
    pattern: 'DESDE_TRES_COMPETICIONES = "2026-10"'
    describe: "los tres campeones desde octubre"
```

verified-by:
  - tests/slices/podio-de-cierre-de-mes/test_victoria.py

## Requirement: El podio de cierre se dibuja como el del resumen diario

<!-- origen: fix-podio-ascii-del-cierre (added) -->

El mensaje de cierre de mes dibuja el podio con el **mismo podio ASCII de bloques macizos** que el resumen
diario (`tools/podios.py::podio_de_texto`), dentro de un bloque de código y bajo «🏆 *Así queda el podio ·
Temporada N*». Los puestos son los de la clasificación: con el primer puesto compartido, **todos los campeones
van juntos en el escalón central, el más alto**. Sustituye a la lista con medallas, que ponía al segundo
campeón debajo con un «·», como si fuera menos.

#### Scenario: dos campeones, juntos arriba
- GIVEN un mes cerrado con dos jugadores empatados en el primer puesto
- WHEN se compone el podio de cierre
- THEN los dos van en la columna central, encima del escalón más alto, y no hay lista de medallas

```yaml
checks:
  - type: regex
    file: tools/podio.py
    pattern: 'podio_de_texto\(\s*f"🏆 \*Así queda el podio · Temporada'
    describe: "el podio de cierre usa el podio ASCII del resumen"
```

verified-by:
  - tests/slices/podio-de-cierre-de-mes/test_podio.py

## Requirement: El resumen cuenta la participación cuando es noticia

<!-- origen: feat-participacion-y-album-al-arrancar (added) -->

Tras la jornada, el resumen dice cuántos han jugado si la jornada bate el récord del canal, trae
`DEBUTANTES_NOTICIA` o más debutantes, o junta `AFLUENCIA_NOTICIA` veces la mediana de las últimas
`JORNADAS_DE_REFERENCIA` jornadas de temporada. Da la bienvenida a los debutantes por su nombre —como mucho
`NOMBRES_DE_BIENVENIDA`, el resto resumido— y cierra con una coletilla pop que rota por jornada. Un día
normal, o sin jornadas anteriores, no sale.

#### Scenario: un récord con debutantes se cuenta
- GIVEN una jornada con más jugadores que ninguna anterior y cinco debutantes
- WHEN se compone el resumen
- THEN dice cuántos son, que es récord, cuánto es lo normal, nombra a tres y resume a dos

#### Scenario: un día normal no lo menciona
- GIVEN una jornada con la gente de siempre
- WHEN se compone el resumen
- THEN no hay bloque de participación

verified-by:
  - tests/slices/resumen-diario-compuesto/test_participacion.py

## Requirement: El juego y las figuras van en lista; el podio ASCII es del marcador

<!-- origen: feat-participacion-y-album-al-arrancar (modified) -->

En el resumen diario, los tres primeros del SuperWordleBros del mes y del álbum de figuras van en una lista,
una línea por puesto («1º Ana · 18 pts»), con los empatados en la misma línea y como mucho tres nombres por
puesto. Solo el marcador general lleva el podio dibujado: es el protagonista (decisión del dueño, 2026-10-02).
El mensaje de la victoria del mes no cambia con este requisito.

#### Scenario: el juego y las figuras no llevan dibujo
- GIVEN un resumen con marcador, juego y figuras
- WHEN se compone
- THEN solo hay un bloque de código, el del marcador, y el juego y las figuras van en lista

#### Scenario: la frase de varios concuerda en plural
- GIVEN dos jugadores que comparten el hecho del día
- WHEN se escribe su comentario
- THEN el verbo va en plural para todas las claves de frases

verified-by:
  - tests/slices/resumen-diario-compuesto/test_podios.py
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py

## Requirement: El cierre de mes se intenta los tres primeros días

<!-- origen: fix-podio-historial-por-fecha (added) -->

#### Scenario: el cierre se intenta los tres primeros días
- **WHEN** se programa la publicación del cierre de mes
- **THEN** el cron corre los días 1, 2 y 3 del mes; si GitHub se salta uno, se publica al siguiente

verified-by:
  - tests/slices/podio-de-cierre-de-mes/test_podio.py
  - tests/slices/podio-de-cierre-de-mes/test_victoria.py
