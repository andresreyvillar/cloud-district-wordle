# Tareas

- [x] Medir el cambio con el corte puesto (1 de 1.706) y sin él (47).
- [x] El espejo por delante de la flor, dentro de la rama del orden nuevo.
- [x] Renombrar el corte a `PRIMERA_JORNADA_DEL_ORDEN_NUEVO`: gobierna ya dos cambios de orden.
- [x] `CUERPO_MINIMO_DEL_ESPEJO` y `es_espejo_reconocible` en `figures.py`, compartidos con el logro.
- [x] Tres escenarios nuevos y el de la invariante histórica renombrado.
- [x] Gate 4c: cuatro mutaciones, cada una mata su escenario.
- [x] Suite completa, `slice coverage`, `slice validate`, `verify gates`.
- [ ] Rematerializar tras el merge: la categoría vive en la instantánea.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage clasificacion-de-figuras
python3 -m tools.wslice verify gates --slice clasificacion-de-figuras --change-id feat-espejo-gana-a-la-flor
```
