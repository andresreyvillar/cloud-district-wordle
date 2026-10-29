# Tasks — chore-nombres-de-logros

## Tarea 1 — Renombrar en el catálogo

`tools/badges.py`: la clave `pleno` → `metronomo`, el nombre → `Metrónom@`, y
`MINIMO_DIAS_PARA_PLENO` → `MINIMO_DIAS_PARA_METRONOMO`.

## Tarea 2 — El escenario y su test

`pleno-solo-exige-los-dias-laborables` → `metronomo-solo-exige-los-dias-laborables`, en el slice y en la
anotación `@scenarios` del test.

Y un test nuevo que impida la colisión que este pack rechaza: **dos medallas no pueden llamarse igual**.

## Tarea 3 — Verificación

```bash
.venv/bin/python3 -B -m pytest tests/slices/medallas-en-el-resumen-diario -q
python3 -m tools.wslice slice coverage medallas-en-el-resumen-diario
grep -rn "pleno" tools/ tests/ openspec/slices/     # esperado: sin resultados
.venv/bin/python3 -B -m pytest -q
```

## Tarea 4 — Cerrar

`git add -A` y parar.
