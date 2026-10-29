# Tasks — chore-stack-local

## Tarea 1 — `tools/local_stack.py`

Orquesta los cuatro pasos y **declara qué escribe** antes de escribir. Banderas: `--seco`, `--con-ingesta`,
`--sin-web`, `--sin-resumen`, `--temporada` (repetible), `--puerto`.

## Tarea 2 — Verificación

```bash
.venv/bin/python3 -B -m py_compile tools/local_stack.py
python3 tools/local_stack.py --seco --sin-web
#   esperado: los tres pasos, "(seco, sin escribir)", y el resumen impreso sin publicar
python3 tools/local_stack.py --temporada 2026-08 --sin-web --sin-resumen
#   esperado: materializadas=1
.venv/bin/python3 -B -m pytest -q
```

## Tarea 3 — Cerrar

Documentar el comando en `CLAUDE.md`, `git add -A` y parar.
