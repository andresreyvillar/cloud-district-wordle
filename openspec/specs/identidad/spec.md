# Spec de `identidad`

Spec **viva** del dominio `identidad` (ver `openspec/README.md`). Se edita directamente en la rama de cada cambio,
junto al código y los tests que la cumplen ([ADR 0009](../../decisions/0009-specs-vivas.md)). Cada Requirement
lleva en un comentario los change packs de los que sale, archivados en `openspec/changes/archive/`.

## Requirement: El identificador canónico de un jugador es su ID de Slack

<!-- origen: feat-identidad-canonica (added) -->

La identidad de un jugador es el identificador que Slack le asigna, no el nombre que muestra. El
identificador no cambia nunca; el nombre sí, y cambia sin avisar.

La columna `slack_user_id` de `wordle_results` contiene ese identificador. Un valor que no tiene forma de
identificador de Slack indica una fila pendiente de canonizar, no una identidad alternativa.

```yaml
checks:
  - type: column
    table: wordle_results
    column: slack_user_id
    describe: contiene identificadores de Slack, no nombres mostrados
```

#### Scenario: una fila con nombre se canoniza
- GIVEN una fila cuya identidad es un nombre mostrado que corresponde a una persona del workspace
- WHEN se ejecuta la canonización
- THEN la fila guarda el identificador de Slack de esa persona

#### Scenario: una fila ya canónica no se modifica
- GIVEN una fila cuya identidad ya es un identificador de Slack
- WHEN se ejecuta la canonización
- THEN la fila no cambia

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

## Requirement: Un cambio de nombre no crea un jugador nuevo

<!-- origen: feat-identidad-canonica (added) -->

Dos filas que pertenecen a la misma persona son del mismo jugador aunque su nombre mostrado difiera. Si
el nombre cambió entre dos partidas, las dos siguen siendo del mismo jugador.

Cuando dos identidades resuelven al mismo identificador y coinciden en puzzle y puntuación, son la misma
partida registrada dos veces y queda una sola fila.

#### Scenario: el mismo puzzle registrado bajo dos nombres
- GIVEN dos filas del mismo puzzle con la misma puntuación, cuyas identidades resuelven al mismo identificador
- WHEN se ejecuta la canonización
- THEN queda una sola fila para ese jugador y ese puzzle

#### Scenario: dos partidas distintas del mismo jugador no se fusionan
- GIVEN dos filas del mismo jugador con puzzles distintos
- WHEN se ejecuta la canonización
- THEN las dos filas se conservan

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

## Requirement: El nombre mostrado es un atributo, no la identidad

<!-- origen: feat-identidad-canonica (added) -->

`player_name` guarda el nombre con el que se muestra al jugador. La canonización **no lo toca**: es la
columna que lee la web publicada, y cambiarla rompería la v1
([ADR 0005](../../../../decisions/0005-hosting-y-convivencia-v1-v2.md)).

Un nombre que no corresponde a ninguna persona del workspace no invalida la fila: la deja pendiente y se
declara. Un jugador que se marchó de la empresa jugó de verdad.

#### Scenario: el nombre mostrado sobrevive a la canonización
- GIVEN una fila con su nombre mostrado
- WHEN la canonización le escribe el identificador
- THEN el nombre mostrado conserva el valor que tenía

#### Scenario: un nombre desconocido se declara en lugar de borrarse
- GIVEN una fila cuyo nombre no corresponde a nadie del workspace
- WHEN se ejecuta la canonización
- THEN la fila conserva su identidad y se cuenta como no resuelta

verified-by:
  - tests/slices/identidad-canonica-de-jugador/test_identidad_canonica.py

## Requirement: La identidad de un resultado es el identificador de quien lo publicó

<!-- origen: feat-ingesta-por-id (added) -->

La identidad de una fila se toma del campo de autor del mensaje de Slack. **Nunca se deriva del texto**,
ni del nombre mostrado, ni se inventa un valor de relleno cuando falta.

Un identificador de Slack no cambia y no se reasigna. Es lo que hace que un renombre no parta a un jugador
en dos, que era el fallo que este dominio arrastraba.

#### Scenario: el renombre no crea un jugador nuevo
- GIVEN un jugador con resultados guardados que cambia su nombre en Slack
- WHEN publica un resultado nuevo y se procesa
- THEN la fila nueva lleva el mismo identificador que las anteriores

#### Scenario: sin autor no hay identidad
- GIVEN un resultado cuyo mensaje no trae autor
- WHEN se procesa
- THEN no se escribe una identidad de relleno

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py

## Requirement: El nombre visible se resuelve del identificador, con etiqueta acordada por delante

<!-- origen: feat-ingesta-por-id (added) -->

El nombre que se guarda para mostrar sale del nombre que la persona muestra en Slack, salvo que el grupo
tenga una **etiqueta acordada** para ella, que gana.

Las etiquetas son las mínimas necesarias, medidas contra la tabla: 18 de los 21 jugadores ya tienen el
nombre de Slack idéntico al guardado, y las tres etiquetas cubren a quienes muestran un handle
(`carlos.h`, `ivan.antona`, `Andres R`). Un diccionario más grande **renombraría a seis personas**, una de
ellas con el nombre de otra.

#### Scenario: la etiqueta acordada gana al handle
- GIVEN una persona cuyo nombre en Slack es un handle y que tiene etiqueta acordada
- WHEN se guarda su resultado
- THEN el nombre guardado es la etiqueta

#### Scenario: sin etiqueta se guarda el nombre de Slack
- GIVEN una persona sin etiqueta acordada
- WHEN se guarda su resultado
- THEN el nombre guardado es el que muestra en Slack

#### Scenario: el nombre guardado nunca es el identificador crudo
- GIVEN cualquier resultado con autor conocido
- WHEN se guarda
- THEN el nombre guardado es legible, porque es lo que muestra la web publicada

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py

## Requirement: El palmarés de un jugador se sigue por identidad, no por nombre

<!-- origen: feat-ficha-de-jugador (added) -->

El palmarés cruza todas las temporadas de un jugador **por su identificador de Slack**. Es lo que hace que
un renombre no le parta el historial en dos: es el mismo fallo que ya se corrigió en los resultados
([ADR 0006](../../../decisions/0006-estructura-de-informacion-v2.md)), y aquí volvería a aparecer si el
cruce fuera por nombre.

El nombre solo se usa para mostrarlo, y se toma de la temporada que se esté mirando: así una ficha antigua
enseña el nombre con el que se jugó.

#### Scenario: el palmarés recorre las temporadas del jugador
- GIVEN un jugador con resultados en varias temporadas
- WHEN se mira su palmarés
- THEN aparece una línea por temporada con su puesto y su media, de la más reciente a la más antigua, y la
  temporada abierta queda señalada

#### Scenario: el palmarés omite las temporadas que no jugó
- GIVEN un jugador que no jugó una de las temporadas materializadas
- WHEN se mira su palmarés
- THEN esa temporada no aparece

#### Scenario: sin nombre conocido se muestra el identificador
- GIVEN un identificador sin resultados en ninguna temporada
- WHEN se abre su ficha
- THEN se muestra el identificador, porque inventar un nombre sería peor que no tenerlo

verified-by:
  - tests/slices/ficha-de-jugador/ficha.test.js

## Requirement: Un autor externo se identifica por su id de Slack, como cualquier otro

<!-- origen: fix-nombre-de-autores-externos (added) -->

Que un autor no esté en el directorio del workspace no cambia su identidad: su fila guarda su id de Slack
en `slack_user_id`. Completar el directorio solo le da nombre; no lo une ni lo separa de nadie.

#### Scenario: el autor externo conserva su id como identidad
- GIVEN un resultado de un usuario externo de Slack Connect
- WHEN se extrae y se guarda
- THEN su identidad es su id de Slack, y su nombre el de su perfil

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py
