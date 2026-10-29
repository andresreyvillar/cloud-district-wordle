# Deltas de `dashboard` — feat-ficha-de-jugador

## ADDED Requirements

### Requirement: El marcador es la puerta de entrada a la ficha de cada jugador

La clasificación lista a todos los jugadores de la temporada y cada uno **enlaza a su ficha de esa misma
temporada**. Sin ese enlace la ficha existe y nadie la encuentra.

La ruta lleva la temporada, así que el enlace que alguien pega en el canal sigue hablando del mes del que
hablaba, y no del mes en que se abre.

#### Scenario: cada fila del marcador enlaza a la ficha
- GIVEN una temporada con clasificación
- WHEN se pinta el marcador
- THEN cada jugador enlaza a su ficha de esa temporada, con su identificador de Slack en la ruta

#### Scenario: un jugador sin resultados en la temporada lo dice
- GIVEN un identificador de jugador que no tiene resultados en la temporada abierta
- WHEN se abre su ficha
- THEN la vista lo declara y ofrece las temporadas en que sí jugó, en lugar de una página vacía

#### Scenario: un identificador desconocido no rompe la vista
- GIVEN un identificador que no aparece en ninguna temporada
- WHEN se abre su ficha
- THEN la vista lo declara sin fallar, porque con el fallback SPA cualquier ruta responde 200

verified-by:
  - tests/slices/ficha-de-jugador/ficha.test.js
