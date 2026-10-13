# Tareas — fix-podio-historial-por-fecha

1. `tools/post_ranking.py`: `mensajes_recientes(desde=...)`.
2. `tools/post_podium.py`: `desde_de_la_comprobacion` y su uso en `celebrar`.
3. `.github/workflows/post_podium.yml`: cron `0 9 1-3 * *`.

```bash
.venv/bin/python3 -B -m pytest tests/slices/podio-de-cierre-de-mes
```
