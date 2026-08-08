# Deltas de `estadisticas` — feat-album-de-figuras

## ADDED Requirements

### Requirement: La ficha muestra el álbum de ese jugador

La ficha de un jugador incluye **su** álbum: la tira agrupada de lo que ha dibujado, su tasa de figuras y su
puesto en el ranking de belleza de esa temporada.

Un jugador que no llega al mínimo ve **cuántas partidas le faltan**, no un puesto en blanco: el mínimo es
una regla del juego y decirla convierte "no apareces" en "te faltan dos".

Un jugador sin partidas clasificadas no ve un 0% —que diría que dibujó mal— sino que todavía no tiene álbum.

#### Scenario: la ficha trae la tira, la tasa y el puesto
- GIVEN un jugador clasificado en el álbum de su temporada
- WHEN abre su ficha
- THEN ve su tira agrupada, su tasa de figuras y su puesto

#### Scenario: por debajo del mínimo se dice cuánto falta
- GIVEN un jugador con menos partidas clasificadas que el mínimo
- WHEN abre su ficha
- THEN ve cuántas partidas le faltan para entrar en el ranking

#### Scenario: sin partidas clasificadas no hay un cero
- GIVEN un jugador cuyas partidas de la temporada no tienen patrón
- WHEN abre su ficha
- THEN se le dice que aún no tiene álbum, en lugar de una tasa del 0%

verified-by:
  - tests/slices/album-de-figuras/album.test.js
