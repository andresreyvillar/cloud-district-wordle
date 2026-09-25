# Deltas de `estadisticas` — fix-sospecha-de-la-mejor-nota

## MODIFIED Requirements

### Requirement: Una nota se lee contra las del mismo día, no en solitario

Que alguien resuelva en dos intentos no significa lo mismo según lo que haya hecho el resto: con un 1 en la
mesa es la segunda mejor marca, y compartida con otra persona es señal de que la palabra era fácil.

Los hechos que se derivan de una nota baja se calculan por tanto **relativos a la jornada**: cuál fue la mejor
nota y cuánta gente la firmó. Es el mismo principio que ya gobierna `sembrado` y `no-inspirado`, que se miden
contra la media del día en lugar de contra un umbral fijo.

#### Scenario: la mejor nota de la jornada se calcula antes de juzgar ninguna
- GIVEN los resultados de una jornada
- WHEN se derivan los hechos comentables
- THEN la nota de cada jugador se compara con la mejor de ese día y con cuántos la firman

verified-by:
  - tests/slices/comentarios-de-la-jornada/test_comentarios.py
