# Tareas

- [x] Verificar la fórmula real antes de tocarla (no era «media del día + porcentaje»).
- [x] Medir qué cuesta faltar hoy y encontrar la inversión Carlos/Clara C.
- [x] Comparar cuatro opciones sobre los datos reales de agosto.
- [x] `margen_de(ausencia)` y el contador de ausencias en el bucle de imputación.
- [x] Escenario nuevo y tres tests, uno con la escala del mes que reproduce el defecto.
- [x] Actualizar la página de reglas con la fórmula y sus dos parámetros.
- [x] Gate 4c: cuatro mutaciones, cada una mata su escenario.
- [ ] Rematerializar tras el merge: la clasificación vive en la instantánea.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage clasificacion-de-temporada
python3 -m tools.wslice verify gates --slice clasificacion-de-temporada --change-id feat-margen-creciente
```
