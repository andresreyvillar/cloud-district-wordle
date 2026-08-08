# Tasks — feat-archivo-de-temporadas

## 1 · Fase 2 — TDD rojo

- [x] 7 escenarios, 9 tests en `tests/slices/archivo-de-temporadas/archivo.test.js`.
- [x] Cobertura 7/7 declarada con el módulo sin existir.

## 2 · Fase 3 — implementación

- [x] `v2/js/data/archivo.js`: `archivo()` y `medallero()`. Puras.
- [x] `v2/js/ui/temporadas.js`: tarjeta por temporada con campeón o líder, totales, marca de bloque
      histórico, y el medallero acumulado con desglose por tipo.
- [x] `app.js` enruta `/temporadas`.

## 3 · Gates

- [x] `wslice slice validate` — 11 slices, 0 errores, 0 warnings.
- [x] 45 tests JS en verde · suite Python sin regresiones.
- [x] **Gate 4c — mutación: 5 mutantes, 0 supervivientes.**

| Mutante | Resultado |
|---|---|
| la temporada en curso también corona | 🔴 dos tests |
| el archivo ordenado de la más antigua a la más reciente | 🔴 dos tests |
| la temporada 0 no se marca como histórica | 🔴 |
| el medallero cuenta jugadores en lugar de medallas | 🔴 |
| una temporada vacía desaparece del archivo | 🔴 |

## 4 · Verificación en navegador (datos reales)

- [x] `Archivo · 2 temporadas · 1 cerrada`.
- [x] `Temporada 1 · agosto 2026` **EN CURSO** → «VA GANANDO Andrés R. 3,00», 4 jornadas, 12 jugadores.
- [x] `Temporada 0 · el histórico` **CERRADA** → «CAMPEÓN Claire 3,56», 181 jornadas, 21 jugadores,
      1502 resultados, con la marca de bloque histórico.
- [x] Clases correctas: `abierta` en agosto, `historica` en la 0.
- [x] Medallero de 17 filas, encabezado por Andrés R. con 5 · el enlace de una temporada abre su marcador.
- [x] **Cero errores de consola.**

## 5 · Hallazgo, arreglado aparte

- [x] La temporada 0 salía con una medalla por jugador. Causa y arreglo en `fix-medallas-temporada-cero`.
