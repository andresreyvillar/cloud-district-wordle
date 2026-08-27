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

### los-premios-de-la-misma-persona-se-dicen-una-vez
**WHEN** alguien es protagonista único de dos o más reconocimientos de la jornada
**THEN** se dicen en una sola línea en lugar de una por premio; y **no se reparten a otra gente**, porque
cederle el premio al segundo para hablar de más personas sería falsear quién ganó qué.

### el-mensaje-tiene-una-sola-voz
**WHEN** se compone el resumen
**THEN** las frases con tono —la pulla, el conector y el cierre— salen todas del mismo estado de ánimo de la
jornada, derivado de los datos, en lugar de que cada bloque elija del suyo.

### lo-mas-notable-abre-el-comentario
**WHEN** la jornada tiene un hecho notable
**THEN** ese hecho es la primera línea, y no queda enterrado detrás de los datos de rutina.

### la-segunda-linea-se-encadena-con-la-primera
**WHEN** la segunda línea habla de la misma persona que la primera
**THEN** se une a ella con un conector del estado de ánimo; y si cambia de sujeto, no se encadena.

### la-jornada-se-cuenta-en-lugar-de-rotularse
**WHEN** se compone el resumen
**THEN** la jornada se cuenta en frases —cómo de dura fue comparada con la temporada, quiénes fueron los
mejores, de quién es el mejor dibujo, quién abrió y quién no apareció— en lugar de rotular cada dato con su
título.

### quien-abre-por-costumbre-se-distingue-de-quien-abre-un-dia
**WHEN** quien abrió la jornada ha abierto además la mayoría de las jornadas recientes
**THEN** se dice que es su costumbre, con el recuento; y si no, solo que hoy abrió.

### los-ausentes-se-nombran-por-orden-de-clasificacion
**WHEN** faltan más personas de las que se pueden nombrar
**THEN** los que se nombran son los **mejor clasificados** de entre los ausentes, porque la ausencia de quien
va primero es más noticia que la de quien va último; y no se nombran por orden alfabético.

### los-ausentes-se-nombran-sin-listarlos-todos
**WHEN** falta más gente de la que se puede nombrar
**THEN** se nombran unos pocos y el resto se resume, de modo que el mensaje no crezca con el grupo.

### obra-del-dia
**WHEN** alguien dejó una figura reconocible ese día
**THEN** se premia la **más rara de la temporada**, con su emoji y su autor; y si nadie dibujó nada
reconocible, el premio se declara desierto en lugar de dárselo a un abstracto.

### la-simetria-gana-la-obra-del-dia
**WHEN** dos dibujos de la misma categoría compiten por el premio y uno es simétrico
**THEN** gana el simétrico, por delante de quien tardó más intentos.

### el-relevo-en-cabeza-se-anuncia
**WHEN** la jornada de hoy cambia quién manda en el marcador
**THEN** el mensaje lo anuncia nombrando a quien sube y a quien cae; y no lo anuncia cuando el cambio es solo
el desempate alternando entre dos que van igualados, ni cuando la temporada aún no tiene jornadas previas
suficientes para que «antes» signifique algo.

### la-tendencia-del-mes-acompana-al-relevo
**WHEN** el relevo se anuncia y la cabeza ya había cambiado antes ese mes
**THEN** se añade cuántas veces ha cambiado y el reparto de jornadas **de los dos que se la juegan**; con un
solo cambio no se añade nada, porque «y van 1 cambios» no es una tendencia.

### el-dominio-en-cabeza-se-cuenta
**WHEN** nadie le quita la cabeza al líder desde varias jornadas seguidas
**THEN** se dice cuántas lleva, en el **mismo hueco** que el relevo —así el mensaje nunca lleva dos líneas de
liderazgo—; y no se dice de dos empatados, porque un empate no es dominio de nadie.

### la-tension-sube-cuando-el-empate-se-repite
**WHEN** la misma pareja vuelve a empatar en cabeza en la temporada
**THEN** la frase sube de tono con las veces que llevan —neutra la primera, insistente a partir de la segunda
y tensa a partir de la cuarta— y dice cuántas son; la escalada va por **veces que se repite**, no por
jornadas seguidas, porque un empate casi nunca dura dos jornadas.

### la-pelea-por-el-primer-puesto-se-cuenta
**WHEN** el primer puesto está empatado o la ventaja del líder se remonta en una jornada
**THEN** el mensaje lo dice nombrando a quienes se lo juegan; y con ventaja amplia no se inventa rivalidad.

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
