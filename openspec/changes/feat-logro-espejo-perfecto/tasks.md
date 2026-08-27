# Tareas

- [x] Medir espejos por altura de cuerpo y jugadores distintos, para elegir el umbral.
- [x] `MINIMO_CUERPO_DEL_ESPEJO = 3` y la medalla en el catálogo de `tools/badges.py`.
- [x] Concederla desde el rasgo, no desde la categoría, en `medallas_permanentes`.
- [x] Añadirla al catálogo de la web (`v2/js/ui/temporada.js`) y al sprite de iconos.
- [x] Dos escenarios nuevos, y quitar el número del escenario del catálogo.
- [x] Test que cruza el catálogo de Python con el de la web, que es la drift que este cambio destapó.
- [x] Gate 4c: cinco mutaciones, cada una mata su escenario.
- [x] Suite completa, `slice coverage`, `slice validate`, `verify gates`, tests JS.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
node --test tests/slices/medallas-de-figuras/medallas.test.js
python3 -m tools.wslice slice coverage medallas-de-figuras
python3 -m tools.wslice verify gates --slice medallas-de-figuras --change-id feat-logro-espejo-perfecto
```
