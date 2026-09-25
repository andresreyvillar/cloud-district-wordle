# Tareas — feat-nivel-congelado

## 1. Migración (`supabase/migrations/20260925140000_create_game_levels.sql`)

`game_levels` con RLS de lectura, sin escritura pública y con trigger de inmutabilidad; `registrar_tiempo`
reemplazada para medir contra el nivel congelado.

Verificación local: `.venv/bin/python3 -B -m pytest tests/slices/nivel-congelado tests/slices/ranking-del-juego`
(Postgres desechable con todas las migraciones, `tests/postgres_local.py`).

## 2. Dominio (`v2/js/domain/superbros.js`)

`HORA_DE_CONGELAR` y `jornadaACongelar(resultados, hoy, hora)`, pura.

## 3. Script (`tools/congelar_nivel.mjs`) y workflow

`congelar({ fetch, url, clave, hoy, hora, seco, log })` y el borde `ahoraEnMadrid`. En `update_stats.yml`,
`setup-node` 22 y el script tras `materialize_seasons.py`.

## 4. Web (`v2/js/data/results.js`, `v2/js/ui/juego.js`)

`leerNivelCongelado`, `NIVEL_CONGELADO`, `nivelParaJugar`, y `pintarJuego` asíncrona.

## Cierre

```bash
python3 -m tools.wslice slice validate nivel-congelado
python3 -m tools.wslice slice coverage nivel-congelado
python3 -m tools.wslice verify gates --slice nivel-congelado --change-id feat-nivel-congelado
node --test tests/slices/nivel-congelado/
.venv/bin/python3 -B -m pytest tests/slices/nivel-congelado
```
