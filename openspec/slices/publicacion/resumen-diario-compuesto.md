---
slice: resumen-diario-compuesto
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0 17 * * 1-5 — workflow post_ranking.yml: post_ranking.py"
events:
  emits: []
  consumes: []
specs:
  - publicacion
tests_root: tests/slices/resumen-diario-compuesto/
blocked: null
---

# El mensaje diario cuenta la jornada, no solo enseña una foto

**Actor:** sistema (cron de las 17:00, de lunes a viernes)
**Trigger:** la ejecución programada que publica en el canal

## Contexto

El mensaje diario es hoy una frase fija, la sección de medallas y un enlace. Todo lo que pasó en la jornada
—quién ganó, qué se dibujó, cómo va el mes— está en la captura, que es una imagen: no se puede leer en la
notificación del móvil, no se puede citar y no se puede buscar.

Este slice compone **el texto**: jugador del día, obra del día, top 5 con el dibujo de cada uno y cabeza del
ranking de belleza. Los comentarios jocosos llegan aparte ([[comentarios-de-la-jornada]] (TBD)).

**Dos premios y no uno.** Medido sobre 17 jornadas: exigir mejor puntuación *y* figura reconocible deja el
premio vacío el 94% de los días, porque la figura sale de las partidas que salen mal. Por eso jugador del
día y obra del día son premios distintos, y casi nunca los gana la misma persona.

**La captura se conserva.** Sustituirla es una pregunta abierta del brief —se ganan dependencias menos y se
pierde el gráfico— y no la decide este slice: el texto se añade al mensaje que ya lleva la imagen.

## Trigger técnico

`post_ranking.py`, que el workflow `post_ranking.yml` ejecuta a las 17:00 de lunes a viernes. El texto va en
`initial_comment` de la subida a Slack, que es donde hoy va la frase fija.

La jornada y la temporada se derivan **de los datos**, no del reloj (§10).

## Comportamiento observable

### jugador-del-dia
**WHEN** se compone el resumen de una jornada
**THEN** nombra a quien mejor puntuación hizo ese día, y si hay empate los nombra a todos.

### obra-del-dia
**WHEN** alguien dejó una figura reconocible ese día
**THEN** se premia la **más rara de la temporada**, con su emoji y su autor; y si nadie dibujó nada
reconocible, el premio se declara desierto en lugar de dárselo a un abstracto.

### top-cinco-con-su-dibujo
**WHEN** se compone el resumen
**THEN** aparecen los cinco primeros del marcador con su media, y junto a cada uno el emoji de lo que
dibujó **ese día**; quien no jugó no lleva emoji.

### cabeza-del-album
**WHEN** hay jugadores clasificados en el álbum
**THEN** el mensaje muestra los tres primeros con su tasa y su tira agrupada.

### sin-jornada-no-hay-resumen
**WHEN** no hay resultados
**THEN** el mensaje no inventa premios: se publica sin las secciones que no tienen datos.

### el-resumen-no-recalcula
**WHEN** se compone el resumen
**THEN** el marcador y el álbum salen del mismo cálculo que publica la web, sin una segunda versión de las
reglas dentro del publicador.

### el-mensaje-no-crece-con-el-grupo
**WHEN** la temporada tiene muchos jugadores
**THEN** el mensaje no crece con ellos: está acotado por construcción —dos líneas, cinco del top y tres del
álbum— y por eso cabe siempre en el comentario de Slack.

### el-resumen-se-enciende-con-una-variable
**WHEN** se despliega el código nuevo sin encender nada
**THEN** el mensaje del canal es exactamente el de siempre; el resumen se activa cambiando una variable del
repositorio, no desplegando.

## Estado después

El mensaje del canal pasa de tres líneas a un resumen con secciones, y **sigue llevando la captura**. No se
escribe nada nuevo en Supabase: el resumen es una lectura.

Ninguna sección se inventa: la que no tiene datos no aparece.

## Edge cases

- **Nadie dibujó nada reconocible**: la obra del día queda desierta y se dice.
- **Empate en la mejor puntuación**: se nombran todos. Con diez jugadores y notas de 1 a 7, el empate es lo
  normal, no la excepción.
- **La temporada en curso sin álbum** (agosto de 2026: 61 de 80 partidas sin patrón): la sección del álbum
  no aparece.
- **Jornada de fin de semana**: el cron solo corre de lunes a viernes, pero si se ejecutase a mano, la
  jornada no cuenta para la temporada y el resumen lo refleja porque usa el mismo cálculo.

## Slices compañeros

- [[comentarios-de-la-jornada]] (TBD) — la sección jocosa, que llega después.
- [[medallas-en-el-resumen-diario]] — la sección de medallas, que ya existe y se conserva.
- [[album-de-figuras]] — la tira agrupada que aquí se reutiliza.
- [[captura-apunta-a-la-v2]] — de dónde sale la imagen que sigue acompañando al texto.
