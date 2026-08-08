# Deltas de `ingesta` — fix-backfill-por-identificador

## MODIFIED Requirements

### Requirement: El backfill empareja mensaje y fila por identificador

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
