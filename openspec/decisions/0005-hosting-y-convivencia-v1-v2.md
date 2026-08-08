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

- La URL es `cloud-district-wordle.clouddistrict.workers.dev` — dominio de Workers. (Era
  `…andres-rey.workers.dev` hasta el 2026-08-07; ver abajo.) Un proyecto Pages
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
(`cloud-district-wordle-2.clouddistrict.workers.dev`), y la v1 **no se mueve**: sigue exactamente donde
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

### Estado del esquema, verificado por SQL

Lo que antes se inferría probando la API REST, ahora está comprobado contra el esquema:

| Elemento | Realidad |
|---|---|
| Clave primaria | `id` (uuid, `gen_random_uuid()`) |
| Unicidad del resultado | **índice único** `idx_slack_user_wordle_unique (slack_user_id, wordle_id)` — no es una constraint; es lo que hace funcionar el `on_conflict` del upsert |
| Columnas obligatorias | `player_name`, `wordle_id`, `score`, `created_at` |
| Columnas nullable | `date` (default `CURRENT_DATE`), `raw_text`, `slack_user_id`, `pattern` |
| RLS | activo, con **una sola política**: `SELECT` para el rol `public` con `qual = true`. No hay política de `INSERT`, `UPDATE` ni `DELETE`, y por eso la clave publicable no puede escribir |
| Advisories de seguridad | ninguno tras la migración de `pattern` |

La ausencia de políticas de escritura es lo que sostiene la seguridad del modelo: la web publica la
clave publicable y con ella solo se puede leer. Cualquier política nueva de escritura rompería esa
garantía y necesita su propio ADR.

**Mecanismo de deploy: CONFIRMADO el 2026-08-07 contra Cloudflare.** La suposición de este ADR era
falsa: no hay Workers Builds, y **el push a `main` no despliega nada**.

| Comprobado | Cómo |
|---|---|
| Cuenta `Andres.rey@clouddistrict.com's Account` (`c266e401…`), subdominio `andres-rey` | `wrangler whoami` |
| Los 10 despliegues del Worker figuran como `Source: Unknown (deployment)`, que es lo que muestra un `wrangler deploy` desde una máquina. Ninguno viene de un build | `wrangler deployments list` |
| **Ningún workflow del repo despliega**: `.github/workflows/` solo tiene los dos cron del pipeline | `grep` |
| El último deploy (2026-05-26 15:25 UTC) es de minutos después del último commit de `main` (17:24 CEST), así que lo publicado **coincide** con `main` — por costumbre de quien despliega, no por automatismo | `git log` + deployments |

**Consecuencia, y es la importante:** *mergear a `main` NO publica la web*. Los cron sí corren desde
`main` (son GitHub Actions), pero los assets solo se publican cuando alguien ejecuta `wrangler deploy`.
Corrige lo que afirmaban el [ADR 0003](0003-modelo-de-ramas-y-despliegue.md) y `CLAUDE.md`.

**Decisión del segundo Worker, ya con datos:** un Worker aparte con su propio config
(`wrangler.v2.jsonc`, `npx wrangler deploy --config wrangler.v2.jsonc`). La objeción que tenía la
opción —«requiere que Workers Builds ejecute ese comando»— **desaparece**, porque no hay Workers Builds:
el deploy es un comando que se lanza a mano, y admite un `--config` sin ceremonia. La alternativa del
`[env.v2]` se descarta: comparte nombre base y `.assetsignore` con la v1, y el objetivo es no tocarla.

**El tercer `?`, el del subdominio: CERRADO el 2026-08-07 cambiándolo.** El subdominio de la cuenta pasó
de `andres-rey` a `clouddistrict`, así que la URL publicada es
`cloud-district-wordle.clouddistrict.workers.dev`.

Se cambia en el dashboard, en **Workers & Pages → panel Account Details → Subdomain**, con el icono de
editar. No hay comando de wrangler ni endpoint que consulte disponibilidad sin escribir: el nombre es único
globalmente y `clouddistrict` estaba libre.

Lo comprobado después del cambio:

| | |
|---|---|
| `cloud-district-wordle.clouddistrict.workers.dev` | **200**, sirviendo la v1 completa. No hizo falta redesplegar: el host es de cuenta, así que el Worker responde en el nuevo al instante |
| `cloud-district-wordle.andres-rey.workers.dev` | **NXDOMAIN**. La URL vieja no redirige: desaparece |

**Alcance real del cambio, menor de lo que este ADR temía:** en la cuenta hay tres aplicaciones, y las otras
dos son proyectos de **Pages** (`tetonor-1xj.pages.dev`, `fuelwatch.pages.dev`). Pages tiene su propio
espacio de nombres, `*.pages.dev`, que **no depende del subdominio de Workers**, así que el renombrado
afectó a un solo host: el de esta web.

**Precio pagado, y era conocido:** los enlaces de todos los mensajes que el bot publicó en el canal durante
meses apuntan a un host que ya no existe. No hay redirección posible.

Para una URL con dominio propio (`wordle.clouddistrict.com`) el camino sigue siendo `Add Domain` / `Add
Route` en la pestaña Domains del Worker, y exige que la zona esté **en esta cuenta**. Es además la única
forma de repartir por ruta —`/2` para la v2—, que `workers.dev` no permite.

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
1. ~~Confirmar el mecanismo de deploy actual en Cloudflare~~ — **hecho el 2026-08-07**, ver arriba. Queda
   solo la pregunta del subdominio, que es de dominio propio y no bloquea el segundo Worker.
2. La URL de la captura de Slack está hardcodeada en un script; al pasar a la v2.0 conviene que sea
   configurable (variable de entorno) en lugar de una constante — candidato a Requirement de
   `publicacion`, no a decisión de este ADR.
3. La retirada de la v1: este ADR no la fija. Cuando llegue, será un ADR nuevo.
