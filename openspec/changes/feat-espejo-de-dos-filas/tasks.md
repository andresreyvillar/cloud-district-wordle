# Tareas

- [x] Analizar el caso concreto y explicar por qué salía flor.
- [x] Medir el impacto del umbral 2 y corregir el aviso previo (1 cuadrícula, no 4).
- [x] Separar `CUERPO_MINIMO_DEL_ESPEJO` (categoría) de `CUERPO_MINIMO_DEL_LOGRO` (logro).
- [x] Fijar por test que los dos umbrales divergen a propósito.
- [x] Cambiar el fixture de flor que resultó ser simétrico, en los cuatro ficheros que lo usaban.
- [x] Hacer que el test de «patrón no ambiguo» compruebe su premisa en lugar de suponerla.
- [x] Gate 4c: cuatro mutaciones, cada una mata su escenario.
- [ ] Rematerializar tras el merge: la categoría vive en la instantánea.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage clasificacion-de-figuras
python3 -m tools.wslice verify gates --slice clasificacion-de-figuras --change-id feat-espejo-de-dos-filas
```
