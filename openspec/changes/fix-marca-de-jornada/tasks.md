# Tareas

- [x] Diagnosticar el triplicado contra el canal real y ver qué título devuelve Slack.
- [x] Buscar la marca de jornada en lugar del título completo.
- [x] Anclarla para que no coincida por prefijo con jornadas de más cifras.
- [x] Test con el texto literal que devolvió Slack, no construido con `titulo_de`.
- [x] Gate 4c: dos mutaciones matan; la tercera es equivalente en comportamiento y se declara.
- [x] Suite completa, `slice validate`, `verify gates`.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice verify gates --slice captura-apunta-a-la-v2 --change-id fix-marca-de-jornada
```
