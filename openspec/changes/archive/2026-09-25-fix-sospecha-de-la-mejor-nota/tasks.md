# Tareas — fix-sospecha-de-la-mejor-nota

## 1. `tools/comentarios.py`

En el bucle de `hechos_elegidos`, la condición del hecho `sospechoso` deja de mirar solo la nota.

Antes del bucle hacen falta dos datos de la jornada: la **mejor nota** y **cuántos la firman**. Con eso, la
condición pasa a exigir las tres cosas: `score <= RESOLVER_SOSPECHOSO`, `score == mejor` y que solo haya uno
con esa nota.

`clavada` no se toca: resolver en 1 sigue teniendo su hecho.

Verificación: `.venv/bin/python3 -B -m pytest tests/slices/comentarios-de-la-jornada -q`

## 2. Tests

Tres escenarios nuevos en `tests/slices/comentarios-de-la-jornada/test_comentarios.py`, anotados con
`# @scenarios`:

- `la-sospecha-va-a-la-mejor-nota-del-dia`: jornada con un 1 y dos 2 → la sospecha nombra al del 1 y a nadie
  más. **Este es el caso real de la jornada 1709.**
- `una-nota-baja-compartida-habla-de-la-palabra-y-no-de-quien-juega`: dos personas con 2 y nadie por debajo →
  ningún hecho `sospechoso`.
- `sospechoso-es-el-chiste-raro`: una sola persona con 2 y el resto peor → sigue saliendo.

## Cierre

```bash
python3 -m tools.wslice slice validate comentarios-de-la-jornada
python3 -m tools.wslice slice coverage comentarios-de-la-jornada
python3 -m tools.wslice verify gates --slice comentarios-de-la-jornada --change-id fix-sospecha-de-la-mejor-nota
.venv/bin/python3 -B -m pytest -q
```

Gate 4c: quitar cualquiera de las dos condiciones nuevas —la de ser la mejor, o la de no compartirla— tiene
que poner en rojo su escenario y ninguno más.
