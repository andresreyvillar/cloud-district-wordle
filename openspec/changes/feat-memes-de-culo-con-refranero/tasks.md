# Tareas

- [x] Buscar expresiones hechas reales con la palabra, con su significado.
- [x] Reescribir las 25 frases del registro sobre esas expresiones, cada una con su sentido.
- [x] Actualizar la lista de marcas del test con las expresiones nuevas.
- [x] Test de que la mayoría se apoya en una expresión y que ninguna se repite más de dos veces.
- [x] Gate 4c: dos mutaciones, cada una mata su escenario.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest tests/slices/voz-de-la-jornada/ -q
python3 -m tools.wslice slice coverage voz-de-la-jornada
```
