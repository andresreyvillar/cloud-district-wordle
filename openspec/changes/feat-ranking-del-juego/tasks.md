# Tareas — feat-ranking-del-juego

## 1. Migración (`supabase/migrations/20260925120000_create_game_times.sql`)

Tabla `game_times` con RLS de lectura y sin privilegios de escritura para la clave pública; función
`registrar_tiempo` `security definer` con `search_path` vacío, que solo mejora y rechaza lo imposible.

Verificación local: `.venv/bin/python3 -B -m pytest tests/slices/ranking-del-juego` (levanta un Postgres
desechable y le aplica la migración tal cual).

Verificación en producción: cada regla con el rol `anon` dentro de un bloque `do` que termina en excepción, así
que Postgres lo deshace todo; y comprobar después que `game_times` sigue vacía.

## 2. Dominio (`v2/js/domain/superbros.js`)

`jugadoresDelGrupo`, `clasificacionDelNivel` (empates comparten puesto), `tiempoPreciso`.

## 3. Datos (`v2/js/data/results.js`)

`leerMarcas(cliente, jornada)`, `escribirMarca(cliente, marca)` por RPC, `RANKING_DEL_JUEGO`.

## 4. Vista (`v2/js/ui/juego.js`, `v2/css/styles.css`)

`selectorDeJugador`, `rankingDelNivel`, `controlDelRanking`, recordar al jugador, y en `pintarJuego` escuchar
`superbros:fin` en cada partida.

## Cierre

```bash
python3 -m tools.wslice slice validate ranking-del-juego
python3 -m tools.wslice slice coverage ranking-del-juego
python3 -m tools.wslice verify slice ranking-del-juego
python3 -m tools.wslice verify gates --slice ranking-del-juego --change-id feat-ranking-del-juego
node --test tests/slices/ranking-del-juego/
.venv/bin/python3 -B -m pytest tests/slices/ranking-del-juego
```
