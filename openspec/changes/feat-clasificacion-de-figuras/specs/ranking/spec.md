# Deltas de `ranking` — feat-clasificacion-de-figuras

## ADDED Requirements

### Requirement: El álbum ordena por tasa de figuras, no por volumen

Cada temporada publica un segundo ranking, **independiente del de puntuación**: el álbum de figuras. La
puntuación de un jugador es la **proporción de sus partidas clasificadas que dejaron una figura
reconocible** (loro, flores o geométrico), no el recuento absoluto.

Medido sobre la temporada 0: el recuento absoluto corona a quien más juega y el ponderado por rareza corona
al segundo de la tabla de puntuación, que es justo lo que este eje existe para evitar.

Hace falta un **mínimo de 5 partidas clasificadas** para tener puesto. Con 3, el líder es alguien con un
100% de tres partidas; con 5, 8 o 10 el líder es el mismo. Quien no llega al mínimo aparece igual, sin
puesto.

El orden es determinista: tasa descendente, a igualdad más figuras delante, y a igualdad de figuras por
nombre.

#### Scenario: la tasa mide figuras por partida
- GIVEN un jugador con partidas clasificadas
- WHEN se calcula su puntuación del álbum
- THEN es la proporción de esas partidas con figura reconocible, y jugar más no la sube por sí solo

#### Scenario: un abstracto rebaja la tasa
- GIVEN un jugador con una partida abstracta
- WHEN se calcula su álbum
- THEN la partida aparece en su recuento y le baja la tasa, en lugar de desaparecer

#### Scenario: por debajo del mínimo no hay puesto
- GIVEN un jugador con menos partidas clasificadas que el mínimo
- WHEN se ordena el álbum
- THEN aparece sin puesto y no encabeza el ranking, aunque su tasa sea la más alta

#### Scenario: el empate se rompe siempre igual
- GIVEN dos jugadores con la misma tasa
- WHEN se ordena el álbum
- THEN va delante quien aportó más figuras, y a igualdad el orden es por nombre

#### Scenario: sin patrones no hay ranking
- GIVEN una temporada en la que ninguna partida tiene patrón
- WHEN se calcula el álbum
- THEN sale vacío y declarado como tal, sin campeón de belleza

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py
