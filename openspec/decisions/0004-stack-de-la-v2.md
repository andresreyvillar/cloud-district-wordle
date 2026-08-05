---
adr: 0004
titulo: Stack de la v2.0
estado: aceptado
fecha: 2026-08-04
decide: Andrés Rey
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

**Opción B: vanilla con módulos ES y la lógica de dominio extraída del render.**

El alcance real de la v2.0 —cinco secciones, selector de temporada y URLs propias por vista
([ADR 0006](0006-estructura-de-informacion-v2.md))— descarta la opción A: no cabe con salud en un
único archivo que mezcla cálculo y DOM. Pero tampoco justifica un bundler: lo que la v2.0 necesita de
verdad es poder **testear el cálculo** (temporadas, elegibilidad, medallero, rachas), y eso se
consigue separando módulos, no añadiendo build.

Estructura acordada:

```
js/
  domain/     ← funciones puras: sin DOM, sin fetch, sin reloj. Testeables con node --test
  ui/         ← render y Plotly: tocan el DOM, se verifican con Playwright
  router.js   ← mapa de rutas → vista
  app.js      ← el borde: carga datos, resuelve la ruta, orquesta
```

Se descarta la opción D (mover el cálculo a Python y que la web solo pinte) pese a ser atractiva
—`pytest` ya está montado y la captura de Slack compartiría números con la web por construcción—
porque introduce un artefacto materializado que hay que invalidar y quita la interactividad de
recalcular en cliente (cambiar de temporada sin ir al servidor). Queda como alternativa si el cálculo
en cliente se vuelve lento o si los números de la web y de la captura llegan a divergir.

Se descartan C y las variantes con framework: superficie de dependencias y paso de build que este
dashboard no necesita.

**Consecuencia técnica verificada:** las URLs limpias no requieren build. Basta añadir
`"not_found_handling": "single-page-application"` al bloque `assets` de `wrangler.jsonc`, y el Worker
sirve `/index.html` con `200 OK` para cualquier ruta que no sea un archivo real
([Cloudflare, SPA routing](https://developers.cloudflare.com/workers/static-assets/routing/single-page-application/)).

## Consecuencias

**Se vuelve fácil:** testear el dominio (una función pura por regla del juego, sin navegador);
desplegar (sigue siendo copiar archivos, sin build que pueda fallar en CI); razonar sobre qué código
toca el DOM y qué código solo calcula. El harness ya reconoce la anotación `@scenarios` en JSDoc sobre
`test()`, así que la cobertura de escenarios funciona sin tocar `tools/wslice`.

**Se vuelve difícil:** garantizar la forma de los datos. Sin tipos, si Supabase devuelve una columna
nueva o un nulo inesperado, se descubre en runtime. Mitigación: un único punto de mapeo en el borde
(hoy `mapRow`) que normaliza y valida, y golden tests sobre el resultado del cálculo.

**Se vuelve difícil también:** compartir código con el pipeline Python. Las reglas de temporada
quedarán implementadas en JavaScript, así que si `tools/post_ranking.py` necesitara calcular lo mismo,
habría duplicación. Hoy no la necesita —captura la web renderizada—, y ese es justo el motivo por el
que la duplicación no aparece.

**Límite declarado:** si aparece un segundo consumidor de las reglas (un endpoint, un bot que responda
en el canal, un export), esta decisión se revisa a favor de la opción D. El disparador es explícito:
**dos consumidores del mismo cálculo**.

> **Actualización 2026-08-05 — el disparador se cumplió y esta parte queda sustituida.** El resumen diario
> en Python y la web pasaron a necesitar las mismas reglas (día laborable, muestra mínima, umbrales de
> medallas, imputación). El [ADR 0008](0008-donde-vive-el-calculo.md) mueve el cálculo a Python con una
> instantánea materializada por temporada. **Lo que este ADR conserva:** vanilla con módulos ES, sin build,
> y `js/domain/` separado del render — pero dentro de `js/domain/` va presentación y formato, no reglas del
> juego.
