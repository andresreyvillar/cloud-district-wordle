---
adr: 0005
titulo: Hosting de la v2.0 y convivencia con la v1
estado: aceptado
fecha: 2026-08-04
decide: Andrés Rey
afecta: [dashboard, resultados, publicacion]
---

## Contexto

La v1 **no está en Cloudflare Pages**, como se asumía: es un **Worker con Static Assets**. La
evidencia es concluyente:

- La URL es `cloud-district-wordle.andres-rey.workers.dev` — dominio de Workers. Un proyecto Pages
  serviría en `*.pages.dev`, y ni `cloud-district-wordle.pages.dev` ni
  `cloud-district-wordle.andres-rey.pages.dev` resuelven.
- `wrangler.jsonc` declara `"assets": { "directory": "." }`, que es la configuración de Workers
  Static Assets (sucesora de Workers Sites, ya deprecado).
- No hay Worker script: solo assets servidos desde el edge (`cf-cache-status: HIT`).

Eso importa porque la plataforma condiciona la v2.0, y la recomendación de Cloudflare es explícita:
para proyectos nuevos, Workers en lugar de Pages — *"all investment, optimizations, and feature work
will be dedicated to improving Workers"*
([Workers Best Practices](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/)).
Las peticiones a assets estáticos no se facturan
([Static Assets](https://developers.cloudflare.com/workers/static-assets/)).

Conclusión de partida: **no hay nada que migrar**. La pregunta real no es dónde alojar la v2.0, sino
cómo convivirá con la v1 mientras se desarrolla, en dos planos que se suelen confundir:

1. **Hosting** — dos URLs, trivial.
2. **Datos** — las dos versiones leen la MISMA tabla de Supabase. Si la v2.0 añade temporadas o
   fusiona los jugadores duplicados, la v1 empieza a mostrar números distintos a los que mostraba,
   porque el dato de debajo cambió. Deja de ser un archivo histórico y pasa a ser una segunda vista
   de datos nuevos con código viejo.

Hay un tercer detalle operativo: `tools/post_ranking.py:14` tiene la URL hardcodeada, así que la
captura diaria que ve el grupo seguirá apuntando a la v1 hasta que alguien cambie esa línea.

## Opciones

### Hosting

**A. Worker nuevo en `workers.dev`.** Segundo Worker, la v1 intacta en su URL.
*Pro:* gratis, inmediato, sin DNS, sin tocar producción. *Contra:* dos deploys que mantener, y la
URL que el grupo ya conoce se queda con la versión vieja hasta el corte.

**A'. La v2 hereda la URL actual y la v1 se aparta** a `cloud-district-wordle-v1`.
*Pro:* el grupo no aprende una URL nueva; la captura diaria de Slack no habría que tocarla.
*Contra:* obliga a republicar la v1 en otro nombre **antes** del corte, y a hacer coincidir dos
despliegues en el tiempo. Toca producción para conseguir algo que se resuelve cambiando una línea.

**B. Dominio propio para las dos** (`wordle.<dominio>` y `v1.wordle.<dominio>`).
*Pro:* presentable, sobrevive a cambios de plataforma. *Contra:* requiere la zona en Cloudflare y
decidir el dominio ahora, cuando la v2.0 aún no existe.

**C. Solo preview por rama.** Workers Builds sirve la rama en una URL de preview.
*Pro:* cero configuración. *Contra:* la URL cambia en cada build; no sirve para compartirla con el grupo.

**D. Reemplazar en sitio.** La v2.0 sustituye a la v1 en la misma URL.
*Pro:* un solo deploy. *Contra:* se pierde la referencia visual de la v1 (solo queda en git).

### Datos

**A. Misma BD, cambios solo aditivos.** Una tabla; la v2.0 añade columnas y nunca rompe lo que la v1
lee. *Pro:* cero trabajo extra, una sola fuente de verdad. *Contra:* la v1 mostrará datos nuevos,
incluidas las identidades ya fusionadas — no es un archivo, es una vista antigua de datos vivos.

**B. La v1 pasa a foto fija.** Exportar el estado actual a JSON y que la v1 lea de ahí. *Pro:* archivo
real de la temporada 1, inmune a la v2.0. *Contra:* un slice más, y dos fuentes de verdad que pueden
divergir sin que nadie se dé cuenta.

## Decisión

**Hosting: opción A.** La v2.0 vive en un Worker nuevo llamado **`cloud-district-wordle-2`**
(`cloud-district-wordle-2.andres-rey.workers.dev`), y la v1 **no se mueve**: sigue exactamente donde
está, con su nombre y su URL.

Se descarta A' (que la v2.0 heredase la URL actual) por una razón de riesgo, no de estética:
apartar la v1 obliga a republicarla bajo otro nombre y a coordinar dos despliegues en el tiempo,
tocando lo único que hoy funciona en producción. El beneficio que compra —no cambiar una URL— se
consigue igual editando una línea (`tools/post_ranking.py:14`) cuando la v2.0 esté lista.

El dominio propio queda aplazado, no descartado: añadir un custom domain a un Worker existente no
rompe nada, y decidirlo ahora obligaría a elegir dominio antes de saber qué es la v2.0.

**Datos: opción A, con una invariante dura.** Una sola tabla `wordle_results`. Mientras la v1 esté
publicada, **todo cambio de esquema es aditivo**: se añaden columnas, nunca se renombra ni se elimina
lo que la v1 lee (`player_name`, `wordle_id`, `score`, `date`). Se acepta explícitamente la
consecuencia: la v1 no es un archivo histórico, es la vista antigua de los datos actuales. Si en algún
momento se quiere un archivo de verdad, es la opción B y merece su propio ADR.

**Mecanismo de deploy: pendiente de confirmar.** El repo no tiene workflow de despliegue, así que el
deploy lo dispara Cloudflare al detectar el push (Workers Builds conectado al repositorio) `?`. Hay
dos formas de montar el segundo Worker y la elección depende de cómo esté configurado hoy:

- **Environment** en `wrangler.jsonc` (`[env.v2] name = "wordle-v2"`), desplegado con
  `wrangler deploy --env v2`. Requiere que el proyecto de Workers Builds ejecute ese comando `?`.
- **Segundo proyecto de Workers Builds** apuntando a la rama de la v2.0 con su propio nombre de
  Worker. Más simple si el deploy actual es el `wrangler deploy` por defecto `?`.

Los tres `?` se resuelven mirando la configuración real en Cloudflare (dashboard o MCP autenticado)
antes de escribir el pack que lo implemente. **No se elige el mecanismo a ciegas.**

## Consecuencias

**Se vuelve fácil:** desarrollar la v2.0 sin miedo a romper lo que el grupo usa a diario; comparar las
dos versiones lado a lado; añadir un dominio propio más adelante; y si la v2.0 necesita una función de
servidor (ocultar la clave de Supabase, recibir eventos de Slack), cabe en el mismo Worker sin cambiar
de plataforma — que es justo lo que Pages haría incómodo.

**Se vuelve difícil:** cambiar el esquema con libertad. La invariante aditiva es una restricción real
sobre los slices de `resultados` e `identidad`: fusionar jugadores duplicados no puede hacerse
borrando `player_name`. Y hay dos deploys que vigilar.

**El corte, cuando llegue, es una línea.** La v2.0 se considera "la que ve el grupo" el día que
`tools/post_ranking.py:14` apunte a `cloud-district-wordle-2`. Ese cambio es el único acto de corte, y
es reversible en un commit. Hasta entonces la v2.0 existe, es visitable y no molesta a nadie.

**Queda pendiente y con dueño:**
1. Confirmar el mecanismo de deploy actual en Cloudflare (los tres `?` de arriba) **antes** de escribir
   el pack que cree el segundo Worker. Nada de elegir el mecanismo a ciegas.
2. La URL de la captura de Slack está hardcodeada en un script; al pasar a la v2.0 conviene que sea
   configurable (variable de entorno) en lugar de una constante — candidato a Requirement de
   `publicacion`, no a decisión de este ADR.
3. La retirada de la v1: este ADR no la fija. Cuando llegue, será un ADR nuevo.
