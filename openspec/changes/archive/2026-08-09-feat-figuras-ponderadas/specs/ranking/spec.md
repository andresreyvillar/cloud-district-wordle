# Deltas de `ranking` — feat-figuras-ponderadas

## MODIFIED Requirements

### Requirement: El álbum ordena por puntos por partida, y no todas las figuras valen igual

La puntuación del álbum es la **media de puntos por partida clasificada**, con las figuras valoradas según
lo raras que son:

| Figura | Puntos | Frecuencia medida |
|---|---|---|
| 📐 geométrico | 3 | 7,4% |
| 🦜 loro | 2 | 13,6% |
| 🌷 flores | 1 | 46,5% |
| 🌀 abstracto | 0 | 32,4% |

Antes todas las figuras reconocibles valían lo mismo y la puntuación era la proporción de partidas con
figura. **Decisión del dueño el 2026-08-09.**

Lo que **no** cambia, y es lo que sostiene el criterio: sigue siendo **por partida**. Ese punto se midió al
elegirlo — el total corona a quien más juega, que es un ranking de asistencia con otro nombre.

La escala se queda en 3/2/1 aunque la rareza medida dé una proporción de unos 6:3:1, porque con 5/3/1 el
podio es idéntico: la escala corta se explica igual y se recuerda mejor.

**Coste declarado.** Con todas las figuras valiendo lo mismo, el podio de belleza no compartía a nadie con
el de puntuación — que es la razón de existir de este segundo eje. Ponderando, el segundo clasificado en
puntuación entra en el podio de belleza. Se acepta como decisión del dueño, no porque la medida lo
recomiende.

La escala **se publica en el catálogo** de la instantánea y la vista la anuncia, porque un número como
«1,14» no dice nada sin saber contra qué se mide.

#### Scenario: un geométrico vale más que un loro, y un loro más que una flor
- GIVEN tres jugadores con el mismo número de partidas, uno solo de geométricos, otro solo de loros y otro
  solo de flores
- WHEN se ordena el álbum
- THEN quedan en ese orden

#### Scenario: la puntuación sigue siendo por partida
- GIVEN dos jugadores con la misma mezcla de figuras y uno con diez veces más partidas
- WHEN se calcula su puntuación
- THEN es la misma para los dos

#### Scenario: un abstracto no suma y baja la media
- GIVEN un jugador con una partida abstracta
- WHEN se calcula su puntuación
- THEN esa partida cuenta en el denominador y no aporta puntos

#### Scenario: la escala viaja con los datos
- GIVEN el catálogo de categorías de una instantánea
- WHEN se lee
- THEN cada categoría dice cuántos puntos vale, de modo que la vista no tiene su propia tabla

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py
  - tests/slices/album-de-figuras/album.test.js
