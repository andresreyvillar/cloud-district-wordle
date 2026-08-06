# Deltas de `estadisticas` — fix-medallas-temporada-cero

## MODIFIED Requirements

### Requirement: La ventana de una temporada la decide el modelo, no el prefijo de la fecha

Cuando un cálculo necesita las filas de una temporada, la pertenencia la decide **la función del modelo de
temporadas**, no una comparación de cadenas contra la fecha.

Comparar el identificador con el principio de la fecha funcionaba mientras toda temporada era un `AAAA-MM`.
Con la temporada 0 dejó de funcionar **en silencio**: ninguna fecha empieza por `0`, así que el histórico
entero se quedó sin una sola medalla de temporada mientras las permanentes seguían apareciendo.

#### Scenario: la temporada 0 reparte medallas sobre todo el histórico
- GIVEN partidas repartidas en meses anteriores al límite de temporadas
- WHEN se piden las medallas de la temporada 0
- THEN se calculan sobre todas ellas, y quien llegue al umbral de Fondista la gana

#### Scenario: la misma medalla en dos temporadas numeradas cuenta dos veces
- GIVEN quince partidas en agosto y quince en septiembre
- WHEN se piden las medallas de cada temporada
- THEN Fondista aparece en las dos

verified-by:
  - tests/slices/medallas-en-el-resumen-diario/test_medallas.py
