# Tasks — feat-voz-de-la-jornada

- [x] **Medido antes de proponer**: la señal del canal existe (6-9 reacciones en buenos resultados, hilos de
      37 y 14 respuestas) y la hora real tiene resolución de segundos. `created_at` NO sirve para el
      madrugador: 34% de minutos distintos porque el cron escribe por lotes.
- [x] `tools/refranero.py` con el diccionario. Solo datos, sin lógica.

## Antes de escribir código

- [ ] **Calibrar los umbrales** de madrugador y rezagado sobre el histórico del canal, y escribir el informe
      en un módulo `tools/calibrate_menciones.py` que solo lea. Criterio: la mención sale en una **minoría
      clara** de las jornadas. Si un umbral nombra a alguien casi siempre, no vale.
- [ ] Decidir con el dueño qué frases del diccionario no suenan al grupo y sustituirlas. **El chiste lo
      conoce él, no el agente.**

## Implementación

- [ ] `tools/senales.py`: deriva del canal hora de publicación por jugador, reacciones por mensaje, respuestas
      por hilo y ausentes. **El texto de los mensajes no sale de este módulo** — solo horas y recuentos.
      Ignora los mensajes del bot y distingue resultado de charla.
- [ ] `tools/voz.py`: elige frase de día (registro por `dificultad()`), pullas de líder, menciones y meme.
      Índice por `jornada % len(...)`. Sin `random` y sin `datetime.now()`.
- [ ] Las condiciones del meme, evaluadas **en orden**, con la primera que se cumpla. Ninguna se cumple → sin
      meme.
- [ ] `tools/post_ranking.py`: lee el canal en el borde y pasa las señales por parámetro. Envuelto para que
      un fallo de la lectura **no impida publicar**.
- [ ] `tools/preview_resumen.py`: compone el mensaje de una jornada y lo imprime **sin publicar**. Es la
      herramienta que cazó «resolvión» con todos los gates en verde.
- [ ] Ninguna frase se repite dentro del mismo mensaje.

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/voz-de-la-jornada/
.venv/bin/python3 tools/calibrate_menciones.py          # frecuencia de cada mención; solo lee
.venv/bin/python3 tools/preview_resumen.py              # el mensaje, sin publicarlo
python3 -m tools.wslice slice coverage voz-de-la-jornada
python3 -m tools.wslice verify gates --slice voz-de-la-jornada --change-id feat-voz-de-la-jornada
```

## Ojo

**Este slice toca el token de Slack y publica en el canal del grupo**, así que la Fase 4 incluye revisión de
seguridad (Gate 4e). Dos riesgos concretos: que el texto de un mensaje del canal acabe en el mensaje
publicado o en un test, y que el bot suba una imagen. Los dos están prohibidos por spec, y los dos hay que
comprobarlos, no suponerlos.

**Los fixtures de los tests son sintéticos.** No se copian mensajes reales del canal al repositorio, ni
siquiera anonimizados: el repositorio es público.
