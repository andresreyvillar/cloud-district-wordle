# Deltas de `resultados` — feat-ingesta-por-id

## ADDED Requirements

### Requirement: Reprocesar la ventana de ingesta no duplica filas

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
