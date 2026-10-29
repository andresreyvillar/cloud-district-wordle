# Deltas de `resultados` — feat-juego-en-la-temporada

## ADDED Requirements

### Requirement: Un nivel admite marcas solo mientras es el último congelado

`registrar_tiempo` acepta marcas únicamente para **la última jornada congelada** en `game_levels`. Una jornada
congelada anterior se rechaza con «ese nivel ya está cerrado», sin escribir nada. Así el ranking de un nivel
deja de cambiar en cuanto se congela el siguiente, y la clasificación del mes del juego no se reescribe hacia
atrás. El resto de validaciones —jugador, estrellas, tiempo mínimo, solo si mejora— no cambia.

La migración es aditiva: reemplaza la función con la misma firma y los mismos permisos.

#### Scenario: el nivel anterior está cerrado
- GIVEN dos niveles congelados, las jornadas N y N+1
- WHEN se registra un tiempo para la jornada N
- THEN falla con «ese nivel ya está cerrado» y `game_times` no cambia

#### Scenario: el último nivel sigue abierto
- GIVEN los mismos dos niveles
- WHEN se registra un tiempo para la jornada N+1
- THEN se guarda como siempre

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql
    pattern: 'if p_jornada <> \(select max\(l.jornada\) from public.game_levels l\) then'
    describe: solo el último nivel congelado admite marcas
```

verified-by:
  - tests/slices/ranking-del-juego/test_registrar_tiempo.py


### Requirement: La materialización lee los niveles y las marcas del juego

`materialize_seasons.py` lee `game_levels` (jornada, fecha) y `game_times` (jornada, jugador, segundos,
estrellas) con la clave de servicio, paginando como con `wordle_results`, y se los pasa a la función de la
clasificación del juego. No escribe en esas tablas.

#### Scenario: las marcas llegan a la instantánea
- GIVEN niveles y marcas en la base de datos
- WHEN se materializa una temporada
- THEN la instantánea trae la clasificación del juego calculada con ellos

```yaml
checks:
  - type: regex
    file: tools/materialize_seasons.py
    pattern: 'niveles, marcas = leer_juego\(create_client\(URL, KEY\)\)'
    describe: el cron lee niveles y marcas antes de materializar
```

verified-by:
  - tests/slices/clasificacion-del-juego/test_clasificacion_del_juego.py


### Requirement: Una marca mejora con más estrellas, o con las mismas en menos tiempo

Las estrellas pesan más que el tiempo (decisión del dueño). `registrar_tiempo` sustituye la marca de un jugador
en un nivel solo si la nueva tiene **más estrellas**, o **las mismas estrellas en menos tiempo**. Con menos
estrellas no la sustituye aunque sea más rápida, y con las mismas estrellas y el mismo tiempo tampoco. Devuelve
`{ mejora, segundos, estrellas }` con la marca que se queda.

#### Scenario: más estrellas mejora aunque sea más lento
- GIVEN una marca de 9 estrellas en 12 s
- WHEN se registran 13 estrellas en 15 s
- THEN la marca pasa a 13 estrellas y 15 s

#### Scenario: menos estrellas no mejora aunque sea más rápido
- GIVEN una marca de 13 estrellas en 15 s
- WHEN se registran 9 estrellas en 12 s
- THEN la marca sigue en 13 estrellas y 15 s

#### Scenario: con las mismas estrellas, gana el tiempo
- GIVEN una marca de 5 estrellas en 40 s
- WHEN se registran 5 estrellas en 31,5 s, y después 5 en 40 s
- THEN la marca pasa a 31,5 s y la segunda no la cambia

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260930120000_close_levels_and_rank_by_stars.sql
    pattern: 'where excluded.estrellas > actual.estrellas\s+or \(excluded.estrellas = actual.estrellas and excluded.segundos < actual.segundos\);'
    describe: la regla de mejora pone las estrellas por delante
```

verified-by:
  - tests/slices/ranking-del-juego/test_registrar_tiempo.py
