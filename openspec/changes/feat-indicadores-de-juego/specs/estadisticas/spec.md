# Deltas de `estadisticas` — feat-indicadores-de-juego

## ADDED Requirements

### Requirement: Los indicadores de juego salen de las cuadrículas, sin publicar palabras

Para cada partida con cuadrícula se estiman las candidatas —soluciones aún posibles— antes de cada intento, con
el coloreado del juego (sin tildes, con Ñ) y la lista de soluciones hasta la última jornada jugada. De ahí salen,
por jugador y temporada: la media frente al grupo y al solucionador de referencia, la mediana de candidatas tras el
primer y el segundo intento, la suerte (Σ acierto − 1/candidatas por intento) y la partida resuelta con más
candidatas. El cálculo es determinista y la instantánea no contiene palabras.

#### Scenario: acertar con una sola candidata no es suerte
- GIVEN una partida cuyo intento ganador llega con una candidata
- WHEN se calcula su suerte
- THEN ese intento suma cero

#### Scenario: la instantánea no lleva palabras
- GIVEN una temporada materializada con la lista de soluciones
- WHEN se serializa la instantánea
- THEN no contiene ninguna palabra de la lista

verified-by:
  - tests/slices/indicadores-de-juego/test_indicadores.py
