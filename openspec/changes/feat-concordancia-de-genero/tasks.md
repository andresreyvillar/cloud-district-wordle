# Tareas

- [x] Comprobar que no hay dato de género en la tabla y plantear el riesgo de deducirlo del nombre.
- [x] Sacar la lista real de jugadores (23) y separar los claros de los dudosos.
- [x] Preguntar al dueño por los tres dudosos antes de escribir nada.
- [x] `tools/personas.py`: tabla declarada, forma de uno, de varios, y neutro por defecto.
- [x] Cambiar las tres frases de `@` a `{g}` y resolver antes del formateo.
- [x] Escenario nuevo y cuatro tests.
- [x] Atar al camino real el test de huecos, que formateaba las plantillas a mano.
- [x] Gate 4c: cuatro mutaciones, cada una mata su escenario.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage comentarios-de-la-jornada
python3 -m tools.wslice verify gates --slice comentarios-de-la-jornada --change-id feat-concordancia-de-genero
```
