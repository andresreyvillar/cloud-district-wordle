# Tasks — feat-desempate-del-album

- [x] Diagnosticado antes de tocar: los empates son aritméticos (5 jornadas → 6 valores posibles) y los
      empatados tienen colecciones idénticas.
- [x] **Medido y descartado** el desempate por orden de publicación: el 34% de minuto distinto por jornada,
      ninguna jornada con todos distintos.
- [x] Desempate por media de la tabla de puntuación, con import local para no crear un ciclo.
- [x] Se comparte puesto solo cuando **la clave entera** coincide, no solo la media del álbum.
- [x] 2 tests nuevos: que el desempate ordena, y que sin nada que separe se sigue compartiendo puesto.
- [x] Fixture de medallas corregido: llevaba filas sin `slack_user_id`, que producción no tiene.
- [x] Verificado con datos reales: agosto pasa de 1,1,3,3,5,6,6,6 a 1..8 sin huecos.

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/clasificacion-de-figuras/
.venv/bin/python3 -B -m pytest
python3 tools/local_stack.py
```
