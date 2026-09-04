# Tareas

- [x] Localizar los dos mensajes en el canal y la posición del original (44).
- [x] Medir el volumen diario del canal para dimensionar la ventana (17/día, ~120 en siete días).
- [x] Paginar en `mensajes_recientes` con el cursor de Slack.
- [x] Pedir cinco páginas desde el cierre de mes; dejar una en el resumen diario.
- [x] Escenario nuevo y dos tests: uno del flujo con la marca fuera de la primera página, otro del lector real.
- [x] Gate 4c: tres mutaciones, cada una mata su escenario.
- [ ] Decisión del dueño: si borrar el mensaje duplicado del canal.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage podio-de-cierre-de-mes
python3 -m tools.wslice verify gates --slice podio-de-cierre-de-mes --change-id fix-historial-del-podio
```
