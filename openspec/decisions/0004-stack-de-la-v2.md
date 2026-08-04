---
adr: 0004
titulo: Stack de la v2.0
estado: propuesto
fecha: 2026-08-04
decide: <pendiente de firma humana>
afecta: [dashboard, estadisticas, ranking]
---

## Contexto

La v1 es un único `index.html` con `js/script.js` (285 líneas, JavaScript vanilla, sin build) que
carga Plotly y `@supabase/supabase-js` desde CDN y pinta cuatro pestañas. Funciona y es trivial de
desplegar: Cloudflare publica los archivos tal cual.

El refactor del 2026-05-26 dejó ese archivo en buen estado (constantes nombradas, `escapeHtml`,
paginación, guards de array vacío), así que **el problema no es la calidad del código actual** sino
lo que la v2.0 va a pedirle: temporadas, podios separados, escala fija comparable entre gráficos,
probablemente filtros y vistas por jugador.

Este ADR queda **propuesto a propósito**: la decisión de stack se toma al definir el roadmap, cuando
esté claro qué features entran. El harness ya está preparado para cualquiera de las opciones
([ADR 0002](0002-harness-en-python.md): el escáner de `@scenarios` entiende Python, JS y TS).

## Opciones

**A. Seguir en vanilla, sin build.**
*Pro:* cero toolchain; el despliegue sigue siendo copiar archivos; nada nuevo que aprender.
*Contra:* los tests del frontend serían solo e2e con Playwright (lentos); no hay forma cómoda de
testear unitariamente el cálculo de estadísticas si vive dentro del mismo archivo que el DOM.

**B. Vanilla con módulos ES + extracción de la lógica pura.**
Separar `stats.js` / `ranking.js` (funciones puras, testeables con Node o con un runner ligero) del
`render.js` que toca el DOM. Sin bundler: `<script type="module">`.
*Pro:* permite unitarios rápidos sobre la parte que importa (medias, temporadas, podios) manteniendo
cero build. *Contra:* los tests de JS necesitan un runner (`node --test` o Vitest) — algo de
toolchain entra.

**C. Framework con build (Vite + TypeScript, con o sin React).**
*Pro:* tipos sobre los datos de Supabase, componentes reutilizables, Vitest.
*Contra:* mete Node/pnpm y un paso de build en el despliegue; es mucho aparato para un dashboard de
cuatro pestañas.

**D. Mover el cálculo al pipeline Python y que la web solo pinte.**
El cron calcula estadísticas y ranking y los deja materializados (tabla o JSON); la web lee resultado
ya cocinado.
*Pro:* todo el dominio testeable con pytest, que ya está montado; la web se simplifica; la captura de
Slack y la web comparten exactamente los mismos números por construcción.
*Contra:* pierde la interactividad de recalcular en cliente (filtros, rangos); añade un artefacto
intermedio que hay que invalidar.

## Decisión

*(En blanco — se firma al definir el roadmap de la v2.0.)*

## Consecuencias

*(Se completa con la decisión.)*
