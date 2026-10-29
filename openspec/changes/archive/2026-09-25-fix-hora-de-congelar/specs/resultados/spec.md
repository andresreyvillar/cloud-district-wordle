# Deltas de `resultados` — fix-hora-de-congelar

## MODIFIED Requirements

### Requirement: Los niveles congelados viven en una tabla aditiva que nadie puede cambiar

`public.game_levels` guarda una fila por jornada: `jornada` (clave), `fecha`, `nivel` (el objeto de `nivelDe`
tal cual, en `jsonb`) y `frozen_at`. Es **aditiva** (ADR 0005). La fila de una jornada aparece **a partir de
las 02:00 de Madrid del día siguiente** (antes, de las 04:00), en la primera vuelta del cron desde esa hora.

La clave pública solo la lee. La escribe el cron con la clave de servicio. Y **nadie la cambia**: un trigger
rechaza cualquier `update`, `delete` o `truncate`, también con la clave de servicio y como superusuario.
Arreglar un nivel a mano exige quitar el trigger a propósito.

#### Scenario: la fila de ayer aparece desde las 02:00
- GIVEN el día D a las 02:00 de Madrid o después
- WHEN corre el cron
- THEN `game_levels` tiene la fila de la jornada de D-1

#### Scenario: un nivel congelado no se cambia
- GIVEN un nivel congelado
- WHEN la clave de servicio o el superusuario intentan cambiarlo, borrarlo o vaciar la tabla
- THEN Postgres lo rechaza con «un nivel congelado no se cambia» y el nivel sigue igual

```yaml
checks:
  - type: regex
    file: supabase/migrations/20260925140000_create_game_levels.sql
    pattern: 'before update or delete on public\.game_levels'
    describe: el trigger que hace inmutable el nivel congelado
```

verified-by:
  - tests/slices/nivel-congelado/congelar.test.js
  - tests/slices/nivel-congelado/test_game_levels.py
