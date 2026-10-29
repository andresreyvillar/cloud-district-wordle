# Tareas

- [x] Analizar la jornada #1707 y encontrar el patrón común (8 de 10 con `G.G.G`).
- [x] Medir cuántas cuadrículas del histórico dibujan la forma (5 de 1.806).
- [x] Medir el efecto de las cuatro posiciones posibles en el orden, y avisar de que la pedida deja 3 de 5.
- [x] Medir el efecto lateral del reorden (57 cuadrículas) y confirmar que el corte deja una.
- [x] `es_culo` sobre el patrón, la categoría, su emoji y sus 3 puntos.
- [x] Escenario nuevo y seis tests.
- [x] Actualizar la explicación de las reglas: pasa de cuatro categorías a cinco.
- [x] Atar a `VOCABULARIO`/`FIGURAS` las cuatro aserciones que enumeraban categorías a mano.
- [x] Gate 4c: seis mutaciones, cada una mata su escenario.
- [ ] Rematerializar tras el merge: la categoría vive en la instantánea.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage clasificacion-de-figuras
python3 -m tools.wslice verify gates --slice clasificacion-de-figuras --change-id feat-categoria-culo
```
