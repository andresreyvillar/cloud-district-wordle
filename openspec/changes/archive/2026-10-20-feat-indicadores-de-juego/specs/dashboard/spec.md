# Deltas de `dashboard` — feat-indicadores-de-juego

## ADDED Requirements

### Requirement: La ficha pinta el bloque «Cómo juegas»

La ficha de un jugador enseña eficiencia, apertura, suerte y acierto más milagroso de la temporada, comparados
con el grupo. Con pocas partidas dice cuántas faltan; sin indicadores en la instantánea dice que no están
disponibles. El bloque no habla de trampas.

#### Scenario: el bloque sale en la ficha
- GIVEN una instantánea con indicadores del jugador
- WHEN se abre su ficha
- THEN se ven los cuatro indicadores

#### Scenario: el bloque no habla de trampas
- WHEN se pinta el bloque
- THEN no contiene «trampa», «tramposo» ni «sospecha»

verified-by:
  - tests/slices/indicadores-de-juego/indicadores.test.js
