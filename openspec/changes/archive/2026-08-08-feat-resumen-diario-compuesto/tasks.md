# Tasks — feat-resumen-diario-compuesto

- [x] Slice con 7 escenarios · 12 tests · cobertura 7/7 · `tools/resumen.py` puro.
- [x] El resumen **no recalcula**: marcador de `standings` y álbum de `album`, los mismos que publica la web.
- [x] La rareza de la obra del día sale **del reparto de la propia temporada**, no de una tabla escrita a
      mano: recalibrar el clasificador cambia qué figura es rara.
- [x] **Gate 4c — 6 mutantes, 0 supervivientes:**

| Mutante | Resultado |
|---|---|
| el jugador del día es la peor puntuación | 🔴 `jugador-del-dia` |
| el empate solo nombra al primero | 🔴 `jugador-del-dia` |
| la obra del día es la figura más común | 🔴 `obra-del-dia` |
| un abstracto puede ser obra del día | 🔴 `obra-del-dia` |
| el emoji del top sale de cualquier día | 🔴 `top-cinco-con-su-dibujo` |
| el álbum se imprime sin nadie clasificado | 🔴 `sin-jornada-no-hay-resumen` |

- [x] **Dos tests flojos corregidos, los dos cazados midiendo en vez de suponiendo:**
  - el del límite de Slack comparaba 499 caracteres contra 3000 y no ejercitaba nada. Se comprobó, se quitó
    el recorte —que era código para un caso imposible— y el escenario pasa a ser el que de verdad importa:
    **el mensaje no crece con el grupo**;
  - el del jugador del día afirmaba `"Ana" in texto`, y Ana sale también en el top y en el álbum, así que
    pasaba aunque el premio se lo llevara otro. Lo cazó el mutante que invierte `min` por `max`.
- [x] Verificado con los datos reales (`--seco`, sin publicar): el mensaje que saldría hoy.

## Comandos

```bash
.venv/bin/python3 -B -m pytest tests/slices/resumen-diario-compuesto/
.venv/bin/python3 -B -m pytest
python3 -m tools.wslice verify gates --slice resumen-diario-compuesto --change-id feat-resumen-diario-compuesto
python3 tools/local_stack.py --seco --sin-web    # imprime el mensaje, no publica
```
