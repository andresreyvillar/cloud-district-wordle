# Tareas — feat-victoria-el-ultimo-dia

1. `tools/calendario.py`: el último laborable del mes.
2. `tools/juego.py`: `mes_en_que_puntua`; `niveles_que_puntuan` valida en el mes de la jornada.
3. `tools/resumen.py`: `bloque_ultima_jornada`; `por_jugar` sin el último laborable.
4. `tools/podio.py`: `_otros_campeones` y `ultima_jornada`.
5. `tools/post_ranking.py` y `tools/post_podium.py`: `publicar_la_victoria`; el título y `ya_celebrado` en
   `post_ranking`; el juego por parámetro.

```bash
.venv/bin/python3 -B -m pytest tests/slices/podio-de-cierre-de-mes tests/slices/clasificacion-del-juego tests/slices/resumen-diario-compuesto
```
