# Spec de `ingesta`

Spec **viva** del dominio `ingesta` (ver `openspec/README.md`). Se edita directamente en la rama de cada cambio,
junto al código y los tests que la cumplen ([ADR 0009](../../decisions/0009-specs-vivas.md)). Cada Requirement
lleva en un comentario los change packs de los que sale, archivados en `openspec/changes/archive/`.

## Requirement: El recorrido del histórico agota todas las páginas

<!-- origen: feat-backfill-de-patrones (added) -->

La lectura del canal para recuperar patrones antiguos continúa mientras la respuesta indique que queda
histórico. No se detiene en la primera página: el histórico completo son más de mil quinientos
resultados y una página devuelve como máximo unos cientos de mensajes.

```yaml
checks:
  - type: slack-api
    method: conversations.history
    describe: el recorrido sigue el cursor de paginación hasta agotarlo
```

#### Scenario: el histórico ocupa varias páginas
- GIVEN un histórico que la API devuelve en tres páginas
- WHEN el comando recorre el canal
- THEN procesa los mensajes de las tres páginas

#### Scenario: sin más histórico el recorrido termina
- GIVEN una respuesta sin cursor de continuación
- WHEN el comando la recibe
- THEN termina el recorrido sin pedir más páginas

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py

## Requirement: La extracción del patrón antiguo usa las mismas reglas que la ingesta

<!-- origen: feat-backfill-de-patrones (added) -->

El patrón que se recupera del histórico es idéntico al que la ingesta habría producido con ese mismo
mensaje: mismas celdas reconocidas, misma normalización del tema claro y oscuro, mismo formato de
filas. No hay una segunda implementación de la extracción.

#### Scenario: un mensaje antiguo produce el mismo patrón que produciría hoy
- GIVEN un mensaje del histórico con su cuadrícula
- WHEN el backfill extrae su patrón
- THEN el resultado es igual al que produce la extracción de la ingesta para ese texto

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py

## Requirement: El backfill no registra resultados

<!-- origen: feat-backfill-de-patrones (added) -->

El recorrido puede encontrar resultados publicados en el canal que nunca llegaron a la tabla. El
comando **no los inserta**: informa de cuántos ha visto y sigue. Recuperar resultados perdidos es un
comportamiento distinto, con sus propias causas (mensajes en hilos, ventana de ingesta corta) y su
propio slice.

#### Scenario: un resultado del canal que no está en la tabla
- GIVEN un mensaje de resultado sin fila correspondiente
- WHEN el comando lo procesa
- THEN no se crea ninguna fila y el mensaje consta en el recuento de resultados sin registrar

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py

## Requirement: La cuadrícula del mensaje se extrae como patrón

<!-- origen: feat-captura-del-patron (added) -->

Al procesar un mensaje de resultado, la ingesta extrae las filas de cuadrícula que lo acompañan. Una
fila de cuadrícula es una línea con **exactamente cinco** celdas de cuadrado y ninguna otra cosa; las
líneas que no cumplen eso no forman parte del patrón.

Las celdas se reconocen por su nombre en el mensaje del canal: verde y amarillo tienen un nombre cada
uno, y la celda de letra ausente tiene **dos** nombres posibles según el tema de quien publica. Los dos
se normalizan al mismo símbolo.

```yaml
checks:
  # Le faltaban `file:` y `pattern:`, así que el probe no podía decidir: lo cazó `checks-probe`.
  - type: regex
    file: tools/patterns.py
    pattern: 'CELDA_RE = re\.compile'
    describe: la fila de cuadrícula exige cinco celdas exactas
```

#### Scenario: se extraen todas las filas del mensaje
- GIVEN un mensaje de resultado con cinco filas de cuadrícula
- WHEN la ingesta lo procesa
- THEN el patrón resultante tiene cinco filas

#### Scenario: una línea con cuatro celdas no es una fila
- GIVEN un mensaje cuya cuadrícula incluye una línea con cuatro celdas
- WHEN la ingesta lo procesa
- THEN esa línea no aparece en el patrón

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py

## Requirement: El patrón pertenece al resultado que lo precede

<!-- origen: feat-captura-del-patron (added) -->

Las filas de cuadrícula llegan al parser como líneas independientes, después de la línea que declara el
resultado. Cada bloque de filas se asocia al último resultado reconocido; un resultado nuevo cierra el
bloque anterior.

#### Scenario: dos resultados seguidos no mezclan sus cuadrículas
- GIVEN dos mensajes de resultado consecutivos, cada uno con su cuadrícula
- WHEN la ingesta los procesa
- THEN cada fila queda con el patrón de su propio mensaje

#### Scenario: los emojis de una conversación no producen patrón
- GIVEN un mensaje de conversación con celdas de cuadrado y ningún resultado previo en el lote
- WHEN la ingesta lo procesa
- THEN no se almacena ningún patrón

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py

## Requirement: La ausencia de cuadrícula no impide registrar el resultado

<!-- origen: feat-captura-del-patron (added) -->

El patrón es información añadida. Si un mensaje de resultado no trae cuadrícula, o sus líneas no son
reconocibles, el resultado se registra igual con su puntuación y su fecha.

#### Scenario: resultado sin cuadrícula
- GIVEN un mensaje que solo contiene la línea del resultado
- WHEN la ingesta lo procesa
- THEN el resultado queda registrado y sin patrón

#### Scenario: un fallo también conserva su patrón
- GIVEN un resultado de fallo, cuya cuadrícula no termina en una fila de aciertos
- WHEN la ingesta lo procesa
- THEN el patrón se almacena con todas las filas del mensaje

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py

## Requirement: La ingesta transporta el identificador del autor, no su nombre

<!-- origen: feat-ingesta-por-id (added) -->

La línea que el extractor pasa al cargador lleva **el identificador de Slack del autor** y, aparte, su
nombre visible. El identificador es lo que identifica; el nombre es solo para mostrar.

Los dos scripts se ejecutan encadenados en la misma invocación, así que el formato de la línea es un
contrato interno y cambia de golpe: no hace falta ventana de compatibilidad.

```yaml
checks:
  - type: cli-command
    describe: extract_slack.py emite el identificador del autor en la línea de encabezado
```

#### Scenario: el encabezado lleva identificador y nombre
- GIVEN un mensaje de resultado de una persona del workspace
- WHEN el extractor lo emite
- THEN la línea contiene su identificador de Slack y su nombre visible, en campos distintos

#### Scenario: la cuadrícula se sigue asociando a su resultado
- GIVEN un mensaje con su resultado y las filas de emojis
- WHEN se procesa el lote con el formato nuevo
- THEN el patrón capturado es el mismo que con el formato anterior

#### Scenario: un mensaje sin autor no se guarda
- GIVEN una línea de resultado sin autor
- WHEN se procesa el lote
- THEN no se escribe ninguna fila para ese resultado y el recuento lo declara

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py

## Requirement: El backfill empareja mensaje y fila por identificador

<!-- origen: fix-backfill-por-identificador (modified) -->

La correspondencia entre un mensaje del canal y su fila se establece por **número de puzzle e identificador
del autor**. El nombre mostrado no participa: cambia con el tiempo, y la columna de identidad guarda
identificadores desde la canonización.

Emparejar por nombre no es una alternativa peor, es una que **no funciona**: medido tras la canonización,
resolvía 0 de 299 filas.

#### Scenario: el autor de un mensaje es su identificador
- GIVEN un mensaje del canal con su autor
- WHEN se convierte en entrada del recorrido
- THEN su autor es el identificador de Slack, no el nombre que mostraba

#### Scenario: un mensaje sin autor no entra en el recorrido
- GIVEN un mensaje de sistema o sin autor
- WHEN se convierte en entrada
- THEN se descarta

#### Scenario: la fila se localiza por puzzle e identificador
- GIVEN una tabla con filas de varios jugadores y puzzles
- WHEN se busca la fila de un puzzle y un identificador
- THEN se devuelve la de ese jugador y ese puzzle, y ninguna otra

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py

## Requirement: La ventana de ingesta se mide en días y se pagina

<!-- origen: feat-ventana-de-ingesta (modified) -->

La ejecución horaria lee **todos los mensajes del canal desde una fecha de corte**, paginando hasta
alcanzarla. La ventana no se expresa en número de mensajes.

Medido sobre el histórico: mediana de 10 mensajes al día, máximo 27. Una ventana de 50 mensajes cubre cinco
días **de media** y **no cubre tres** en la peor racha, que son 52 mensajes. Contar mensajes hace que la
cobertura dependa de lo hablador que esté el grupo — un día de charla desplaza los resultados de días
anteriores— que es lo contrario de lo que se le pide a una red de seguridad.

Reingerir lo ya guardado no duplica, porque el upsert va por `(slack_user_id, wordle_id)`. Ese es el hecho
que hace barata una ventana ancha: el único coste son un par de páginas más de API.

#### Scenario: la ventana es una fecha de corte
- GIVEN mensajes de hace un día, de hace casi la ventana entera y de hace un mes
- WHEN se lee el canal
- THEN entran los dos primeros y no el tercero

#### Scenario: un día hablador no desplaza a los días anteriores
- GIVEN sesenta mensajes de charla de hoy y un resultado de hace cuatro días
- WHEN se lee el canal
- THEN el resultado de hace cuatro días entra igualmente

#### Scenario: la ventana pagina hasta el corte
- GIVEN más mensajes en la ventana de los que caben en una página
- WHEN se lee el canal
- THEN se piden las páginas necesarias y llegan todos, en orden cronológico

#### Scenario: la fecha de corte entra por parámetro
- GIVEN una fecha actual concreta
- WHEN se calcula el corte
- THEN sale de esa fecha y no del reloj del sistema

#### Scenario: un fallo a mitad de la paginación aborta
- GIVEN que la segunda página falla
- WHEN se lee el canal
- THEN la ejecución falla en lugar de emitir los mensajes que sí llegaron

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py

## Requirement: El canal se lee al publicar, y de él solo salen números

<!-- origen: feat-voz-de-la-jornada (added) -->

La publicación de la tarde lee los mensajes del día en el canal con `conversations.history`, la misma llamada
y el mismo token que ya usa la ingesta horaria. **No hace falta ningún permiso nuevo.**

De esa lectura se derivan **señales**, y nada más: a qué hora publicó cada jugador su resultado, cuántas
reacciones recibió cada mensaje, cuántas respuestas tiene cada hilo y quién no publicó nada. **El texto de los
mensajes no sale de la función que los lee.** El repositorio es público y el canal contiene conversaciones de
compañeros identificables, así que la restricción no se cumple a medias: si la señal se puede expresar con un
número, viaja como número.

Las señales **no se persisten**. Viven lo que dura la ejecución del cron y se descartan al publicar. Dos
razones, y la segunda es de corrección y no de comodidad: no hace falta esquema nuevo para datos de
comportamiento de personas identificables, y **las reacciones son un dato vivo** — guardarlas en la ingesta
horaria las congelaría a media mañana, mientras que leerlas a las 17:00 cuenta el día completo.

Se ignoran los mensajes del **propio bot**: publica todas las tardes y sería siempre el más aplaudido de su
propio resumen. Y se distingue un mensaje **con resultado** de la charla: solo los primeros dan hora de
publicación, porque contar un «jajaja» como resultado falsearía tanto la hora como la ausencia.

La lectura es **best-effort**: si falla o devuelve vacío, el resumen se publica con lo que sale de la tabla.
Un canal caído no puede impedir que el marcador se publique.

```yaml
checks:
  - type: slack-api
    method: conversations.history
    note: la misma llamada de la ingesta horaria; sin scopes nuevos
```

#### Scenario: la hora de publicación es la del canal
- GIVEN un mensaje de resultado publicado a una hora concreta
- WHEN se derivan las señales del día
- THEN la hora que se usa es la del mensaje, no la del registro de la fila

#### Scenario: del canal no sale texto
- GIVEN un día con mensajes de resultado y con charla
- WHEN se derivan las señales
- THEN lo que se devuelve son horas y recuentos, y ningún contenido de mensaje

#### Scenario: el bot no compite en su propio resumen
- GIVEN que el bot publicó su mensaje de la tarde anterior con reacciones
- WHEN se busca el mensaje más aplaudido del día
- THEN el del bot no se considera

#### Scenario: la charla no da hora de publicación
- GIVEN alguien que escribió en el canal pero no publicó resultado
- WHEN se derivan las señales
- THEN no consta como que haya publicado a esa hora

#### Scenario: un canal que no responde no tumba el resumen
- GIVEN que la lectura del canal falla
- WHEN se compone el resumen
- THEN se publica con lo que sale de la tabla, sin las menciones que dependen del canal

verified-by:
  - tests/slices/voz-de-la-jornada/test_senales.py

## Requirement: El hilo de la jornada se lee entero, y sale del borde sin nombres

<!-- origen: feat-tono-del-hilo (added) -->

Hasta ahora del canal se leían las cabeceras: quién publicó, cuándo, cuántas reacciones y cuántas respuestas
colgaban. Para saber de qué iba una conversación hay que leerla, así que el hilo del resultado más comentado
de la jornada se pide entero.

Lo que se manda fuera va **anonimizado, contenido incluido**: cada persona aparece con un rol —quien abrió
el hilo, y el resto como participantes numerados— y del texto se retiran las marcas de Slack, que traen
identificadores en crudo, y los nombres del grupo, que la gente escribe a mano. El nombre lo reinserta el
repositorio al componer el mensaje, que ya lo sabe.

Anonimizar **solo la etiqueta de quien habla no anonimiza nada**, y se comprobó: en cuanto alguien menciona a
un compañero —lo normal en un hilo— su identificador sale tal cual dentro del texto.

Y un participante no puede fabricar participantes: los saltos de línea de una respuesta se colapsan, porque
si no una sola persona escribe «participante 7: …» dentro de su propio mensaje y el modelo cuenta dos
personas donde hay una.

Tapar un nombre es sustituir **la palabra**, no la subcadena: con una «Ana» o una «Cata» en la liga,
sustituir por subcadena convertía «mañana» en «mañalguien» y el texto que decide si se publica un reproche
llegaba ilegible.

Se excluye lo que escribe quien abrió el hilo: la conversación que interesa es la del grupo sobre su jugada,
no su defensa.

#### Scenario: la transcripción no lleva nombres
- GIVEN el hilo de un jugador con respuestas de otros
- WHEN se prepara la transcripción para clasificarla
- THEN ningún nombre de jugador ni identificador de Slack aparece en ella

#### Scenario: quien abrió el hilo no cuenta como participante
- GIVEN un hilo donde su autor también responde
- WHEN se prepara la transcripción
- THEN sus propias respuestas no se cuentan como conversación del grupo

```yaml
checks:
  - type: regex
    file: tools/tono.py
    pattern: 'def transcripcion'
    describe: la transcripción que sale del borde se arma aquí, sin nombres
```

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py

## Requirement: Solo se lee el hilo de la jornada que se publica

<!-- origen: feat-tono-del-hilo (added) -->

La ventana que se pide al canal son treinta días, porque las aperturas se cuentan sobre el histórico. La
clasificación, en cambio, mira **un solo hilo**: el de la jornada que se está publicando.

Sin ese recorte se repetiría el defecto que ya tuvo la mención del hilo antes de acotarla: el mensaje acabó
presentando como «el hilo del día» una conversación de tres semanas atrás.

#### Scenario: los hilos de otros días no se clasifican
- GIVEN una ventana del canal con hilos de jornadas anteriores
- WHEN se elige el hilo a clasificar
- THEN se elige el de la jornada que se publica

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py

## Requirement: Un autor que no está en el directorio se nombra por su perfil

<!-- origen: fix-nombre-de-autores-externos (added) -->

El extractor completa el directorio de `users.list` con los autores de la ventana que no aparecen en él
—los usuarios externos de Slack Connect—: su nombre sale del `user_profile` del mensaje y, si no viene, de
`users.info`, una consulta por autor y ejecución. Solo si Slack no da nombre se emite el identificador.

#### Scenario: un autor externo se nombra por su perfil
- GIVEN un resultado de alguien que no está en `users.list`, con su perfil en el mensaje
- WHEN se extrae la ventana
- THEN la línea lleva el nombre de su perfil y no su identificador

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py
