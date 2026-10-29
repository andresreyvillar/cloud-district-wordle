# Tareas

- [x] Probar y descartar el cron de Cloudflare escuchando sus logs en la ventana (0 eventos de cron).
- [x] Medir los disparos reales de GitHub y el hueco máximo (5,6 h; mediana 3,6 h).
- [x] Confirmar el techo de 360 min por job y que el `GITHUB_TOKEN` no puede auto-despertar.
- [x] Confirmar que el repositorio es público, así que los minutos son gratis.
- [x] Bucle de sincronización con espera de 55 min y siete vueltas.
- [x] `concurrency` con `cancel-in-progress` para no acumular latidos.
- [x] Probar el bucle en local con esperas de 1 s: éxito, fallo parcial y código de salida.
- [ ] Observar dos días la cadencia real y ajustar las vueltas si hace falta.
- [ ] Pendiente del dueño: el historial de cron-job.org, que sigue sin diagnóstico.

## Comandos de verificación

```bash
python3 -c "import yaml,pathlib; yaml.safe_load(pathlib.Path('.github/workflows/update_stats.yml').read_text())"
gh run list --workflow=update_stats.yml --limit 40 --json createdAt,event
```
