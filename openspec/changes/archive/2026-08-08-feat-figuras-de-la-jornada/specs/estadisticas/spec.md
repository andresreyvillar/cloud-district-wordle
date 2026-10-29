# Deltas de `estadisticas` — feat-figuras-de-la-jornada

## ADDED Requirements

### Requirement: La instantánea publica las figuras de la última jornada

Además del álbum agregado, la instantánea de una temporada publica **la figura de cada resultado de su
jornada más reciente**: el número de jornada y, por jugador, la categoría que dibujó.

Se calcula sobre **todos los resultados de la temporada, cuenten o no sus días**. El álbum agregado solo
cuenta lo que puntúa; esta clave responde otra pregunta —qué se ha dibujado hoy— y una jornada abierta
todavía no alcanza la muestra mínima a media mañana.

Se publica **una sola jornada**, no el histórico: acotarlo es lo que permite que la vista de hoy tenga el
dato sin engordar la instantánea con miles de entradas que nadie lee.

Un resultado sin cuadrícula no aparece: no se le inventa categoría.

#### Scenario: la jornada más reciente trae sus figuras
- GIVEN una temporada con resultados en varias jornadas
- WHEN se materializa
- THEN publica el número de la jornada más reciente y la figura de cada jugador que dibujó ese día

#### Scenario: una jornada que aún no cuenta también publica sus figuras
- GIVEN una jornada con menos jugadores de los que hacen falta para que cuente
- WHEN se materializa la temporada
- THEN sus figuras se publican igual

#### Scenario: sin cuadrícula no hay entrada
- GIVEN un resultado de esa jornada sin patrón
- WHEN se materializa
- THEN ese jugador no aparece en las figuras de la jornada

#### Scenario: una temporada sin resultados no publica jornada
- GIVEN una temporada sin ningún resultado
- WHEN se materializa
- THEN la clave existe pero sin jornada ni figuras, y nada la da por buena

verified-by:
  - tests/slices/figuras-de-la-jornada/test_ultima_jornada.py
