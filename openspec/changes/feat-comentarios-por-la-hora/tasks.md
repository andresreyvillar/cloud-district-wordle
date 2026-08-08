# Tasks — feat-comentarios-por-la-hora

- [x] **Frecuencias medidas antes de fijar nada**, sobre 186 jornadas: clavada 0,01 · rezagado-con-suerte
      0,06 · rezagado 0,24 con 4h de hueco (0,31 con 3h).
- [x] Comprobado que `created_at` sirve como hora de publicación: 60 minutos distintos y un reparto por
      horas con forma humana (pico de 07 a 11 UTC, cola hasta la noche). **Salvo 268 filas del backfill**,
      insertadas todas el 2026-02-02, que se excluyen solas porque su fecha no coincide con la del puzzle.
- [x] Tres hechos nuevos · 5 tests · cobertura 10/10 escenarios del slice.
- [x] `post_ranking` lee también `created_at`.
- [x] **Gate 4c — 4 mutantes sobre este pack, 0 supervivientes:** sin muestra suficiente, hora del backfill,
      llegar tarde y clavarla como simple retraso, y la clavada nunca detectada.

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/comentarios-de-la-jornada/
python3 -m tools.wslice verify gates --slice comentarios-de-la-jornada --change-id feat-comentarios-por-la-hora
RESUMEN_COMPUESTO=1 python3 tools/local_stack.py --seco --sin-web
```
