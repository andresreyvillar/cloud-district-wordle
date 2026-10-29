# Tasks — feat-tabla-de-datos

- [x] 7 escenarios · 8 tests en `tests/slices/tabla-de-datos/tabla.test.js`. Cobertura 7/7.
- [x] `v2/js/data/tabla.js` y `v2/js/ui/datos.js`; `/datos` deja de estar pendiente.
- [x] **Fallo encontrado en el navegador y arreglado**: «70 de 1543 cuentan». Ver el proposal.
- [x] `v2/js/data/temporada.js`: una sola definición, con el límite leído de las reglas.
- [x] `normalizar()` renombra `temporada` → `mes`.
- [x] **Gate 4c — 4 mutantes, 0 supervivientes**: orden ascendente · sin instantánea se afirma que no
      cuenta · el motivo invertido · el fallo pintado como 7.
- [x] Verificado en navegador: 1572 filas en el DOM, cabecera correcta, los fallos como `X`,
      cero errores de consola.

## Nota de datos, no del slice

Al contar las filas salió que la tabla tiene **1572** cuando la migración de ayer dejó 1543: el cron de
`main` ha metido **29 filas de deriva en menos de un día**, y las 29 duplican a alguien que ya estaba en su
jornada. Se ve a simple vista en la tabla (el mismo jugador dos veces en `#1673`). No se ha tocado
producción: es una decisión del humano.
