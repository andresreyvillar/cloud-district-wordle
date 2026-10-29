# Spec de `resultados`

Spec **viva** del dominio `resultados` (ver `openspec/README.md`). Se edita directamente en la rama de cada cambio,
junto al código y los tests que la cumplen ([ADR 0009](../../decisions/0009-specs-vivas.md)). Cada Requirement
lleva en un comentario los change packs de los que sale, archivados en `openspec/changes/archive/`.

## Requirement: El relleno de patrones solo escribe donde falta

<!-- origen: feat-backfill-de-patrones (added) -->

Una operación de relleno escribe `pattern` únicamente en las filas que lo tienen vacío. Las filas con
patrón quedan intactas, de modo que la operación es idempotente: ejecutarla dos veces produce el mismo
estado que ejecutarla una.

```yaml
checks:
  - type: column
    table: wordle_results
    column: pattern
```

#### Scenario: una fila con patrón no se modifica
- GIVEN una fila cuyo `pattern` ya tiene contenido
- WHEN se ejecuta el relleno
- THEN el valor de `pattern` de esa fila es el mismo antes y después

#### Scenario: dos ejecuciones seguidas dejan el mismo estado
- GIVEN un conjunto de filas parcialmente rellenado
- WHEN el relleno se ejecuta dos veces
- THEN el estado de la tabla tras la segunda ejecución es idéntico al de la primera

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py

## Requirement: El relleno no altera el censo de resultados

<!-- origen: feat-backfill-de-patrones (added) -->

Una operación de relleno de patrones no crea ni elimina filas, y no modifica ninguna columna que no sea
`pattern`. El número de resultados por jugador y por puzzle es idéntico antes y después.

#### Scenario: el número de filas no cambia
- GIVEN la tabla con N filas
- WHEN se ejecuta el relleno completo
- THEN la tabla sigue teniendo N filas

#### Scenario: la puntuación y la fecha no se tocan
- GIVEN una fila con su puntuación y su fecha
- WHEN el relleno escribe su patrón
- THEN la puntuación y la fecha conservan el valor que tenían

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py

## Requirement: Las filas sin mensaje localizable quedan declaradas

<!-- origen: feat-backfill-de-patrones (added) -->

Cuando una fila sin patrón no tiene mensaje correspondiente en el histórico del canal, la fila
permanece sin patrón y la operación la cuenta como no resuelta. El recuento final distingue tres
cantidades: filas rellenadas, filas intactas y filas no resueltas.

#### Scenario: fila sin mensaje en el canal
- GIVEN una fila sin patrón cuyo mensaje no aparece en el histórico
- WHEN termina el relleno
- THEN la fila sigue sin patrón y aparece en el recuento de no resueltas

verified-by:
  - tests/slices/backfill-de-patrones/test_backfill_de_patrones.py

## Requirement: La tabla almacena el patrón de la cuadrícula

<!-- origen: feat-captura-del-patron (added) -->

`wordle_results` tiene una columna `pattern` de texto, opcional. Contiene el camino de emojis del
resultado; vacía cuando el mensaje no traía cuadrícula o cuando la fila es anterior al backfill.

La columna es **aditiva**: no altera ni sustituye a `player_name`, `wordle_id`, `score`, `date` ni
`raw_text`, que son las que lee la v1 de la web
([ADR 0005](../../../../decisions/0005-hosting-y-convivencia-v1-v2.md)).

```yaml
checks:
  - type: column
    table: wordle_results
    column: pattern
    nullable: true
```

#### Scenario: una fila sin cuadrícula sigue siendo válida
- GIVEN un resultado cuyo mensaje no incluye cuadrícula
- WHEN se registra en la tabla
- THEN la fila existe con su puntuación y su fecha, y `pattern` queda vacía

#### Scenario: la v1 sigue funcionando con la columna nueva
- GIVEN la columna `pattern` añadida a la tabla
- WHEN la web v1 consulta los resultados
- THEN recibe las columnas que ya leía y funciona sin cambios

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py

## Requirement: El patrón se almacena en forma normalizada y reversible

<!-- origen: feat-captura-del-patron (added) -->

El patrón se guarda como una cadena de filas separadas por `/`, cada fila con exactamente cinco
caracteres: `G` acierto en posición, `Y` letra presente en otra posición, `.` letra ausente.

Ejemplo: un resultado en tres intentos se almacena como `...YY/.G.YY/GGGGG`.

El formato es **reversible**: a partir de la cadena se reconstruye la cuadrícula tal como se publicó,
salvo el tema claro u oscuro de quien la publicó, que es información de presentación y no de juego.
Guardar el patrón y no una categoría ya calculada es deliberado: el clasificador de figuras se
recalibrará, y un veredicto persistido haría irrecuperable el histórico en cada ajuste.

```yaml
checks:
  # Era un `config-key` sin `file:`, así que no verificaba nada — lo cazó el gate `checks-probe` el
  # 2026-08-07. Y el tipo era el equivocado: no es una clave de configuración, es una constante de Python.
  - type: regex
    file: tools/patterns.py
    pattern: '^PATTERN_ROW_SEPARATOR = "/"$'
    describe: el separador de filas del patrón es la barra
```

#### Scenario: el patrón conserva el orden de los intentos
- GIVEN una cuadrícula de cuatro filas
- WHEN se almacena el patrón
- THEN la cadena tiene cuatro grupos separados por `/` en el mismo orden que el mensaje

#### Scenario: dos caminos idénticos con temas distintos producen el mismo patrón
- GIVEN dos resultados con el mismo camino, uno publicado en tema claro y otro en tema oscuro
- WHEN se almacenan
- THEN las dos cadenas son idénticas

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py

## Requirement: El patrón no participa en la identidad de la fila

<!-- origen: feat-captura-del-patron (added) -->

La unicidad de un resultado sigue siendo la pareja jugador–puzzle. El patrón es un atributo: cambiarlo
no crea una fila nueva, y una reejecución de la ingesta sobre el mismo mensaje deja una sola fila con un
solo patrón.

La unicidad la garantiza un **índice único**, no una constraint — verificado contra el esquema:
`idx_slack_user_wordle_unique` sobre `(slack_user_id, wordle_id)`. Es lo que hace funcionar el
`on_conflict` del upsert. La clave primaria es `id` (uuid).

El **doble que imita ese índice** no vive aquí: los tests de este slice solo parsean patrones y no escriben
en ninguna tabla. Vive en los slices que escriben —`ingesta-por-id-de-slack` e
`identidad-canonica-de-jugador`—, y ahí es donde el `checks:` de tipo `index` está declarado. Lo que este
slice puede demostrar por su cuenta es que el upsert usa esa pareja como clave de conflicto, y eso es lo que
declara:

```yaml
# Antes había aquí un `checks: - type: index`, y el gate `checks-probe` lo tumbó el 2026-08-07 con razón:
# reclamaba un doble que impusiera el índice en un tests_root donde no se escribe nada. La invariante es
# cierta, pero este slice no es quien la demuestra.
checks:
  - type: regex
    file: tools/add_results.py
    pattern: '^CLAVE_DE_CONFLICTO = \("slack_user_id", "wordle_id"\)$'
    describe: el upsert usa la pareja jugador-puzzle como clave de conflicto
```

**Límite conocido de esa unicidad:** `slack_user_id` es nullable, y en Postgres dos `NULL` no colisionan
en un índice único. Dos filas con `slack_user_id` nulo y el mismo puzzle no violarían el índice. Hoy no
hay ninguna fila con ese valor nulo (verificado: 0 de 1532), así que el riesgo es teórico; deja de serlo
el día que la resolución de identidad devuelva nulo en lugar de un nombre.

#### Scenario: reprocesar un mensaje no duplica la fila
- GIVEN un resultado ya registrado con su patrón
- WHEN la ingesta procesa el mismo mensaje otra vez
- THEN sigue existiendo una sola fila para ese jugador y ese puzzle

verified-by:
  - tests/slices/captura-del-patron/test_captura_del_patron.py


## Requirement: El censo de partidas solo baja por fusión

<!-- origen: feat-identidad-canonica (added) -->

Una canonización de identidad puede reducir el número de filas, y **solo** por un motivo, que se informa
con su cantidad: **la fusión de dos filas que son la misma partida**. Una fusión exige que las dos filas
coincidan en jugador resuelto, puzzle y puntuación; con puntuación distinta no se fusiona, se declara
conflictiva y se deja intacta.

Nada se elimina por ningún otro motivo. En particular, una atribución cruzada **no** se elimina: se
reatribuye (ver el Requirement siguiente), y solo desaparece si al reatribuirse resulta ser una partida ya
registrada — es decir, por fusión.

Cualquier otra variación del censo es un fallo. La suma es verificable:
`filas_después = filas_antes − fusionadas`.

```yaml
checks:
  - type: index
    table: wordle_results
    name: idx_slack_user_wordle_unique
    kind: unique
    columns: [slack_user_id, wordle_id]
```

#### Scenario: el censo cuadra con lo declarado
- GIVEN una tabla con N filas
- WHEN la canonización informa de F fusiones
- THEN la tabla queda con N − F filas

#### Scenario: una partida legítima nunca se pierde
- GIVEN dos filas del mismo jugador con puzzles distintos
- WHEN se ejecuta la canonización
- THEN las dos siguen existiendo

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

## Requirement: Las filas con atribución cruzada se declaran y no se tocan

<!-- origen: feat-identidad-canonica (added) -->

Una fila cuyo identificador pertenece a una persona y cuyo nombre mostrado indica otra **no la resuelve
este comando**. Se cuenta aparte y se deja exactamente como está.

**Ninguna de las dos señales basta, y las dos alternativas se probaron:**

- *Reatribuir al dueño del nombre* **fabrica partidas**. Se implementó y se ejecutó, apoyándose en que cinco
  de las seis filas cruzadas que el dueño del nombre ya tenía registradas coincidían en puntuación exacta.
  El canal desmintió la inferencia: de las tres restantes, dos correspondían a días en los que esa persona
  **no publicó nada** y la tercera era copia byte a byte de la cuadrícula de otra jugadora.
- *Eliminarlas* destruye datos apoyándose en que un nombre no cuadra con un identificador, que no es prueba
  de que la fila sea falsa.

Lo que las delata es **el canal**, y este cálculo no lo consulta. Por eso las declara y para. Hay una prueba
barata para quien decida: tras el backfill de patrones, **una fila sin mensaje en el canal se queda sin
patrón**.

Consecuencia declarada: la fila cruzada sigue ocupando su clave `(identificador, puzzle)`, así que puede
bloquear la canonización de su dueño legítimo. Ese bloqueo también se informa.

#### Scenario: identificador y nombre señalan a personas distintas
- GIVEN una fila cuyo identificador pertenece a un jugador y cuyo nombre mostrado es de otro
- WHEN se ejecuta la canonización
- THEN la fila queda intacta y consta en el recuento de atribuciones cruzadas

#### Scenario: una cruzada no se fusiona con la partida del dueño del nombre
- GIVEN una fila cruzada que coincide en puzzle y puntuación con una fila de la persona del nombre
- WHEN se ejecuta la canonización
- THEN las dos filas siguen existiendo

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

## Requirement: Toda migración de identidad admite ensayo

<!-- origen: feat-identidad-canonica (added) -->

El comando se puede ejecutar en modo ensayo: recorre, resuelve y cuenta exactamente lo que haría, sin
escribir ni eliminar nada. El recuento del ensayo y el de la ejecución real coinciden.

#### Scenario: el ensayo no modifica la tabla
- GIVEN una tabla con filas pendientes de canonizar
- WHEN se ejecuta el comando en modo ensayo
- THEN el recuento es el de la ejecución real y ninguna fila cambia

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

## Requirement: Reprocesar la ventana de ingesta no duplica filas

<!-- origen: feat-ingesta-por-id (added) -->

La ingesta relee los últimos mensajes cada hora, así que el mismo resultado se procesa muchas veces. La
escritura es un `upsert` sobre **(identificador, puzzle)**, que es la clave del índice único de la tabla,
así que reprocesar actualiza en lugar de insertar.

Esta es la razón por la que este slice va **después** de la migración de identidad y no antes: con el
extractor emitiendo identificadores sobre una tabla que guardaba nombres, las filas de la ventana se
habrían duplicado — 32 de las 40 últimas, medido.

```yaml
checks:
  - type: index
    table: wordle_results
    name: idx_slack_user_wordle_unique
    kind: unique
    columns: [slack_user_id, wordle_id]
```

#### Scenario: el mismo mensaje dos veces deja una sola fila
- GIVEN un resultado ya guardado
- WHEN se vuelve a procesar el mismo mensaje
- THEN sigue habiendo una sola fila para ese jugador y ese puzzle

#### Scenario: la escritura no toca columnas que no le corresponden
- GIVEN un resultado que se guarda
- WHEN se compone la fila
- THEN contiene identidad, nombre, puzzle, puntuación, fecha, texto y patrón, y nada más

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py

## Requirement: Lo calculado se materializa aparte de lo crudo

<!-- origen: feat-temporada-mensual (added), feat-temporada-cero (modified) -->

Lo que el pipeline calcula de una temporada vive en `season_snapshots`, **nunca en `wordle_results`**. La
tabla cruda solo guarda lo que ocurrió; lo derivado se puede borrar y recalcular sin perder nada.

La clave es `temporada`, así que recalcular **actualiza** en lugar de acumular versiones. Se registra
`updated_at` para poder detectar una instantánea rancia.

**Hay una fila por temporada del modelo, no una por mes con datos.** Con las temporadas numeradas desde un
límite, todo el periodo anterior es **una sola fila** (`temporada = '0'`) en lugar de una por cada mes. Al
cambiar el límite hay que **borrar las filas que el modelo ya no reconoce** antes de rematerializar: una
instantánea huérfana se sigue leyendo desde la web y aparecería como una temporada fantasma.

Cada instantánea declara además **si su clasificación está imputada**, para que un consumidor no compare
como equivalentes la media de una temporada numerada y la de la 0.

```yaml
checks:
  - type: table
    name: season_snapshots
    columns: [temporada, payload, updated_at]
    rls: read-only-for-publishable-key
```

#### Scenario: materializar deja una fila por temporada del modelo
- GIVEN resultados repartidos en varios meses anteriores al límite
- WHEN se materializan las temporadas
- THEN existe **una sola** fila para todo ese periodo

#### Scenario: la instantánea declara su criterio
- GIVEN la instantánea de una temporada
- WHEN se inspecciona
- THEN dice si su clasificación está imputada

#### Scenario: materializar dos veces no duplica
- GIVEN una temporada ya materializada
- WHEN se vuelve a materializar
- THEN sigue habiendo una sola fila para ella, con la marca de tiempo actualizada

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py

## Requirement: La categoría se deriva del patrón, no se almacena

<!-- origen: feat-clasificacion-de-figuras (added) -->

La figura de una partida se calcula a partir del patrón crudo **cada vez que se materializa la temporada**.
No existe una columna de categoría, y ningún proceso escribe el veredicto.

El precio está declarado: recalibrar un umbral cambia el álbum de todo el mundo en la siguiente
materialización. La contrapartida es que lo hace **sin migración** y sobre el histórico completo, que es lo
que permite que el clasificador siga mejorando.

Una partida **sin patrón no tiene categoría**. No se le asigna abstracto: abstracto es un veredicto sobre
un dibujo, y aquí no hay dibujo que mirar. Queda fuera del cálculo y la instantánea publica cuántas son.

El álbum usa **los mismos días que la temporada**. No tiene su propia definición de qué jornada cuenta.

#### Scenario: la figura sale del patrón crudo
- GIVEN un resultado con su cuadrícula almacenada
- WHEN se materializa la temporada
- THEN su categoría aparece en el recuento del jugador sin haberse escrito en ninguna columna

#### Scenario: sin patrón no se inventa categoría
- GIVEN un resultado que cuenta en la temporada pero no tiene patrón
- WHEN se calcula el álbum
- THEN no cuenta como figura ni como abstracto, y la instantánea dice cuántas partidas quedaron así

#### Scenario: el álbum hereda los días de la temporada
- GIVEN un resultado con patrón cuya jornada no cuenta en la temporada
- WHEN se calcula el álbum
- THEN su patrón tampoco entra

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py

## Requirement: La simetría es un rasgo del patrón, y no se almacena

<!-- origen: feat-figuras-simetricas (added) -->

La simetría en espejo se **deriva de la columna `pattern`** cada vez que se clasifica, igual que el resto de
los rasgos del dibujo. No se añade ninguna columna, ningún índice y ningún campo a la instantánea: lo que
viaja es la categoría resultante, no cómo se llegó a ella.

Es la misma propiedad que sostiene todo el álbum: recalibrar reclasifica el histórico solo, sin migración.
Persistir «este patrón es simétrico» crearía un dato que hay que mantener a mano en cuanto la definición del
rasgo cambie, y dejaría el histórico irrecuperable en cada ajuste.

El rasgo se mide sobre el **cuerpo** de la cuadrícula, nunca sobre la cuadrícula entera. La banda verde final
—la fila de la palabra acertada— es simétrica en toda partida resuelta, así que incluirla convertiría el
rasgo en «¿ha resuelto?», que ya se sabe por otro camino.

```yaml
checks:
  - type: cli-command
    command: python3 tools/calibrate_figures.py --sin-red
    expect: el acuerdo con el conjunto dorado no baja de 24 fichas
  - type: column
    table: wordle_results
    column: pattern
    note: el rasgo se deriva de esta columna; no se crea ninguna otra
```

#### Scenario: la simetría no añade columnas
- GIVEN el esquema de `wordle_results`
- WHEN se clasifica una cuadrícula simétrica
- THEN la categoría se deriva de `pattern` y no se escribe en ninguna columna nueva

#### Scenario: el mismo patrón da el mismo veredicto sin estado
- GIVEN una cuadrícula cualquiera
- WHEN se clasifica dos veces
- THEN el veredicto es el mismo, sin depender de una clasificación anterior

verified-by:
  - tests/slices/clasificacion-de-figuras/test_simetria.py

## Requirement: La categoría de un resultado depende de cuándo se jugó

<!-- origen: feat-geometria-antes-que-loro (modified) -->

La figura de una cuadrícula ya no se deriva solo del patrón: se deriva del patrón **y de su jornada**, porque
las reglas de clasificación cambian con el tiempo y los cambios no se aplican hacia atrás.

Consecuencia práctica: dos cuadrículas idénticas jugadas a distinto lado de un cambio de reglas pueden tener
categorías distintas, y eso es correcto — cada partida se juzga con las reglas que estaban en vigor cuando se
jugó, igual que la temporada 0 conserva las suyas.

Consecuencia para quien consuma esto: **el patrón por sí solo no basta** para saber la categoría. Todo cálculo
que clasifique resultados tiene que llevar la jornada consigo; si no la lleva, obtiene el orden histórico, que
es lo correcto para reproducir el pasado y lo incorrecto para una partida de hoy.

#### Scenario: la categoría se deriva del patrón y de la jornada
- **WHEN** se clasifica el resultado de una jornada
- **THEN** se aplican las reglas vigentes en esa jornada, no las últimas
- **AND** un resultado anterior a un cambio de reglas conserva su categoría original

verified-by:
  - tests/slices/clasificacion-de-figuras/test_orden_de_reglas.py
  - tests/slices/figuras-de-la-jornada/test_ultima_jornada.py


## Requirement: Un mismo rasgo se juzga con un solo criterio

<!-- origen: feat-espejo-gana-a-la-flor (modified) -->

La simetría de una cuadrícula decide dos cosas —su categoría y un logro— y las dos usan **el mismo** criterio
de qué cuenta como espejo.

Tenerlo por duplicado producía una contradicción observable: el logro consideraba accidente un espejo de dos
filas mientras la categoría lo trataba como espejo bueno, así que una flor legítima perdía su figura por una
simetría que el propio sistema no reconocía como gesta.

#### Scenario: el logro y la categoría usan el mismo umbral
- **WHEN** se decide si una cuadrícula es un espejo
- **THEN** el criterio es el mismo para la categoría y para el logro

verified-by:
  - tests/slices/clasificacion-de-figuras/test_orden_de_reglas.py
  - tests/slices/clasificacion-de-figuras/test_simetria.py
  - tests/slices/figuras-de-la-jornada/test_ultima_jornada.py
  - tests/slices/medallas-de-figuras/test_espejo_perfecto.py


## Requirement: Un resultado publicado deja de ser cierto cuando cambia su contexto

<!-- origen: fix-cierre-de-temporada (modified) -->

Lo que la web enseña de una temporada no se recalcula al pintarlo: sale de una instantánea escrita antes. Eso
la hace rápida y consistente con lo que publica el bot, y tiene un precio que hay que administrar: **una
instantánea es cierta solo mientras nada de lo que la rodea cambie**.

El caso que lo demostró no fue un dato mal calculado, sino un dato que **envejeció**: el estado de una
temporada depende de si existe otra posterior, así que empezar un mes nuevo vuelve falsa la instantánea del
anterior sin tocarla.

De ahí la regla: cuando un hecho de una temporada dependa de algo externo a ella, hay que **reescribirla
cuando ese algo cambie**, no confiar en que se calculará al leer.

#### Scenario: la instantánea de un mes cerrado no se queda con el estado viejo
- **WHEN** empieza una temporada nueva
- **THEN** la anterior se reescribe, porque su estado dependía de que no hubiera ninguna posterior

verified-by:
  - tests/slices/temporada-mensual/test_temporada_mensual.py


## Requirement: La frescura de los resultados no puede depender de un servicio que no la garantiza

<!-- origen: fix-reloj-de-repuesto (modified) -->

Los resultados que la web enseña son tan recientes como la última sincronización, y esa sincronización se
apoya en un reloj externo al sistema. Cuando ese reloj no garantiza nada, **la frescura de los datos tampoco
está garantizada**, aunque el código sea correcto.

Es lo que ocurrió: el pipeline funcionaba y la web mostraba datos de hasta seis horas antes, porque las
ejecuciones simplemente no se lanzaban. Ningún test podía cazarlo — no había nada roto que probar.

De ahí dos exigencias sobre la ingesta: que se despierte desde **más de un reloj**, de modo que la
indisponibilidad de uno no detenga los datos; y que **un fallo transitorio no consuma la ventana**, porque
cuando las ventanas son escasas perder una por un timeout de un segundo cuesta horas de retraso.

#### Scenario: los datos siguen llegando aunque un reloj falle
- **WHEN** el planificador que dispara la ingesta descarta su ventana
- **THEN** otro reloj la dispara, y los resultados se sincronizan igual dentro de la hora

verified-by:
  - tests/slices/temporada-mensual/disparador.test.js
  - tests/slices/temporada-mensual/test_temporada_mensual.py


## Requirement: Un fixture que representa una categoría no puede cumplir otra

<!-- origen: feat-espejo-de-dos-filas (modified) -->

Los patrones que los tests usan como ejemplo de una categoría tienen que cumplir **solo** esa: un fixture
llamado «flor» que además es un espejo hace que su test mida la regla del espejo sin declararlo, y cambia de
significado cuando esa otra regla cambia.

Ocurrió: `Y...Y/..Y../GGGGG` se usaba como flor en cuatro ficheros de test y es palíndromo en sus dos filas.
Al bajar el umbral del espejo, esos tests se pusieron en rojo por un motivo que no era el suyo.

Cuando un test dependa de que su fixture sea inequívoco, esa condición **se comprueba** en el propio test en
lugar de suponerse.

#### Scenario: un fixture no ambiguo se comprueba, no se supone
- **WHEN** un test necesita un patrón que solo cumpla una regla de clasificación
- **THEN** el test verifica que cumple exactamente una antes de usarlo

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py
  - tests/slices/clasificacion-de-figuras/test_orden_de_reglas.py
  - tests/slices/figuras-de-la-jornada/test_ultima_jornada.py
  - tests/slices/medallas-de-figuras/test_espejo_perfecto.py
  - tests/slices/medallas-de-figuras/test_medallas_de_figuras.py
  - tests/slices/resumen-diario-compuesto/test_resumen.py


## Requirement: La frescura de los datos se defiende con cobertura, no con más disparos

<!-- origen: fix-latido-horario (modified) -->

Cuando el planificador que dispara la ingesta no cumple lo declarado y no hay reloj externo que funcione, la
cadencia no se consigue pidiendo más disparos: se consigue haciendo que **cada disparo cubra más tiempo**.

Una ejecución sincroniza repetidamente durante horas en lugar de una sola vez, de modo que unos pocos disparos
al día bastan para una cadencia horaria. El intervalo entre sincronizaciones se elige para que ningún hueco
supere la hora, y el número de repeticiones para cubrir el hueco máximo medido en el planificador.

Solo hay una ejecución viva: un disparo nuevo cancela la anterior y reinicia la ventana de cobertura, en lugar
de acumular ejecuciones solapadas. Cancelar a media sincronización es seguro porque la ingesta y la
materialización son idempotentes.

Un fallo de una repetición no aborta las siguientes: perder una hora es preferible a perder el resto de la
ventana.

#### Scenario: unos pocos disparos dan cobertura horaria
- **WHEN** el planificador dispara la ingesta unas pocas veces al día
- **THEN** cada disparo sincroniza repetidamente hasta cubrir el hueco típico entre disparos
- **AND** ningún intervalo entre sincronizaciones supera la hora

#### Scenario: un fallo aislado no cuesta la ventana
- **WHEN** una de las sincronizaciones de la ventana falla
- **THEN** las siguientes se ejecutan igual, y la ejecución termina en error para que el fallo se vea

```yaml
checks:
  - type: regex
    file: .github/workflows/update_stats.yml
    pattern: 'cancel-in-progress: true'
    describe: solo hay una ejecución viva; un disparo nuevo cancela la anterior
  - type: regex
    file: .github/workflows/update_stats.yml
    pattern: 'timeout-minutes: 350'
    describe: la ejecución dura lo bastante para cubrir varias horas sincronizando
```

## Requirement: La frescura se persigue con dos mecanismos que se complementan

<!-- origen: feat-cadencia-de-sincronizacion (modified) -->

La ingesta se dispara por ventanas frecuentes **y** cada ejecución cubre varias horas sincronizando
repetidamente. Las dos piezas responden a fallos distintos del planificador y ninguna sobra:

- las **ventanas** dan frecuencia cuando el planificador responde;
- la **cobertura por ejecución** da continuidad cuando el planificador calla.

El sistema se adapta solo: con el planificador sano, cada ventana cancela la ejecución en curso y sincroniza,
así que el bucle nunca pasa de su primera vuelta; con el planificador callado, la ejecución viva sigue
sincronizando y cubre el silencio.

Cancelar una ejecución a media sincronización es seguro porque la ingesta y la materialización son
idempotentes.

#### Scenario: las ventanas y la cobertura se complementan
- **WHEN** el planificador descarta la mayoría de las ventanas
- **THEN** la ejecución que sí arrancó sigue sincronizando y la cadencia se mantiene

verified-by:
  - tests/slices/cadencia-de-sincronizacion/test_cadencia.py


## Requirement: Una forma puede ser propiedad de la palabra y no del jugador

<!-- origen: feat-categoria-culo (modified) -->

Algunas cuadrículas se parecen entre sí porque **la palabra del día las obliga**, no porque quien jugó hiciera
algo particular. En la jornada que originó la categoría del melocotón, 8 de los 10 jugadores terminaron con la
misma penúltima fila: las letras impares eran fáciles y las pares difíciles, así que el grupo entero convergió
en el mismo esqueleto.

Consecuencia para quien lea el álbum: **una categoría puede aparecer en racimo**, varios el mismo día y
ninguno en meses. No es un fallo del clasificador ni una casualidad sospechosa; es la palabra repartiendo la
misma forma a todos.

Y consecuencia para quien añada categorías: una forma frecuente **dentro de un solo día** puede ser rarísima
en el histórico. Elegir el umbral o la puntuación mirando un día induce a error; hay que medir sobre el
histórico completo.

#### Scenario: una forma puede repetirse el mismo día en varios jugadores
- **WHEN** la palabra del día tiene un esqueleto de letras fáciles y difíciles muy marcado
- **THEN** varios jugadores terminan con la misma forma, y todos reciben la misma categoría

verified-by:
  - tests/slices/album-de-figuras/album.test.js
  - tests/slices/clasificacion-de-figuras/test_album.py
  - tests/slices/clasificacion-de-figuras/test_orden_de_reglas.py
  - tests/slices/voz-de-la-jornada/test_memes.py


## Requirement: Los niveles congelados viven en una tabla aditiva que nadie puede cambiar

<!-- origen: feat-nivel-congelado (added), fix-hora-de-congelar (modified) -->

`public.game_levels` guarda una fila por jornada: `jornada` (clave), `fecha`, `nivel` (el objeto de `nivelDe`
tal cual, en `jsonb`) y `frozen_at`. Es **aditiva** (ADR 0005). La fila de una jornada aparece **a partir de
las 02:00 de Madrid del día siguiente** (antes, de las 04:00), en la primera vuelta del cron desde esa hora.

La clave pública solo la lee. La escribe el cron con la clave de servicio. Y **nadie la cambia**: un trigger
rechaza cualquier `update`, `delete` o `truncate`, también con la clave de servicio y como superusuario.
Arreglar un nivel a mano exige quitar el trigger a propósito.

#### Scenario: la fila de ayer aparece desde las 02:00
- GIVEN el día D a las 02:00 de Madrid o después
- WHEN corre el cron
- THEN `game_levels` tiene la fila de la jornada de D-1

#### Scenario: un nivel congelado no se cambia
- GIVEN un nivel congelado
- WHEN la clave de servicio o el superusuario intentan cambiarlo, borrarlo o vaciar la tabla
- THEN Postgres lo rechaza con «un nivel congelado no se cambia» y el nivel sigue igual

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260925140000_create_game_levels.sql
    pattern: 'before update or delete on public\.game_levels'
    describe: el trigger que hace inmutable el nivel congelado
```

verified-by:
  - tests/slices/nivel-congelado/congelar.test.js
  - tests/slices/nivel-congelado/test_game_levels.py

## Requirement: `registrar_tiempo` se mide contra el nivel congelado

<!-- origen: feat-nivel-congelado (added) -->

`registrar_tiempo` (misma firma y permisos) solo acepta jornadas **con nivel congelado**. El mínimo de tiempo
sale de los tramos de ese nivel —una etiqueta por tramo— y el máximo de estrellas, de sus coleccionables. Una
jornada con cuadrículas en `wordle_results` pero sin congelar se rechaza como «esa jornada no tiene nivel».

#### Scenario: una jornada sin congelar no admite marcas
- GIVEN una jornada con cuadrículas pero sin nivel congelado
- WHEN se registra un tiempo
- THEN se rechaza

#### Scenario: las estrellas se acotan a los coleccionables del nivel
- GIVEN un nivel de 2 tramos y 1 coleccionable
- WHEN se registran 2 estrellas
- THEN se rechaza; con 1, se acepta

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260925140000_create_game_levels.sql
    pattern: "select l\\.nivel into nivel from public\\.game_levels l where l\\.jornada = p_jornada;"
    describe: la función lee el nivel congelado de la jornada
  - type: regex
    file: supabase/migrations/20260925140000_create_game_levels.sql
    pattern: "coleccionables := coalesce\\(jsonb_array_length\\(nivel -> 'collectibles'\\), 0\\);"
    describe: el máximo de estrellas sale de los coleccionables del nivel
```

verified-by:
  - tests/slices/nivel-congelado/test_game_levels.py

## Requirement: Las marcas del juego viven en una tabla aditiva que la clave pública solo lee

<!-- origen: feat-ranking-del-juego (added) -->

`public.game_times` guarda **una fila por `(jornada, jugador)`** con la mejor marca: `segundos` (centésimas),
`estrellas` y `updated_at`. Es **aditiva** (ADR 0005): no cambia `wordle_results` ni `season_snapshots`.

Con la clave pública, la tabla **solo se lee**: RLS con política de lectura y sin privilegios de escritura para
`anon` ni `authenticated`. La única vía de escritura es la función `registrar_tiempo`.

#### Scenario: la clave pública no escribe en la tabla
- GIVEN los roles `anon` y `authenticated`
- WHEN intentan insertar, cambiar, borrar o vaciar filas de `game_times`
- THEN Postgres lo rechaza y las marcas siguen intactas

#### Scenario: la clave pública sí la lee
- GIVEN una marca registrada
- WHEN `anon` lee la tabla
- THEN la ve

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260925120000_create_game_times.sql
    pattern: 'revoke insert, update, delete, truncate on public\.game_times from anon, authenticated;'
    describe: la clave pública no tiene privilegios de escritura sobre la tabla
  - type: regex
    file: supabase/migrations/20260925120000_create_game_times.sql
    pattern: 'alter table public\.game_times enable row level security;'
    describe: la tabla tiene RLS
```

verified-by:
  - tests/slices/ranking-del-juego/test_registrar_tiempo.py

## Requirement: `registrar_tiempo` solo sobrescribe una marca si la mejora, y rechaza lo imposible

<!-- origen: feat-ranking-del-juego (added) -->

`public.registrar_tiempo(p_jornada, p_jugador, p_segundos, p_estrellas)` es `security definer` con
`search_path` vacío y la ejecutan `anon` y `authenticated`. Inserta la marca, o la sustituye **solo si el tiempo
nuevo es menor**; un tiempo igual o peor deja la anterior. Devuelve `{ mejora, segundos }` con la marca que se
queda.

Rechaza, sin escribir nada: un jugador que no aparece en `wordle_results`; una jornada sin nadie con
cuadrícula; estrellas negativas o por encima del número de tramos; y un tiempo por debajo de
`tramos × 8 × 32 ÷ (300 × 1,5)` segundos —recorrer el nivel a la velocidad máxima del motor, con un 50 % de
margen— o de una hora o más.

No hay autenticación: cualquiera puede registrar a nombre de cualquiera. Es el modelo de confianza declarado
del grupo, no un descuido.

#### Scenario: la primera marca se guarda con centésimas
- GIVEN un jugador sin marca en un nivel
- WHEN `anon` llama a `registrar_tiempo`
- THEN se guarda redondeada a centésimas y devuelve `mejora: true`

#### Scenario: un tiempo igual o peor no pisa la marca
- GIVEN una marca de 40 s
- WHEN se registra 40 s o 55 s
- THEN la marca sigue en 40 s con sus estrellas y devuelve `mejora: false`

#### Scenario: un tiempo mejor la sustituye
- GIVEN una marca de 40 s
- WHEN se registra 31,5 s
- THEN la marca pasa a 31,5 s con las estrellas nuevas

#### Scenario: lo imposible se rechaza
- GIVEN un jugador desconocido, una jornada sin nivel, estrellas de más o un tiempo por debajo del mínimo
- WHEN se llama a `registrar_tiempo`
- THEN falla con el motivo y la tabla no cambia

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260925120000_create_game_times.sql
    pattern: "security definer\\s+set search_path = ''"
    describe: la función privilegiada no hereda el search_path de quien la llama
  - type: regex
    file: supabase/migrations/20260925120000_create_game_times.sql
    pattern: 'where excluded\.segundos < actual\.segundos;'
    describe: solo se sustituye una marca por un tiempo estrictamente menor
```

verified-by:
  - tests/slices/ranking-del-juego/test_registrar_tiempo.py

## Requirement: Un nivel admite marcas solo mientras es el último congelado

<!-- origen: feat-juego-en-la-temporada (added) -->

`registrar_tiempo` acepta marcas únicamente para **la última jornada congelada** en `game_levels`. Una jornada
congelada anterior se rechaza con «ese nivel ya está cerrado», sin escribir nada. Así el ranking de un nivel
deja de cambiar en cuanto se congela el siguiente, y la clasificación del mes del juego no se reescribe hacia
atrás. El resto de validaciones —jugador, estrellas, tiempo mínimo, solo si mejora— no cambia.

La migración es aditiva: reemplaza la función con la misma firma y los mismos permisos.

#### Scenario: el nivel anterior está cerrado
- GIVEN dos niveles congelados, las jornadas N y N+1
- WHEN se registra un tiempo para la jornada N
- THEN falla con «ese nivel ya está cerrado» y `game_times` no cambia

#### Scenario: el último nivel sigue abierto
- GIVEN los mismos dos niveles
- WHEN se registra un tiempo para la jornada N+1
- THEN se guarda como siempre

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql
    pattern: 'if p_jornada <> \(select max\(l.jornada\) from public.game_levels l\) then'
    describe: solo el último nivel congelado admite marcas
```

verified-by:
  - tests/slices/ranking-del-juego/test_registrar_tiempo.py

## Requirement: La materialización lee los niveles y las marcas del juego

<!-- origen: feat-juego-en-la-temporada (added), feat-victoria-el-ultimo-dia (modified) -->

`materialize_seasons.py` lee `game_levels` (jornada, fecha) y `game_times` (jornada, jugador, segundos,
estrellas) con la clave de servicio, paginando como con `wordle_results`, y se los pasa a la función de la
clasificación del juego. No escribe en esas tablas. La **fecha** de cada nivel decide en qué mes puntúa: el de
su jornada, o el siguiente si es el último día laborable del mes. El publicador lee los mismos datos para la
victoria del último día.

#### Scenario: la fecha del nivel decide su mes
- GIVEN un nivel con fecha del último día laborable de un mes
- WHEN se materializan ese mes y el siguiente
- THEN el nivel puntúa en el siguiente

verified-by:
  - tests/slices/clasificacion-del-juego/test_clasificacion_del_juego.py

## Requirement: Una marca mejora con más estrellas, o con las mismas en menos tiempo

<!-- origen: feat-juego-en-la-temporada (added) -->

Las estrellas pesan más que el tiempo (decisión del dueño). `registrar_tiempo` sustituye la marca de un jugador
en un nivel solo si la nueva tiene **más estrellas**, o **las mismas estrellas en menos tiempo**. Con menos
estrellas no la sustituye aunque sea más rápida, y con las mismas estrellas y el mismo tiempo tampoco. Devuelve
`{ mejora, segundos, estrellas }` con la marca que se queda.

#### Scenario: más estrellas mejora aunque sea más lento
- GIVEN una marca de 9 estrellas en 12 s
- WHEN se registran 13 estrellas en 15 s
- THEN la marca pasa a 13 estrellas y 15 s

#### Scenario: menos estrellas no mejora aunque sea más rápido
- GIVEN una marca de 13 estrellas en 15 s
- WHEN se registran 9 estrellas en 12 s
- THEN la marca sigue en 13 estrellas y 15 s

#### Scenario: con las mismas estrellas, gana el tiempo
- GIVEN una marca de 5 estrellas en 40 s
- WHEN se registran 5 estrellas en 31,5 s, y después 5 en 40 s
- THEN la marca pasa a 31,5 s y la segunda no la cambia

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql
    pattern: 'where excluded.estrellas > actual.estrellas\s+or \(excluded.estrellas = actual.estrellas and excluded.segundos < actual.segundos\);'
    describe: la regla de mejora pone las estrellas por delante
```

verified-by:
  - tests/slices/ranking-del-juego/test_registrar_tiempo.py

## Requirement: El nombre de un autor externo se guarda legible, y se corrige al reprocesar

<!-- origen: fix-nombre-de-autores-externos (added) -->

`player_name` de un autor externo es el nombre de su perfil de Slack, no su id. Como la ingesta es un
`upsert` sobre `(slack_user_id, wordle_id)` que reescribe `player_name`, una fila que se guardó con el id
como nombre se corrige sola la siguiente vez que su mensaje entra en la ventana.

#### Scenario: una fila guardada con el id como nombre se corrige al reprocesarla
- GIVEN una fila de un autor externo con su id como `player_name`
- WHEN su mensaje se vuelve a procesar con el directorio completado
- THEN la misma fila lleva ahora el nombre de su perfil

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py

## Requirement: La instantánea publica el mínimo del álbum que se aplicó

<!-- origen: feat-participacion-y-album-al-arrancar (modified) -->

El campo `minimo` del álbum en la instantánea es el mínimo **efectivo** de la temporada —las jornadas que
lleva, con tope—, no la constante: la web lo enseña para explicar por qué una fila no tiene puesto, y tiene
que ser el que decidió.

#### Scenario: el mínimo publicado es el que decidió
- GIVEN una temporada mensual con una jornada
- WHEN se materializa el álbum
- THEN `minimo` vale 1

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py

## Requirement: El debate vive en tablas aditivas que solo escriben sus funciones

<!-- origen: feat-debate-de-reglas (added), feat-pestana-debate (modified), feat-propuestas-votables (modified) -->

Con la clave pública se leen las propuestas que no están rechazadas. `rule_proposal_votes` guarda un voto por
`(propuesta, votante)`, `a_favor` o `en_contra`; solo lo escribe `votar_propuesta`, que rechaza propuestas
inexistentes o rechazadas, sentidos desconocidos y a quien no ha jugado nunca.

#### Scenario: una propuesta rechazada no admite votos
- **WHEN** llega un voto a una propuesta rechazada
- **THEN** se rechaza como propuesta desconocida

#### Scenario: la clave pública no escribe en los votos de propuestas
- **WHEN** se intenta insertar o borrar directamente en `rule_proposal_votes`
- **THEN** Postgres lo rechaza

```yaml
checks:
  - type: regex
    file: supabase/migrations/20261015090000_public_votable_proposals.sql
    pattern: 'revoke insert, update, delete, truncate on public\.rule_proposal_votes from anon, authenticated;'
    describe: la clave pública no tiene privilegios de escritura sobre los votos de propuestas
```

verified-by:
  - tests/slices/debate-de-reglas/test_debate_sql.py
