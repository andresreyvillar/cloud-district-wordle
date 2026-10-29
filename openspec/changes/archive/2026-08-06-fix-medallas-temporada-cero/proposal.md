# Proposal — fix-medallas-temporada-cero

> **Slice:** `medallas-en-el-resumen-diario` (modificación: un escenario nuevo)

## Why

Lo encontró la vista del archivo al pintar el medallero acumulado: **toda la temporada 0 tenía una sola
medalla por jugador**, y siempre de las permanentes (Suertud@, El día imposible). Nadie con Fondista después
de 181 jornadas de historia, cuando el umbral son quince partidas.

La causa: `_de_la_temporada` filtraba con `str(fila["date"]).startswith(temporada)`. Funcionaba mientras
toda temporada era un `AAAA-MM`; con la temporada 0 **ninguna fecha empieza por `0`**, así que la ventana
salía vacía y `medallas_de_temporada` devolvía `{}` sin quejarse. Las permanentes seguían apareciendo porque
no pasan por ese filtro, y ese contraste es lo que delató el fallo.

Es exactamente el tipo de error que el modelo de temporadas debía impedir: **dos definiciones de "pertenecer
a una temporada"**, una en `seasons.temporada_de` y otra escrita a mano aquí.

## What Changes

- `tools/badges.py`: `_de_la_temporada` usa `seasons.temporada_de`, la misma función que decide la temporada
  de un resultado en el ranking. Ahora no pueden divergir.
- Escenario nuevo en el slice: `la-temporada-cero-tambien-reparte-medallas`.
- **Un fixture corregido**: `test_la_misma_medalla_en_dos_temporadas_cuenta_dos_veces` usaba julio y agosto,
  y julio dejó de ser una temporada al decidirse la temporada 0. Pasa a usar agosto y septiembre. Se
  corrigió el fixture, no la aserción.

## Impact

- El medallero real pasa de 6 jugadores con una medalla cada uno a **17 jugadores**, con hasta 5.
- Instantáneas rematerializadas.
- **Observación que queda anotada, no resuelta:** los umbrales están calibrados para un mes, y sobre las 181
  jornadas de la temporada 0 se cumplen casi todos (Verdugo y Fondista los tiene medio grupo). La temporada 0
  es un caso atípico por construcción; si se quiere que su medallero discrimine, hay que decidirlo como regla.
