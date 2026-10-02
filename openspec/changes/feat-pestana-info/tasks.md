# Tareas — feat-pestana-info

1. `tools/juego.py` y `tools/rules.py`: `HORA_DE_CONGELAR`, el eje `juego` con sus cinco reglas y `historica`.
2. `v2/js/ui/reglas.js`: `esVigente` y `reglasVigentes`.
3. `v2/js/ui/info.js`: `pintarInfo`, con la explicación sin cifras.
4. `v2/js/router.js` · `shell.js` · `app.js`: la vista Info, las rutas viejas y el salto del índice.
5. `v2/css/styles.css`: los bloques de Info.

```bash
.venv/bin/python3 -B -m pytest tests/slices/reglas-explicadas
node --test tests/
```
