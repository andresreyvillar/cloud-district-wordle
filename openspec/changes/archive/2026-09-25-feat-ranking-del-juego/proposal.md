# Terminar el nivel deja tu tiempo en el ranking de esa jornada

> Slice: `ranking-del-juego`.

## Por qué

SuperWordleBros ya se juega y se comparte copiando el texto al canal, pero comparar tiempos exige leer el
hilo. El dueño pidió que cada uno elija su nombre de la lista de jugadores, que su tiempo quede en un ranking
debajo del juego, que se pueda reintentar sin límite y que **solo se sobrescriba la marca si se mejora**.

Decisiones tomadas con el dueño: **un ranking por nivel** (por jornada: cada día el escenario es otro) y la
verificación en producción **dentro de transacciones que se deshacen**.

## Qué cambia

1. **Tabla aditiva `public.game_times`** (`supabase/migrations/20260925120000_create_game_times.sql`): una
   fila por `(jornada, jugador)` con la mejor marca. La clave pública solo la lee.
2. **Función `public.registrar_tiempo`**: la única vía de escritura. Solo sustituye si mejora y rechaza lo
   imposible (jugador desconocido, jornada sin nivel, estrellas de más, tiempo por debajo de lo que permite la
   física del motor).
3. **La pestaña** (`v2/js/ui/juego.js`): «¿Quién eres?» recordado por navegador, envío en cada llegada a la
   meta —con la partida en espera si aún no hay nombre— y el ranking del nivel debajo del juego.
4. **La capa de datos** (`v2/js/data/results.js`): `leerMarcas`, `escribirMarca` y la API real.

## Qué NO cambia

- Nada de `wordle_results` ni `season_snapshots`; nada del pipeline ni de Slack.
- El motor de Joel: el ranking consume el `superbros:fin` que ya dispara.
- El texto para compartir: sigue en `m:ss`; el ranking usa centésimas.

## Riesgos declarados

- **Suplantación.** Sin login, cualquiera puede registrar a nombre de otro. Es el modelo de confianza del
  grupo; lo que se impide es escribir en la tabla directamente, borrar marcas y los tiempos imposibles.
- **El mínimo depende de la física del motor** (`RUN_SPEED = 300`). Con el 50 % de margen, un PR de Joel que
  suba la velocidad hasta 450 px/s sigue sin rechazar tiempos honrados; más allá, hay que tocar la función.
- El linter de Supabase avisa de que `anon` ejecuta una función `security definer`
  (`0028`/`0029`): es intencionado, y está acotada por `search_path` vacío y por sus validaciones.
