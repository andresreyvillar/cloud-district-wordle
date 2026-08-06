# Deltas de `ranking` — feat-archivo-de-temporadas

## ADDED Requirements

### Requirement: El archivo guarda quién ganó cada temporada

Con temporadas mensuales el histórico deja de ser una lista de partidas y pasa a ser un **palmarés
colectivo**. El archivo lista cada temporada materializada con su campeón, su media y sus totales, de la más
reciente a la más antigua.

Una temporada **en curso no tiene campeón**: tiene quien va ganando. Y la temporada 0 va marcada como
**bloque histórico jugado con otras reglas**, para que su media de 181 jornadas sin imputar no se lea como
comparable con la de un mes.

#### Scenario: el archivo ordena de la más reciente a la más antigua
- GIVEN varias temporadas materializadas
- WHEN se abre el archivo
- THEN aparecen ordenadas por número de orden descendente, con la temporada 0 al final

#### Scenario: una temporada cerrada muestra su campeón
- GIVEN una temporada cerrada con clasificación
- WHEN se muestra en el archivo
- THEN muestra a quien la ganó con su media, y sus jornadas, jugadores y resultados

#### Scenario: una temporada en curso no corona a nadie
- GIVEN una temporada cuyo estado es en curso
- WHEN se muestra en el archivo
- THEN aparece marcada como abierta y su primero se presenta como quien va ganando, no como campeón

#### Scenario: la temporada 0 se marca como bloque histórico
- GIVEN la temporada 0
- WHEN se muestra en el archivo
- THEN queda marcada como bloque histórico jugado con otras reglas

#### Scenario: una temporada vacía no desaparece
- GIVEN un mes sin ningún día con muestra suficiente
- WHEN se muestra el archivo
- THEN esa temporada aparece con cero jornadas y sin campeón

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js
