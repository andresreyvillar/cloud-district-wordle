# Tareas — feat-debate-de-reglas

1. Migración `20261014120000_create_rule_debate.sql`: tablas, RLS, funciones y la votación anti-spoilers.
2. `v2/js/data/results.js`, `v2/js/domain/debate.js`, `v2/js/ui/debate.js`.
3. `v2/js/ui/info.js`, `v2/js/app.js`, `v2/css/styles.css`.
4. Aplicar la migración en producción (con confirmación del dueño).

```bash
.venv/bin/python3 -B -m pytest tests/slices/debate-de-reglas
node --test tests/slices/debate-de-reglas/
```
