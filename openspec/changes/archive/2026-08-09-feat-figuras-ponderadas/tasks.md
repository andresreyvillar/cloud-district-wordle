# Tasks — feat-figuras-ponderadas

- [x] **Medido antes de implementar** el efecto sobre el podio, con las dos escalas candidatas.
- [x] `PUNTOS` en `album.py`, y el catálogo de la instantánea publica lo que vale cada figura.
- [x] La puntuación sigue siendo **por partida**: la propiedad que impide que gane quien más juega.
- [x] La escala se anuncia en la vista y sale del catálogo, no de una tabla propia.
- [x] Web, ficha y mensaje de Slack adaptados; `tasa` se sigue publicando como dato.
- [x] Cambio de regla declarado como `MODIFIED`. Cinco tests actualizados, ninguno debilitado: siguen
      comprobando el criterio, sobre el que ahora manda.

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/clasificacion-de-figuras/
node --test tests/slices/album-de-figuras/
RESUMEN_COMPUESTO=1 python3 tools/local_stack.py --seco --sin-web
```
