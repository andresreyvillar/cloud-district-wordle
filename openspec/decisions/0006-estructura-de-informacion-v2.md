---
adr: 0006
titulo: Estructura de información y rutas de la v2.0
estado: aceptado
fecha: 2026-08-04
decide: Andrés Rey
afecta: [dashboard, ranking, estadisticas]
---

## Contexto

La v1 es una sola página con cuatro pestañas (Ranking, Estadísticas, Evolución, Datos) que agregan
**todo el histórico** desde el wordle #1419. No hay concepto de temporada, ni forma de mirar un mes
concreto, ni vista de un jugador.

El grupo ha votado (6 a 0) que el ranking pase a ser **mensual con reset el día 1**. Eso no es una
feature que se añada a la estructura actual: la invalida. Una web que agrega todo el histórico no puede
representar un marcador que se reinicia cada mes, y la pregunta "¿quién ganó en marzo?" no tiene dónde
vivir.

Dato que condiciona el diseño: si las temporadas mensuales se aplican al histórico existente, la web
**nace con 9 temporadas cerradas y 6 ganadores distintos**. El archivo no es una promesa a futuro, es
contenido desde el primer día. Y el reset mensual tiene un efecto secundario —se pierde la épica del
acumulado— que un medallero de podios resuelve sin inventar reglas nuevas.

Las demás ideas del hilo de Slack (rachas, remontada, nota ponderada, umbral de participación) **no
están cerradas** y no condicionan esta estructura: son contenido que entra en secciones ya previstas.

## Opciones

**A. Añadir un selector de temporada a las pestañas actuales.**
*Pro:* cambio mínimo. *Contra:* no resuelve "ver temporadas pasadas" como una vista propia; el archivo
y el medallero no tienen sitio; la pestaña "Estadísticas" seguiría mezclando todo el histórico.

**B. Reestructurar por temporada, con secciones y URL propia por vista.**
*Pro:* cada pregunta del grupo tiene una vista y un enlace pegable en el canal; el bot puede enlazar
la temporada cerrada en su mensaje de cierre. *Contra:* obliga a routing y a repensar la navegación.

**C. Una página por temporada, generada.**
*Pro:* URLs estáticas reales, sin routing. *Contra:* requiere paso de generación (build) y no encaja
con la temporada en curso, que cambia a diario.

## Decisión

**Opción B.** La temporada es el eje: un selector global determina el periodo, y las secciones se
resuelven dentro de él. Dos vistas quedan fuera del eje porque son transversales: el archivo de
temporadas y el medallero.

### Secciones del MVP (1 de septiembre)

| Sección | Qué responde | Estado |
|---|---|---|
| **Temporada** | ¿cómo va el mes? Podios y clasificación | núcleo |
| **Temporadas** | ¿quién ganó cada mes? Archivo de las cerradas + medallero acumulado | núcleo |
| **Hoy** | ¿quién ha jugado ya, quién falta, y qué tal se ha dado la palabra? | acordada |
| **Jugador** | ¿cómo voy yo? Palmarés, media por temporada, distribución, evolución | acordada |
| **Datos** | la tabla cruda, para verificar que un resultado se capturó | se mantiene de la v1 |

### Mapa de rutas

```
/                        temporada en curso
/t/<AAAA-MM>             temporada concreta (cerrada o en curso)
/t/<AAAA-MM>/j/<jugador> jugador dentro de esa temporada
/temporadas              archivo + medallero acumulado
/hoy                     el día en curso
/datos                   tabla cruda
```

El identificador de temporada es `AAAA-MM` (legible, ordenable, sin ambigüedad). El identificador de
jugador **no** es el nombre mostrado: eso es exactamente lo que la Fase 1 del roadmap viene a arreglar.
Hasta que exista un identificador estable, la ruta de jugador queda bloqueada por
`identidad-estable-por-id-de-slack` `?` — la forma final del segmento se decide en ese slice.

### Fuera del MVP

| Fuera | Disparador que lo traería |
|---|---|
| Sección de **palabras / dificultad del día** (el día más duro, media del grupo por palabra) | Que el grupo la pida. Los datos ya existen y sale barata: candidata number one para después del 1 de septiembre |
| Comparador entre jugadores | Que alguien lo pida más de una vez |
| Animaciones de evolución entre temporadas | Depende de la escala fija (Fase 4.1); la escala se hace primero |

### Cómo se sirven las URLs

`"not_found_handling": "single-page-application"` en el bloque `assets` de `wrangler.jsonc`: el Worker
sirve `/index.html` con `200 OK` para cualquier ruta que no corresponda a un archivo real
([Cloudflare, SPA routing](https://developers.cloudflare.com/workers/static-assets/routing/single-page-application/)).
Sin build y sin hash en la URL.

## Consecuencias

**Se vuelve fácil:** enlazar una vista concreta en el canal ("mira mi julio"); que el mensaje de cierre
de temporada del bot apunte a la temporada que acaba de cerrar; añadir secciones nuevas (una ruta más);
y responder preguntas que hoy no tienen vista, como quién falta por jugar.

**Se vuelve difícil:** el 404 desaparece. Con el fallback SPA, `/cualquier-cosa` devuelve `index.html`
con 200, así que **la ruta inválida hay que detectarla en cliente** y mostrar algo con sentido. Es un
Requirement de `dashboard`, no un detalle de implementación: si no se hace, un enlace mal escrito
enseña una página vacía.

**Se vuelve difícil también:** la v1 y la v2 dejan de parecerse. Conviven en URLs distintas
([ADR 0005](0005-hosting-y-convivencia-v1-v2.md)) y no hay que intentar que la v1 entienda temporadas.

**Deuda declarada:** la ruta `/t/<AAAA-MM>/j/<jugador>` no se puede especificar hasta que exista
identidad estable. Si la Fase 1 se retrasase, la sección Jugador sale del MVP antes que el resto —
es la única con dependencia dura.
