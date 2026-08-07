# Tasks — fix-reglas-ratificadas

- [x] 13 reglas aplicadas → votadas.
- [x] Dos estados corregidos: la imputación y el «sin mínimo» **están aplicados** desde el 2026-08-05.
- [x] `rules.MARGEN_DE_IMPUTACION` eliminado; el parámetro apunta a `standings.MARGEN`.
- [x] Dos tests reescritos al hecho actual, uno de ellos comprobando el estado **contra el cálculo**.
- [x] Un fixture corregido antes de dar el test por bueno: con cinco jugadores, quitar a uno dejaba la
      jornada por debajo de la muestra mínima y no se imputaba nada — el test habría fallado por el motivo
      equivocado. Con seis, la ausencia es una ausencia.
- [x] Cobertura 7/7 · suite completa en verde · instantáneas rematerializadas.
- [x] **Gate 4c — 3 mutantes, 0 supervivientes:** el margen publicado como literal · la imputación marcada
      como votada · el cálculo dejando de imputar.
