# Deltas de `ranking` — fix-empate-en-cabeza

## ADDED Requirements

### Requirement: Un primer puesto compartido tiene varios líderes y varios campeones

Cuando varios jugadores comparten el primer puesto de una temporada —misma media publicada, que es cuando la
clasificación les da el mismo puesto—, **todos** son quienes van ganando mientras está en curso y **todos** son
campeones cuando se cierra. El archivo de temporadas trae `lideres` y `campeones` como listas con todos los del
primer puesto, y el medallero suma la temporada ganada a cada campeón. `lider` y `campeon` se conservan como el
primero de esas listas, para quien solo necesite uno.

#### Scenario: un empate en cabeza da dos líderes
- GIVEN una temporada en curso con dos jugadores en el puesto 1
- WHEN se construye el archivo
- THEN `lideres` tiene a los dos

#### Scenario: un título compartido da dos campeones
- GIVEN una temporada cerrada con dos jugadores en el puesto 1
- WHEN se construyen el archivo y el medallero
- THEN `campeones` tiene a los dos, y cada uno suma una temporada ganada

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js
