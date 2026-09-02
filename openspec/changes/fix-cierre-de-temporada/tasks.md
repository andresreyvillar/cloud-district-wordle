# Tareas

- [x] Comprobar que `temporadas()` ya marcaba agosto como cerrada (el cálculo no era el problema).
- [x] Localizar la instantánea congelada y su fecha, para confirmar la causa.
- [x] `por_defecto()`: la en curso más la última cerrada.
- [x] Escenario nuevo con sus tests.
- [x] Gate 4c: tres mutaciones, cada una mata su escenario.
- [x] Rematerializar para arreglar la instantánea ya publicada.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
.venv/bin/python3 -B tools/materialize_seasons.py --dry-run
python3 -m tools.wslice slice coverage temporada-mensual
```
