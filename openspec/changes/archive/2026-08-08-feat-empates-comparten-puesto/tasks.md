# Tasks — feat-empates-comparten-puesto

- [x] Medido antes de decidir: el **62%** de las jornadas que cuentan tiene empate en la mejor nota.
- [x] Slice con 5 escenarios · 5 tests · cobertura 5/5.
- [x] La misma regla en el ranking de figuras, que tenía el mismo defecto.
- [x] El mensaje **sangra** el empate en vez de repetir el número: dos «2º» seguidos se leen como una errata.
- [x] Coma decimal en el mensaje, como en la web.
- [x] Cambio de regla declarado como `MODIFIED` y slice `clasificacion-de-temporada` actualizado.
- [x] **Gate 4c — 2 mutantes, 0 supervivientes:** puestos correlativos otra vez, y el puesto que no salta.
- [x] Verificado con el mensaje real: agosto con un 4º compartido y el álbum con un 1º a tres bandas.

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/empates-comparten-puesto/
python3 -m tools.wslice verify gates --slice empates-comparten-puesto --change-id feat-empates-comparten-puesto
RESUMEN_COMPUESTO=1 python3 tools/local_stack.py --seco --sin-web
```
