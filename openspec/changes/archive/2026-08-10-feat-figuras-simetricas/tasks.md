# Tasks — feat-figuras-simetricas

- [x] **Medido antes de implementar**: acuerdo y reparto con espejo exacto, ≤1 y ≤2 defectos; e impacto sobre
      el ranking de figuras de agosto (no se mueve).
- [ ] Añadir al conjunto dorado la ficha del arco `🟩⬛⬛⬛🟩 / 🟩🟩⬛🟩🟩 / 🟩🟩🟩🟩🟩`, etiquetada `geometrico`,
      en `docs/context/sources/2026-08-05-etiquetado-de-patrones.md`. El parser espera la cabecera
      `## <n> · #<puzzle> · <intentos> intentos` con la rejilla en un bloque y `etiqueta: <categoria>` debajo.
- [x] **Corregido en la propuesta**: el espejo iba como segunda vía del geométrico y le robaba la categoría a
      las flores simétricas. Lo delataron los fixtures del slice, no la medición agregada.
- [ ] `tools/figures.py`: rasgo nuevo del espejo, medido **sobre el cuerpo**, consultado **en último lugar**
      —después del loro, del geométrico por densidad y de la flor—. La simetría es exacta: cero celdas rotas.
- [ ] No tocar el techo de densidad ni el orden de las reglas existentes.
- [ ] Sustituir el fixture `ABSTRACTO` de `tests/slices/clasificacion-de-figuras/test_album.py`, que es
      simétrico y pasaría a geométrico, por un abstracto **asimétrico**. No relajar la aserción.
- [ ] Test del invariante: sobre el conjunto dorado, ninguna ficha con figura cambia de categoría.
- [ ] Corregir el docstring de `es_geometrico`, que hoy promete «una escalera» y no la cumple. Dejar dicho que
      la escalera sigue en abstracto y por qué (simetría diagonal, no vertical).
- [ ] Los cinco escenarios nuevos en verde, y los del comportamiento anterior **sin debilitar**.
- [ ] Rehacer las dos medidas de calibración y comprobar los umbrales del proposal.
- [ ] Prueba de mutación (Gate 4c): cambiar el espejo exacto por «≤1 defecto» debe poner en rojo
      `una-celda-rota-no-es-espejo`; quitar el descarte de la banda final debe poner en rojo
      `la-simetria-se-mide-sin-contar-el-suelo`.

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/clasificacion-de-figuras/
.venv/bin/python3 tools/calibrate_figures.py --sin-red     # acuerdo ≥ 24/31 con la ficha nueva
.venv/bin/python3 tools/calibrate_figures.py               # + reparto sobre producción (solo lee)
python3 -m tools.wslice slice coverage clasificacion-de-figuras
python3 -m tools.wslice verify gates --slice clasificacion-de-figuras --change-id feat-figuras-simetricas
```

## Ojo

El conjunto dorado pasa de 30 a 31 fichas, así que **el denominador del acuerdo cambia**: 24/30 = 80% pasa a
ser 25/31 = 81% si la ficha nueva acierta. Los umbrales escritos en el docstring de `figures.py` y en el
proposal se refieren a las 30 originales — actualizarlos, no compararlos a ciegas.
