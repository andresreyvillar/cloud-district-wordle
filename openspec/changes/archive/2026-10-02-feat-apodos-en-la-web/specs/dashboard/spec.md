# Deltas de `dashboard` — feat-apodos-en-la-web

## ADDED Requirements

### Requirement: La web nombra con su apodo a quien lo tiene declarado, sin cambiar su identidad

Una tabla declarada (`v2/js/domain/apodos.js`) asigna un apodo de presentación a un nombre de jugador. Toda
vista de la v2 que pinta el nombre de un jugador pinta su apodo si lo tiene, escapado como cualquier nombre;
la etiqueta de su tramo en el SuperWordleBros también, al montar el nivel y sin cambiar el nivel guardado.
La identidad no cambia: rutas de ficha, valor del selector del juego y marcas siguen usando el id de Slack.
El bot de Slack no usa apodos.

#### Scenario: el apodo sustituye al nombre en cada vista
- GIVEN un jugador con apodo declarado que aparece en la temporada, hoy, su ficha, el archivo, los datos y el juego
- WHEN se pinta cada vista
- THEN sale el apodo y no el nombre a secas

#### Scenario: la identidad no cambia
- GIVEN un jugador con apodo
- WHEN se pinta su enlace a la ficha y su opción en el selector del juego
- THEN siguen llevando su id de Slack

#### Scenario: el nivel del juego pinta el apodo
- GIVEN un nivel congelado con la etiqueta «Carrillo  4/6»
- WHEN se prepara para el motor
- THEN la etiqueta lleva el apodo y el nivel original no cambia
