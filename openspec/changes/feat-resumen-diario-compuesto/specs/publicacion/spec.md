# Deltas de `publicacion` — feat-resumen-diario-compuesto

## ADDED Requirements

### Requirement: El resumen diario cuenta la jornada en texto

El mensaje que el bot publica cada tarde incluye, además de las medallas y el enlace, **cuatro secciones**
derivadas de los datos del día y de la temporada:

1. **Jugador del día** — la mejor puntuación de la jornada, con todos los empatados.
2. **Obra del día** — la figura **más rara de la temporada** entre las dibujadas ese día.
3. **Top 5** del marcador, cada uno con el emoji de lo que dibujó ese día.
4. **Cabeza del álbum** — los tres primeros del ranking de belleza con su tasa y su tira.

Son **dos premios y no uno** por evidencia: exigir mejor puntuación *y* figura reconocible deja el premio
vacío el 94% de las jornadas, porque la figura sale de las partidas que salen mal.

La rareza **se deriva del reparto de la propia temporada**, no de una tabla fija: recalibrar el clasificador
cambia qué figura es rara, y una lista escrita a mano se quedaría atrás.

Ninguna sección se inventa: la que no tiene datos no se imprime. Y el texto **no recalcula nada** — el
marcador y el álbum salen de la misma instantánea que publica la web.

#### Scenario: el jugador del día es la mejor puntuación, y los empates se nombran
- GIVEN una jornada con varios jugadores
- WHEN se compone el resumen
- THEN nombra a quien mejor puntuó, y si empatan los nombra a todos

#### Scenario: la obra del día es la figura más rara del día
- GIVEN una jornada con figuras de distintas categorías
- WHEN se elige la obra del día
- THEN gana la categoría menos frecuente de la temporada, con su autor

#### Scenario: sin figuras el premio queda desierto
- GIVEN una jornada en la que nadie dibujó una figura reconocible
- WHEN se compone el resumen
- THEN la obra del día se declara desierta, sin premiar un abstracto

#### Scenario: el top 5 lleva el dibujo del día
- GIVEN el marcador de la temporada y los resultados del día
- WHEN se compone el top 5
- THEN cada uno lleva el emoji de lo que dibujó ese día, y quien no jugó no lleva ninguno

#### Scenario: la cabeza del álbum aparece con su tira
- GIVEN una temporada con jugadores clasificados en el álbum
- WHEN se compone el resumen
- THEN muestra los tres primeros con su tasa y su tira agrupada

#### Scenario: sin datos no se inventan secciones
- GIVEN una jornada sin resultados o una temporada sin álbum
- WHEN se compone el resumen
- THEN esas secciones no aparecen, y el mensaje sigue siendo válido

#### Scenario: el mensaje cabe en Slack
- GIVEN una temporada con muchos jugadores
- WHEN se compone el resumen
- THEN el texto se mantiene dentro del límite del comentario, recortando listas y no sentido

verified-by:
  - tests/slices/resumen-diario-compuesto/test_resumen.py
