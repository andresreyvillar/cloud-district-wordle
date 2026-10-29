# Deltas de `dashboard` — feat-clasificacion-de-temporada

## ADDED Requirements

### Requirement: La vista de temporada muestra la clasificación y su contexto

La vista de una temporada muestra el podio, la tabla completa y el contexto que la hace legible: cuántos
jugaron, cuántos días válidos tuvo, la media del grupo y qué jornada fue la más dura.

Y dice **cuándo se calculó**, porque es un dato derivado que puede quedar rancio si el cron falla
([ADR 0008](../../../decisions/0008-donde-vive-el-calculo.md)).

#### Scenario: una temporada poblada muestra su tabla
- GIVEN una temporada con clasificación materializada
- WHEN el grupo la abre
- THEN ve el podio y una fila por jugador con su posición y sus medias

#### Scenario: una temporada sin días válidos lo explica
- GIVEN una temporada cuyos días no alcanzan la muestra mínima
- WHEN el grupo la abre
- THEN la vista lo explica en lugar de mostrar una tabla vacía

#### Scenario: la vista dice cuándo se calculó
- GIVEN una clasificación materializada
- WHEN se muestra
- THEN indica la antigüedad del cálculo

verified-by:
  - tests/slices/clasificacion-de-temporada/test_clasificacion.py
