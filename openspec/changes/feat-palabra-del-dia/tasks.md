# Tareas

- [x] Confirmar que el grupo juega «La palabra del día» y que el `wordle_id` es el índice del juego.
- [x] Verificar el formato del fichero descifrado (2.000 entradas, `id`/`solution`/`extras` vacío).
- [x] Medir la cobertura del Wikcionario sobre jornadas ya jugadas, y descartar el falso 18/25 por límite.
- [x] Medir a qué hora publica el grupo, para elegir la ventana sin destripar a nadie.
- [x] `tools/palabra.py`: descifrado puro, guardarraíl, acepción y recorte.
- [x] Línea de apertura en el resumen, con la palabra entrando **por parámetro** (§10).
- [x] El borde en `post_ranking.py`, envuelto para que un fallo no impida publicar.
- [x] Cron a `0 22`, `30 22` y `0 23` de lunes a viernes.
- [x] `msgpack` en `requirements.txt` y en el workflow que publica.
- [x] Slice nuevo con 7 escenarios y 15 tests, **sin red**: el fichero cifrado se construye en el test.
- [x] Gate 4c: cinco mutaciones, cada una mata su escenario.
- [x] Verificación de punta a punta contra la red real antes de desplegar.
- [ ] Handoff staged: lo mergea el humano.

## Comandos de verificación

```bash
.venv/bin/python3 -B -m pytest -q
python3 -m tools.wslice slice coverage palabra-del-dia
python3 -m tools.wslice verify gates --slice palabra-del-dia --change-id feat-palabra-del-dia
RESUMEN_COMPUESTO=1 CAPTURA_OBJETIVO=v2 .venv/bin/python3 -B tools/preview_resumen.py
```
