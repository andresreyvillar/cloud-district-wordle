# Deltas de `resultados` — feat-ranking-del-juego

## ADDED Requirements

### Requirement: Las marcas del juego viven en una tabla aditiva que la clave pública solo lee

`public.game_times` guarda **una fila por `(jornada, jugador)`** con la mejor marca: `segundos` (centésimas),
`estrellas` y `updated_at`. Es **aditiva** (ADR 0005): no cambia `wordle_results` ni `season_snapshots`.

Con la clave pública, la tabla **solo se lee**: RLS con política de lectura y sin privilegios de escritura para
`anon` ni `authenticated`. La única vía de escritura es la función `registrar_tiempo`.

#### Scenario: la clave pública no escribe en la tabla
- GIVEN los roles `anon` y `authenticated`
- WHEN intentan insertar, cambiar, borrar o vaciar filas de `game_times`
- THEN Postgres lo rechaza y las marcas siguen intactas

#### Scenario: la clave pública sí la lee
- GIVEN una marca registrada
- WHEN `anon` lee la tabla
- THEN la ve

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260925120000_create_game_times.sql
    pattern: 'revoke insert, update, delete, truncate on public\.game_times from anon, authenticated;'
    describe: la clave pública no tiene privilegios de escritura sobre la tabla
  - type: regex
    file: supabase/migrations/20260925120000_create_game_times.sql
    pattern: 'alter table public\.game_times enable row level security;'
    describe: la tabla tiene RLS
```

verified-by:
  - tests/slices/ranking-del-juego/test_registrar_tiempo.py


### Requirement: `registrar_tiempo` solo sobrescribe una marca si la mejora, y rechaza lo imposible

`public.registrar_tiempo(p_jornada, p_jugador, p_segundos, p_estrellas)` es `security definer` con
`search_path` vacío y la ejecutan `anon` y `authenticated`. Inserta la marca, o la sustituye **solo si el tiempo
nuevo es menor**; un tiempo igual o peor deja la anterior. Devuelve `{ mejora, segundos }` con la marca que se
queda.

Rechaza, sin escribir nada: un jugador que no aparece en `wordle_results`; una jornada sin nadie con
cuadrícula; estrellas negativas o por encima del número de tramos; y un tiempo por debajo de
`tramos × 8 × 32 ÷ (300 × 1,5)` segundos —recorrer el nivel a la velocidad máxima del motor, con un 50 % de
margen— o de una hora o más.

No hay autenticación: cualquiera puede registrar a nombre de cualquiera. Es el modelo de confianza declarado
del grupo, no un descuido.

#### Scenario: la primera marca se guarda con centésimas
- GIVEN un jugador sin marca en un nivel
- WHEN `anon` llama a `registrar_tiempo`
- THEN se guarda redondeada a centésimas y devuelve `mejora: true`

#### Scenario: un tiempo igual o peor no pisa la marca
- GIVEN una marca de 40 s
- WHEN se registra 40 s o 55 s
- THEN la marca sigue en 40 s con sus estrellas y devuelve `mejora: false`

#### Scenario: un tiempo mejor la sustituye
- GIVEN una marca de 40 s
- WHEN se registra 31,5 s
- THEN la marca pasa a 31,5 s con las estrellas nuevas

#### Scenario: lo imposible se rechaza
- GIVEN un jugador desconocido, una jornada sin nivel, estrellas de más o un tiempo por debajo del mínimo
- WHEN se llama a `registrar_tiempo`
- THEN falla con el motivo y la tabla no cambia

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260925120000_create_game_times.sql
    pattern: "security definer\\s+set search_path = ''"
    describe: la función privilegiada no hereda el search_path de quien la llama
  - type: regex
    file: supabase/migrations/20260925120000_create_game_times.sql
    pattern: 'where excluded\.segundos < actual\.segundos;'
    describe: solo se sustituye una marca por un tiempo estrictamente menor
```

verified-by:
  - tests/slices/ranking-del-juego/test_registrar_tiempo.py
