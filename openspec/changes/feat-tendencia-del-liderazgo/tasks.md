# Tareas

- [x] Medir las cinco tendencias candidatas sobre los datos reales y decidir cuáles entran.
- [x] Simular la línea diaria y documentar por qué se descarta (el «lleva N jornadas mandando» falso).
- [x] `TENDENCIA_DEL_MES` (8 frases) y `DOMINIO` (6) en `tools/refranero.py`.
- [x] `historia_del_liderazgo()` en `tools/resumen.py`: cambios, jornadas por jugador y **racha seguida**.
- [x] Engancharla a `bloque_relevo`; `_dominio()` en el mismo hueco cuando no hay relevo.
- [x] Dos escenarios nuevos en el slice y seis tests con `@scenarios`.
- [x] Gate 4c: cuatro mutaciones, cada una mata su escenario.
- [x] Suite completa, `slice coverage` 20/20, `slice validate`, `verify gates`.
- [x] Medir la duración y la recurrencia de los empates; escalar por recurrencia.
- [x] `RIVALIDAD_EMPATE_OTRA_VEZ` (8) y `RIVALIDAD_EMPATE_TENSION` (8); `veces_esta_cabeza` en la historia.
- [x] Arreglar el punto doble de las frases de rivalidad (`sin_punto_doble` en `tools/voz.py`).
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest tests/slices/resumen-diario-compuesto/ -q
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage resumen-diario-compuesto
python3 -m tools.wslice slice validate resumen-diario-compuesto
python3 -m tools.wslice verify gates --slice resumen-diario-compuesto --change-id feat-tendencia-del-liderazgo
```
