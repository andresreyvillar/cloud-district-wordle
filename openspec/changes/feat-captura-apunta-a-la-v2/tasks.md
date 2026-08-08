# Tasks — feat-captura-apunta-a-la-v2

- [x] Slice con 6 escenarios, declarando por qué es slice propio pese a compartir cron con
      `medallas-en-el-resumen-diario` (uno decide qué dice el mensaje, otro de dónde sale la imagen).
- [x] 8 tests. **Ninguno publica**: la captura y la subida entran por parámetro como dobles.
- [x] `Objetivo` con URL y los dos selectores juntos; `OBJETIVOS` con v1 y v2; `CAPTURA_OBJETIVO`.
- [x] `publicar()` devuelve código de salida; `main` lo propaga con `SystemExit`.
- [x] Workflow: añadidas `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY` al paso que publica —faltaban, y por
      eso el mensaje nunca ha llevado medallas— y `CAPTURA_OBJETIVO` con `v1` por defecto.
- [x] Los dos tests del slice hermano que llamaban `comentario(seccion)` pasan a pasar el objetivo. **No se
      ha relajado la firma** para que siguieran verdes: el acoplamiento entre foto y enlace es lo que el
      slice fija. La aserción gana precisión: ya no comprueba «workers.dev», comprueba la URL del objetivo.
- [x] **Gate 4c — 5 mutantes, 0 supervivientes:**

| Mutante | Test que cae |
|---|---|
| un objetivo desconocido cae en el por defecto | `un_objetivo_desconocido_revienta` |
| el enlace vuelve a ser fijo | `el_enlace_del_mensaje_es_el_del_objetivo_capturado` |
| una captura fallida devuelve éxito | `una_captura_fallida_termina_con_error` |
| una subida fallida devuelve éxito | `una_subida_fallida_termina_con_error` |
| los dos objetivos comparten selectores | `cada_objetivo_trae_su_url_y_sus_dos_selectores` |

- [x] Suite completa en verde. **`post_ranking.py` no se ha ejecutado**: publica en el canal.
