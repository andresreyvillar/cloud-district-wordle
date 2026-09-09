# Tareas

- [x] Medir qué pasaría exigiendo las cinco categorías a secas (25 personas perderían la medalla).
- [x] Medir la alternativa autoajustable y confirmar que agosto y la temporada 0 quedan intactos.
- [x] `categorias_vistas` desde el reparto del álbum, sin un segundo recuento.
- [x] `_es_coleccionista` con las vistas y respaldo a las cuatro de siempre.
- [x] Actualizar la regla que lee el grupo: «las cuatro figuras» → «cada figura que haya salido».
- [x] Escenario nuevo y cuatro tests, incluido el del flujo completo.
- [x] Gate 4c: cuatro mutaciones, cada una mata su escenario.
- [ ] Rematerializar tras el merge: los logros viven en la instantánea.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
node --test tests/slices/medallas-de-figuras/medallas.test.js
python3 -m tools.wslice slice coverage medallas-de-figuras
```
