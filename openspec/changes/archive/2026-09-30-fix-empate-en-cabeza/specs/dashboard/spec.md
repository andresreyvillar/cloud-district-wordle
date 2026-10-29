# Deltas de `dashboard` — fix-empate-en-cabeza

## ADDED Requirements

### Requirement: La tarjeta de la temporada presenta el empate como empate

La tarjeta de cada temporada en `/temporadas` nombra a **todos** los que comparten el primer puesto. En curso,
dice «empate en cabeza» en lugar de «va ganando»; cerrada, dice «campeones» y que comparten el primer puesto,
en lugar de coronar al primero de la lista. Con un único primero, la tarjeta no cambia.

#### Scenario: en curso y empatados
- GIVEN una temporada en curso con dos jugadores en el puesto 1
- WHEN se pinta su tarjeta
- THEN dice empate en cabeza y nombra a los dos

#### Scenario: cerrada y empatados
- GIVEN una temporada cerrada con dos jugadores en el puesto 1
- WHEN se pinta su tarjeta
- THEN dice campeones, nombra a los dos y dice que comparten el primer puesto

#### Scenario: un solo primero no cambia
- GIVEN una temporada cerrada con un único primero
- WHEN se pinta su tarjeta
- THEN dice campeón y nombra solo a ese jugador

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js
