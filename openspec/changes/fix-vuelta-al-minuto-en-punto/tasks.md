# Tareas

- [x] Contar las ejecuciones por día antes y después del cambio de minuto.
- [x] Medir los huecos entre ejecuciones consecutivas.
- [x] Comprobar que el primer hueco grande precede al cambio (descarta que lo causara).
- [x] Revertir los dos cron a los minutos medidos, dejando escrito por qué contra la recomendación.
- [ ] Observar dos días y decidir si hace falta el disparador externo.

## Comandos de verificación

```bash
grep -h "cron:" .github/workflows/*.yml
gh run list --workflow=update_stats.yml --limit 60 --json createdAt,event
```
