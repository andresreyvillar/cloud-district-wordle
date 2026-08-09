# Deltas de `ranking` — feat-desempate-del-album

## MODIFIED Requirements

### Requirement: El álbum deshace sus empates con la tabla de puntuación

Cuando dos jugadores tienen los mismos puntos por partida, el álbum los ordena por su **media en la tabla de
puntuación**: delante quien mejor puntúa. Solo comparten puesto quienes no se distinguen **ni por ahí**.

Antes compartían puesto en cuanto empataban en la puntuación del álbum, y eso producía una tabla sin segundo
ni cuarto puesto. **Decisión del dueño el 2026-08-09.**

El problema no era de redondeo: en una temporada de cinco jornadas jugadas por todo el mundo, los puntos por
partida solo pueden tomar seis valores, así que siete de ocho jugadores empataban — y con **colecciones
idénticas**, las mismas figuras en el mismo número. Ningún criterio sacado del propio álbum podía
separarlos.

Se consideró y **se descartó** premiar a quien publica antes: la marca de tiempo disponible es la de la
escritura del cron, que trabaja por lotes cada hora. Medido sobre el histórico, solo el **34%** de los
resultados de una jornada tienen minuto distinto y en **ninguna** jornada son todos distintos. Ordenar por
ahí premiaría a quien cayó del lado bueno de una hora en punto.

**Precio declarado:** acopla los dos ejes. El álbum existe para premiar a otra gente que el marcador, y
ahora el marcador decide sus empates — pero solo cuando el criterio propio ya no distingue.

#### Scenario: dos con los mismos puntos por partida se ordenan por el marcador
- GIVEN dos jugadores con colecciones idénticas y distinta media de puntuación
- WHEN se ordena el álbum
- THEN va delante quien mejor puntúa, y ocupan puestos distintos

#### Scenario: sin nada que los separe, siguen compartiendo puesto
- GIVEN dos jugadores idénticos también en la tabla de puntuación
- WHEN se ordena el álbum
- THEN comparten puesto

#### Scenario: el desempate no altera el criterio principal
- GIVEN un jugador con más puntos por partida y peor media de puntuación que otro
- WHEN se ordena el álbum
- THEN va delante el de más puntos por partida

verified-by:
  - tests/slices/clasificacion-de-figuras/test_album.py
