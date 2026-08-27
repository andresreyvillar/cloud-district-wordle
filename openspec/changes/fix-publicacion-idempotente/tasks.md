# Tareas

- [x] Medir los descartes del planificador por día y el retraso real de las ejecuciones.
- [x] Marcar el título de la captura con la jornada (`titulo_de`).
- [x] `ya_publicada(mensajes, jornada)` como función pura, y la guarda **antes** de la captura.
- [x] `mensajes_recientes` con cliente inyectable y repliegue a vacío ante fallo de Slack.
- [x] Tres ventanas para el resumen y minuto 23 para el horario, fuera del `:00`.
- [x] Dos escenarios nuevos en `captura-apunta-a-la-v2` con sus tests.
- [x] Gate 4c: cinco mutaciones, cada una mata su escenario.
- [x] Suite completa, `slice coverage` 10/10, `slice validate`, `verify gates`.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage captura-apunta-a-la-v2
python3 -m tools.wslice slice validate
python3 -m tools.wslice verify gates --slice captura-apunta-a-la-v2 --change-id fix-publicacion-idempotente
```
