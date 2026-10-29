# El nivel de cada jornada se congela una vez

> Slice: `nivel-congelado`.

## Por qué

El nivel se calculaba en el navegador al abrir la pestaña, así que el de ayer podía cambiar durante la
madrugada si llegaba tarde una cuadrícula. Con el ranking por nivel eso mezclaba tiempos de dos escenarios
distintos. El dueño decidió **congelarlo**, a las **04:00 de Madrid** (en 60 días, la cuadrícula más tardía
llegó a las 02:57), generado con **Node y el mismo módulo JS** de la web.

## Qué cambia

1. **`public.game_levels`** (`supabase/migrations/20260925140000_create_game_levels.sql`): una fila por
   jornada, solo lectura para la clave pública, e inmutable para todos por trigger.
2. **`tools/congelar_nivel.mjs`**, ejecutado en cada vuelta de `update_stats.yml` (con `setup-node` 22):
   congela la última jornada asentada con `nivelDe`.
3. **La pestaña** lee el último nivel congelado en lugar de calcularlo.
4. **`registrar_tiempo`** se mide contra el nivel congelado.

## Qué NO cambia

- `nivelDe` y el motor: el mismo nivel, generado en otro sitio.
- `wordle_results` y `season_snapshots`.

## Riesgos declarados

- Entre las 00:00 y la congelación de las 04:00 (más el retraso del cron de GitHub) se juega el nivel de
  anteayer. Es la contrapartida elegida.
- **Node entra en el pipeline**, que era solo Python. Decisión del dueño: una sola implementación del
  generador vale más que un pipeline de un solo lenguaje.
- Si el cron no congela un día, la pestaña sigue en el último congelado; a la mañana siguiente, antes de las
  04:00, el script congela el que faltaba.
