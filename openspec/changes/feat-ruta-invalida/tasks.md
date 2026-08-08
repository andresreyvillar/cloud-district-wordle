# Tasks — feat-ruta-invalida

- [x] Slice con 6 escenarios, incluida la distinción entre ruta inválida y jugador sin datos.
- [x] 7 tests en `tests/slices/ruta-invalida/ruta.test.js`. Cobertura 6/6.
- [x] `pintarDesconocida` se prueba **sin navegador** con un contenedor falso: solo asigna `innerHTML`, así
      que lo que se verifica es el marcado que llega al DOM.
- [x] Sin cambios de producción: el pack fija comportamiento existente.
- [x] **Gate 4c — 4 mutantes, 0 supervivientes.** Es lo único que demuestra que estos tests valen:

| Mutante | Resultado |
|---|---|
| `TEMPORADA_RE` acepta cualquier mes de dos dígitos (`2026-13` pasa) | 🔴 |
| `IDENTIFICADOR_RE` acepta cualquier cosa (`/j/pepito` abre ficha) | 🔴 |
| `seccionDe` marca sección en una ruta desconocida | 🔴 |
| la ruta pedida se pinta sin escapar | 🔴 |

- [x] Verificado en navegador: `/t/2026-13`, `/t/2026-08/j/pepito`, `/j/U08U27DFDL2` y `/loquesea` declaran
      «ruta no reconocida» con la ruta pedida y **cero secciones marcadas** en la navegación.
