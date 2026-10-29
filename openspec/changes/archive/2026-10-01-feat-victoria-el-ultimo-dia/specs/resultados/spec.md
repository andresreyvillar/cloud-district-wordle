# Deltas de `resultados` — feat-victoria-el-ultimo-dia

## MODIFIED Requirements

### Requirement: La materialización lee los niveles y las marcas del juego

`materialize_seasons.py` lee `game_levels` (jornada, fecha) y `game_times` (jornada, jugador, segundos,
estrellas) con la clave de servicio, paginando como con `wordle_results`, y se los pasa a la función de la
clasificación del juego. No escribe en esas tablas. La **fecha** de cada nivel decide en qué mes puntúa: el de
su jornada, o el siguiente si es el último día laborable del mes. El publicador lee los mismos datos para la
victoria del último día.

#### Scenario: la fecha del nivel decide su mes
- GIVEN un nivel con fecha del último día laborable de un mes
- WHEN se materializan ese mes y el siguiente
- THEN el nivel puntúa en el siguiente

verified-by:
  - tests/slices/clasificacion-del-juego/test_clasificacion_del_juego.py
