# Tareas — fix-empate-en-cabeza

1. `v2/js/data/archivo.js`: `campeones`/`lideres` con todos los del puesto 1; medallero por cada campeón.
2. `v2/js/ui/temporadas.js`: exportar `tarjeta`; «EMPATE EN CABEZA», «CAMPEONES», «comparten el primer
   puesto».
3. `tools/refranero.py` + `tools/podio.py`: `PODIO_CAMPEONES` con varios campeones.

```bash
node --test tests/slices/archivo-de-temporadas/
.venv/bin/python3 -B -m pytest tests/slices/podio-de-cierre-de-mes
```
