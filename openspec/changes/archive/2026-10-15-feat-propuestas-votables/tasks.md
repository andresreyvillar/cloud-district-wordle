# Tareas — feat-propuestas-votables

1. Migración: política de lectura, `rule_proposal_votes` y `votar_propuesta`.
2. Web: lectura de votos, `apoyos`, botones y publicación al momento.
3. Aplicar la migración en producción (con el visto bueno del dueño).

```bash
.venv/bin/python3 -B -m pytest tests/slices/debate-de-reglas
node --test tests/slices/debate-de-reglas/
```
