# Tareas

- [x] Comprobar que la web ya tiene podio y URL por temporada cerrada, para no dibujar uno nuevo.
- [x] `temporada_que_cierra` derivada de los datos, con la temporada 0 y los saltos de mes fuera.
- [x] `podio_de` cortando por puesto y no por filas, para no partir empates.
- [x] Felicitación con las medallas del mes; con empate arriba, a todos y sin medallas de uno solo.
- [x] Objetivo de captura del podio, reutilizando la maquinaria existente.
- [x] Workflow nuevo del 1 al 7, con la condición en el código y no en el cron.
- [x] Guarda de idempotencia con la marca del mes, no el título entero.
- [x] Slice con 8 escenarios y 11 tests, sin red.
- [x] Gate 4c: seis mutaciones, cada una mata su escenario.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage podio-de-cierre-de-mes
python3 -m tools.wslice verify gates --slice podio-de-cierre-de-mes --change-id feat-podio-de-cierre-de-mes
```
