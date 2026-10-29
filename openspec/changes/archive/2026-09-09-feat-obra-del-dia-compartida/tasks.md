# Tareas

- [x] Explicar el desempate existente y detectar que el nombre decidía en los empates.
- [x] Medir cuántas jornadas tendrían obra compartida (52 de 204, 25%).
- [x] `_obra_del_dia` devuelve a todos los empatados, ordenados por nombre.
- [x] Adaptar los dos consumidores: el bloque suelto y la viñeta de la jornada.
- [x] Registros en plural para el dibujo genérico y para el melocotón.
- [x] Escenario nuevo y tres tests, incluido el caso de un solo ganador.
- [x] Gate 4c: cuatro mutaciones, cada una mata su escenario.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage resumen-diario-compuesto
python3 -m tools.wslice verify gates --slice resumen-diario-compuesto --change-id feat-obra-del-dia-compartida
```
