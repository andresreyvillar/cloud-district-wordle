# Tasks — feat-ventana-de-ingesta

- [x] **Supuesto medido antes de tocar nada**: 1200 mensajes reales, mediana 10/día, peor racha de 3 días
      52 mensajes. La ventana de 50 no cubría tres días malos.
- [x] Comprobado que `users_list` **ya paginaba**: esa mitad del punto 4.2 del roadmap estaba hecha desde
      `ingesta-por-id-de-slack`. El roadmap estaba desactualizado, no el código.
- [x] Cuatro escenarios nuevos en el slice; 6 tests; cobertura 11/11.
- [x] Doble de Slack con la semántica que importa: orden inverso, cursor y `oldest`.
- [x] Implementación: `VENTANA_EN_DIAS`, `corte_de_la_ventana`, `mensajes_de_la_ventana`.
- [x] **Gate 4c — 5 mutantes, 0 supervivientes:**

| Mutante | Test que cae |
|---|---|
| la ventana baja a un día | `un_dia_muy_hablador_no_desplaza…` |
| no pagina: se queda en la primera página | `un_dia_muy_hablador_no_desplaza…` |
| no se pasa el corte a la API | `lo_anterior_al_corte_no_entra` |
| un fallo a media paginación devuelve lo leído | `un_fallo_en_la_segunda_pagina_aborta…` |
| el orden cronológico se invierte | `la_ventana_pagina_hasta_el_corte` |

- [x] Verificado contra Slack real (solo lectura, sin volcar texto): 123 mensajes en 2 páginas, 81
      resultados, jornadas #1660–#1674.
