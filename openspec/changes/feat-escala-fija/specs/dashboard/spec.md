# Deltas de `dashboard` — feat-escala-fija

## ADDED Requirements

### Requirement: Dos gráficos del mismo tipo se comparan mirándolos

Las gráficas usan **escalas fijas**, no el máximo de lo que cada una dibuja. Un gráfico autoescalado no
miente en sus números pero sí en lo que sugiere de un vistazo, que es como se leen.

| Gráfico | Escala |
|---|---|
| Dificultad por jornada | 1 a 7 intentos, fija |
| Distribución de intentos | el mayor recuento de la temporada, común a todos sus jugadores |

Y la escala **se anuncia**: una escala fija que no se declara es indistinguible de una automática.

#### Scenario: la dificultad va en la escala de intentos
- GIVEN una jornada con su dificultad
- WHEN se pinta
- THEN su altura sale de la escala fija de 1 a 7, no del máximo del mes

#### Scenario: la misma dificultad se ve igual en dos temporadas
- GIVEN la misma dificultad en dos temporadas distintas
- WHEN se pintan
- THEN tienen la misma altura, y la temporada más fácil no toca el techo

#### Scenario: la distribución comparte escala entre jugadores
- GIVEN dos jugadores de la misma temporada, uno con muchas partidas y otro con pocas
- WHEN se pintan sus distribuciones
- THEN el mismo recuento da la misma altura y quien jugó poco se ve pequeño

#### Scenario: la escala se declara
- GIVEN un gráfico con escala fija
- WHEN se muestra
- THEN dice cuál es su escala

#### Scenario: un valor fuera de escala se recorta
- GIVEN un valor por encima del máximo de la escala
- WHEN se pinta
- THEN se recorta al máximo en lugar de desbordar

#### Scenario: sin datos no se divide por cero
- GIVEN una temporada sin recuentos
- WHEN se calcula la escala
- THEN sigue siendo utilizable y no produce alturas inválidas

verified-by:
  - tests/slices/escala-fija-comparable/escala.test.js
