# Tasks — feat-resultado-del-dia

## 1 · Fase 2 — TDD rojo

- [x] 8 escenarios, 11 tests en `tests/slices/resultado-del-dia/dia.test.js`.
- [x] Cobertura 8/8 declarada con el módulo sin existir; rojo comprobado.
- [x] Fixtures con la forma de `normalizar()` (filas) y de `rules.como_json()` (reglas), que son las que
      produce el sistema de verdad.

## 2 · Fase 3 — implementación

- [x] `v2/js/data/dia.js`: `diaEnCurso()`, `minimoDeLaMuestra()`, `esLaborable()`. Puras, sin reloj.
- [x] `v2/js/ui/hoy.js`: titular con la jornada y la fecha, HUD, veredicto del día, el aviso de si cuenta,
      tarjetas de resultado enlazadas a la ficha y los ausentes.
- [x] `app.js` enruta `/hoy` con las filas crudas y las instantáneas.

## 3 · Gates

- [x] `wslice slice validate` — 10 slices, 0 errores, 0 warnings.
- [x] Cobertura 8/8 · 36 tests JS en verde · suite Python sin regresiones.
- [x] **Gate 4c — mutación: 5 mutantes, 0 supervivientes.**

| Mutante | Resultado |
|---|---|
| la jornada en curso es la primera con datos | 🔴 |
| el fin de semana cuenta si hay muestra | 🔴 |
| sin reglas publicadas, el umbral por defecto es 5 | 🔴 |
| quien falta se calcula con los presentes | 🔴 |
| el veredicto dura/fácil invertido | 🔴 dos tests |

## 4 · Verificación en navegador (datos reales, ya migrados)

- [x] `/hoy` → `#1673 · Jueves 6 de agosto · Temporada 1 · agosto 2026`.
- [x] `HAN JUGADO 11 · FALTAN 1 · MEDIA DEL DÍA 3,91 · MEJOR 2`.
- [x] Veredicto: «más fácil que la media de la temporada (4,17), por 0,26».
- [x] Aviso: «ya cuenta para la temporada: es laborable y la han jugado 11 personas, el mínimo son 5».
- [x] Las 11 tarjetas ordenadas del 2 al 6, cada una enlazando a su ficha; el clic navega y pinta.
- [x] **Cero errores de consola.**
- [x] Corregido lo que solo se ve en el navegador: `text-transform: capitalize` escribía «6 De Agosto». La
      mayúscula se pone ahora en el texto, no en el CSS.
