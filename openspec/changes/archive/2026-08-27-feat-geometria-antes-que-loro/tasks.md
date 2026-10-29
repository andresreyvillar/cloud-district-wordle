# Tareas

- [x] Medir qué mueve el reorden antes de aplicarlo (42 de 1.706, todas loro → geométrico).
- [x] `PRIMERA_JORNADA_GEOMETRIA_PRIMERO` y `geometria_primero(jornada)`.
- [x] `figura(patron, jornada)` con las dos ramas de orden.
- [x] Pasar la jornada en los cinco llamadores de producción.
- [x] Dos escenarios nuevos con sus tests, incluido el fixture ambiguo que hace que el orden importe.
- [x] Verificar contra producción que **ninguna** cuadrícula del histórico cambia.
- [x] Gate 4c: cuatro mutaciones, cada una mata su escenario.
- [x] Suite completa, `slice coverage`, `slice validate`, `verify gates`.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage clasificacion-de-figuras
python3 -m tools.wslice verify gates --slice clasificacion-de-figuras --change-id feat-geometria-antes-que-loro
```
