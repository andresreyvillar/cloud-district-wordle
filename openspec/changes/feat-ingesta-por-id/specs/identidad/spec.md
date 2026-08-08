# Deltas de `identidad` — feat-ingesta-por-id

## ADDED Requirements

### Requirement: La identidad de un resultado es el identificador de quien lo publicó

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

### Requirement: El nombre visible se resuelve del identificador, con etiqueta acordada por delante

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
