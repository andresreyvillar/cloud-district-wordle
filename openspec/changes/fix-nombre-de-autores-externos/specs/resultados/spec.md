# Deltas de `resultados` — fix-nombre-de-autores-externos

## ADDED Requirements

### Requirement: El nombre de un autor externo se guarda legible, y se corrige al reprocesar

`player_name` de un autor externo es el nombre de su perfil de Slack, no su id. Como la ingesta es un
`upsert` sobre `(slack_user_id, wordle_id)` que reescribe `player_name`, una fila que se guardó con el id
como nombre se corrige sola la siguiente vez que su mensaje entra en la ventana.

#### Scenario: una fila guardada con el id como nombre se corrige al reprocesarla
- GIVEN una fila de un autor externo con su id como `player_name`
- WHEN su mensaje se vuelve a procesar con el directorio completado
- THEN la misma fila lleva ahora el nombre de su perfil

verified-by:
  - tests/slices/ingesta-por-id-de-slack/test_ingesta_por_id.py
