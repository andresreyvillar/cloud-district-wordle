# Deltas de `dashboard` — feat-archivo-de-temporadas

## ADDED Requirements

### Requirement: El medallero acumula todas las temporadas

El archivo publica un medallero con las medallas de cada jugador **sumadas sobre todas las temporadas**,
desglosadas por tipo, y cuántas temporadas ha ganado. Ganar cuenta solo en temporadas cerradas: en una
abierta se va ganando, no se ha ganado.

#### Scenario: el medallero suma todas las temporadas
- GIVEN medallas repartidas en varias temporadas
- WHEN se muestra el medallero
- THEN cada jugador aparece con su total, su desglose por tipo y sus temporadas ganadas, de más a menos

#### Scenario: cada temporada del archivo enlaza a su marcador
- GIVEN el archivo con temporadas
- WHEN se pulsa una
- THEN se abre su marcador

#### Scenario: sin instantáneas el archivo lo declara
- GIVEN ninguna temporada materializada
- WHEN se abre el archivo
- THEN lo declara en lugar de mostrar una lista vacía

verified-by:
  - tests/slices/archivo-de-temporadas/archivo.test.js
