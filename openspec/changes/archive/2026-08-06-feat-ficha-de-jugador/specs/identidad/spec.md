# Deltas de `identidad` — feat-ficha-de-jugador

## ADDED Requirements

### Requirement: El palmarés de un jugador se sigue por identidad, no por nombre

El palmarés cruza todas las temporadas de un jugador **por su identificador de Slack**. Es lo que hace que
un renombre no le parta el historial en dos: es el mismo fallo que ya se corrigió en los resultados
([ADR 0006](../../../decisions/0006-estructura-de-informacion-v2.md)), y aquí volvería a aparecer si el
cruce fuera por nombre.

El nombre solo se usa para mostrarlo, y se toma de la temporada que se esté mirando: así una ficha antigua
enseña el nombre con el que se jugó.

#### Scenario: el palmarés recorre las temporadas del jugador
- GIVEN un jugador con resultados en varias temporadas
- WHEN se mira su palmarés
- THEN aparece una línea por temporada con su puesto y su media, de la más reciente a la más antigua, y la
  temporada abierta queda señalada

#### Scenario: el palmarés omite las temporadas que no jugó
- GIVEN un jugador que no jugó una de las temporadas materializadas
- WHEN se mira su palmarés
- THEN esa temporada no aparece

#### Scenario: sin nombre conocido se muestra el identificador
- GIVEN un identificador sin resultados en ninguna temporada
- WHEN se abre su ficha
- THEN se muestra el identificador, porque inventar un nombre sería peor que no tenerlo

verified-by:
  - tests/slices/ficha-de-jugador/ficha.test.js
