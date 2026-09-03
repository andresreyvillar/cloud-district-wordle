# Tareas

- [x] Distinguir las dos causas: ventanas descartadas y fallos de red.
- [x] Leer el log del fallo real y confirmar que era `httpx.ReadTimeout`.
- [x] `con_reintento` en la lectura y la escritura, solo para fallos transitorios.
- [x] `scheduled` en el Worker con `workflow_dispatch`, apagado sin token.
- [x] Cron Trigger en `wrangler.jsonc`, en un minuto distinto del de GitHub.
- [x] Dos escenarios nuevos, tres tests de Python y cuatro de JavaScript.
- [x] Gate 4c: cuatro mutaciones, cada una mata su escenario.
- [ ] **A mano**: `npx wrangler secret put GITHUB_TOKEN` y `npx wrangler deploy`.
- [ ] Observar dos días si la cadencia horaria se cumple.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
node --test tests/slices/temporada-mensual/disparador.test.js
.venv/bin/python3 -B tools/materialize_seasons.py --dry-run
```
