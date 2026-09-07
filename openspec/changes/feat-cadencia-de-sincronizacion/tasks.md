# Tareas

- [x] Buscar si hay una forma más simple y robusta; no la hay más allá del disparador externo, ya fallido.
- [x] Auditar el histórico con el criterio nuevo para tener el suelo (119 en 15 días, hueco máx 15,7 h).
- [x] `tools/cadencia.py`: el criterio como función pura, con el instante por parámetro.
- [x] Tres ventanas por hora en el workflow, complementando el latido ya desplegado.
- [x] Slice con 4 escenarios y 9 tests.
- [x] Arreglar los dos huecos que los tests destaparon: silencios en los bordes y veredicto sin datos.
- [x] Gate 4c: mutaciones sobre el criterio.
- [ ] Auditar de nuevo en dos días y ajustar las ventanas o las vueltas según el resultado.
- [ ] Pendiente del dueño: el historial de cron-job.org, que sigue sin diagnóstico.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest tests/slices/cadencia-de-sincronizacion/ -q
python3 -m tools.wslice slice coverage cadencia-de-sincronizacion
gh run list --workflow=update_stats.yml --limit 120 --json createdAt,conclusion
```
