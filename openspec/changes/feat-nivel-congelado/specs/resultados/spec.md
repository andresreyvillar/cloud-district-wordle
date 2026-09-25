# Deltas de `resultados` — feat-nivel-congelado

## ADDED Requirements

### Requirement: Los niveles congelados viven en una tabla aditiva que nadie puede cambiar

`public.game_levels` guarda una fila por jornada: `jornada` (clave), `fecha`, `nivel` (el objeto de `nivelDe`
tal cual, en `jsonb`) y `frozen_at`. Es **aditiva** (ADR 0005).

La clave pública solo la lee. La escribe el cron con la clave de servicio. Y **nadie la cambia**: un trigger
rechaza cualquier `update`, `delete` o `truncate`, también con la clave de servicio y como superusuario.
Arreglar un nivel a mano exige quitar el trigger a propósito.

#### Scenario: un nivel congelado no se cambia
- GIVEN un nivel congelado
- WHEN la clave de servicio o el superusuario intentan cambiarlo, borrarlo o vaciar la tabla
- THEN Postgres lo rechaza con «un nivel congelado no se cambia» y el nivel sigue igual

#### Scenario: la clave pública solo lee
- GIVEN los roles `anon` y `authenticated`
- WHEN intentan congelar o cambiar un nivel
- THEN Postgres lo rechaza; leerlos sí pueden

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260925140000_create_game_levels.sql
    pattern: 'before update or delete on public\.game_levels'
    describe: el trigger que hace inmutable el nivel congelado
  - type: regex
    file: supabase/migrations/20260925140000_create_game_levels.sql
    pattern: 'before truncate on public\.game_levels'
    describe: tampoco se puede vaciar la tabla
  - type: regex
    file: supabase/migrations/20260925140000_create_game_levels.sql
    pattern: 'revoke insert, update, delete, truncate on public\.game_levels from anon, authenticated;'
    describe: la clave pública no escribe
```

verified-by:
  - tests/slices/nivel-congelado/test_game_levels.py


### Requirement: `registrar_tiempo` se mide contra el nivel congelado

`registrar_tiempo` (misma firma y permisos) solo acepta jornadas **con nivel congelado**. El mínimo de tiempo
sale de los tramos de ese nivel —una etiqueta por tramo— y el máximo de estrellas, de sus coleccionables. Una
jornada con cuadrículas en `wordle_results` pero sin congelar se rechaza como «esa jornada no tiene nivel».

#### Scenario: una jornada sin congelar no admite marcas
- GIVEN una jornada con cuadrículas pero sin nivel congelado
- WHEN se registra un tiempo
- THEN se rechaza

#### Scenario: las estrellas se acotan a los coleccionables del nivel
- GIVEN un nivel de 2 tramos y 1 coleccionable
- WHEN se registran 2 estrellas
- THEN se rechaza; con 1, se acepta

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260925140000_create_game_levels.sql
    pattern: "select l\\.nivel into nivel from public\\.game_levels l where l\\.jornada = p_jornada;"
    describe: la función lee el nivel congelado de la jornada
  - type: regex
    file: supabase/migrations/20260925140000_create_game_levels.sql
    pattern: "coleccionables := coalesce\\(jsonb_array_length\\(nivel -> 'collectibles'\\), 0\\);"
    describe: el máximo de estrellas sale de los coleccionables del nivel
```

verified-by:
  - tests/slices/nivel-congelado/test_game_levels.py
