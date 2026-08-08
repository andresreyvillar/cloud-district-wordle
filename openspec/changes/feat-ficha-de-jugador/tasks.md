# Tasks — feat-ficha-de-jugador

## 1 · Fase 2 — TDD rojo

- [x] 8 escenarios, 13 tests en `tests/slices/ficha-de-jugador/ficha.test.js` (`node --test`).
- [x] Cobertura 8/8 declarada con el módulo aún sin existir; rojo comprobado.
- [x] Los fixtures copian la forma **real** de la carga útil de `tools/seasons.py`. Se corrigió uno: la
      temporada 0 traía una jornada imputada, que es un dato que Python no puede producir porque esa
      temporada no imputa. Se arregló el fixture, no el código.

## 2 · Fase 3 — implementación

- [x] `v2/js/data/ficha.js`: `ficha()`, `palmares()`, `rutaDeFicha()`. Puras.
- [x] `v2/js/ui/jugador.js`: titular con puesto, HUD, coste de faltar, distribución, desglose, medallas,
      palmarés y vuelta al marcador.
- [x] `filaDeMarcador()` extraída y exportada de `temporada.js`; el podio enlaza también.
- [x] `app.js` enruta la vista y le pasa **todas** las instantáneas (el palmarés las necesita).
- [x] CSS de los bloques nuevos, con las tablas de la ficha escapando del grid de 7 columnas del marcador.

## 3 · Gates

- [x] `wslice slice validate` — 9 slices, 0 errores, 0 warnings.
- [x] `wslice verify slice ficha-de-jugador` — cobertura 8/8; indeterminate solo por las specs
      consolidadas, que se crean en el archive.
- [x] 25 tests JS en verde (13 del slice + 12 del esqueleto) · suite Python sin regresiones.
- [x] **Gate 4c — mutación: 5 mutantes, 0 supervivientes.**

| Mutante | Resultado |
|---|---|
| el coste de faltar, calculado al revés | 🔴 |
| el palmarés ordenado de la más antigua a la más reciente | 🔴 |
| una temporada sin imputación publica coste igual | 🔴 |
| el enlace pierde la temporada (`/j/<x>`) | 🔴 dos tests |
| el nombre entra sin escapar en el enlace | 🔴 |

## 4 · Verificación en navegador (datos reales)

- [x] `/t/0` → las filas enlazan: `Claire → /t/0/j/U02TN4L9HEE`.
- [x] Ficha de la temporada 0: `1º · 3,56 · 102/181 · mejor 2 · peor fallo`; distribución que suma 102;
      bloque **MES A MES** por las 181 jornadas; `AUSENCIAS · esta temporada no imputa`.
- [x] Ficha de una temporada con imputación: `3,50 → 3,87 · +0,37`, y la jornada imputada marcada con 4,62.
- [x] Palmarés con las dos temporadas y la abierta señalada · navegación marcando «Temporada».
- [x] Identificador inexistente: la vista lo declara y ofrece volver. **Cero errores de consola.**

## 5 · Lo que este slice NO hace

- **La gráfica de evolución**: necesita la escala fija comparable (Fase 4.4).
- **El álbum de figuras del jugador**: el clasificador ya está calibrado, pero el álbum es su propio slice.
- **Agrupar medallas por identidad**: `tools/badges.py` sigue agrupando por nombre. Declarado en el slice.
