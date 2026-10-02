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

### las-frases-concuerdan-en-numero
**WHEN** una frase nombra a más de una persona
**THEN** el verbo y los sustantivos van en plural, y en singular cuando es una sola; el registro está partido
en dos y se elige por cuántos son, en lugar de mezclar las dos concordancias y acertar la mitad de las veces.

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

### el-comentario-del-dibujo-lleva-la-broma-de-su-categoria
**WHEN** la obra del día es de una categoría con material propio
**THEN** el comentario usa el registro de esa categoría en lugar del genérico, con el nombre de quien la
firmó: el chiste va pegado al dibujo, que es donde el grupo lo espera.

### la-simetria-gana-la-obra-del-dia
**WHEN** dos dibujos de la misma categoría compiten por el premio y uno es simétrico
**THEN** gana el simétrico, por delante de quien tardó más intentos.

### la-obra-del-dia-se-comparte-en-caso-de-empate
**WHEN** varios dibujos empatan en categoría, simetría e intentos
**THEN** el premio es de todos y se nombran todos, en lugar de elegir uno por el orden alfabético; el nombre
sigue ordenando la lista pero ya no decide quién gana.

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

### podio-del-marcador
**WHEN** se compone el resumen y hay clasificados en el marcador general
**THEN** el marcador sale como un **podio ASCII de bloques macizos** dentro de un bloque de código, con su
título encima: el 1º en el centro y más alto, el 2º a la izquierda y el 3º a la derecha, y encima de cada
escalón su puesto, su nombre y su media.

### podio-del-juego
**WHEN** el nivel que se jugó ese día tiene marcas, o la clasificación del juego del mes tiene jugadores
**THEN** después del podio del marcador va una línea con quién ganó ese nivel, su tiempo con centésimas y
cuántos lo terminaron, y debajo el podio del SuperWordleBros del mes con los puntos de cada uno.

### podio-de-figuras
**WHEN** hay jugadores clasificados en el álbum
**THEN** después del podio del juego va el podio de figuras, con la puntuación media de cada uno.

### los-podios-van-en-orden
**WHEN** hay datos para los tres rankings
**THEN** salen en este orden: el marcador general, el SuperWordleBros y las figuras.

### el-empate-comparte-escalon
**WHEN** varios jugadores comparten un puesto del podio
**THEN** sus nombres van juntos en el mismo escalón; si son más de tres, se nombran tres y se dice cuántos más
hay.

### el-podio-cabe-en-el-movil
**WHEN** se pinta un podio
**THEN** ninguna de sus líneas pasa de 32 caracteres, y un nombre de más de 10 se acorta para que quepa en su
escalón.

### un-ranking-sin-datos-no-pinta-podio
**WHEN** uno de los tres rankings no tiene a nadie
**THEN** su podio no sale, y los demás salen igual y en su orden.

### el-mes-arranca
**WHEN** la jornada del resumen es una de las tres primeras que cuentan en la temporada
**THEN** justo antes de los podios va una línea de arranque de mes, y no se habla de ventajas ni de recta
final.

### la-recta-final-cuenta-lo-que-queda
**WHEN** quedan cuatro días laborables o menos en el mes después de la jornada del resumen
**THEN** justo antes de los podios va el bloque de recta final: cuántas jornadas quedan, quién manda y a qué
distancia está el segundo, y que un empate a final de mes **comparte el primer puesto**.

### la-recta-final-dice-si-el-juego-sigue-abierto
**WHEN** el bloque de recta final sale y hay clasificación del juego
**THEN** dice cuántos puntos quedan en juego en el SuperWordleBros —10 por cada nivel del mes que queda por
cerrar— y si el segundo todavía puede alcanzar al primero.

### la-ultima-jornada-se-anuncia
**WHEN** la jornada del resumen es el último día laborable del mes
**THEN** el bloque de recta final lo dice como la última jornada, no como «quedan 0».

### a-mitad-de-mes-no-hay-bloque-de-tension
**WHEN** la jornada no está entre las tres primeras de la temporada ni en la recta final
**THEN** no sale ni la línea de arranque ni el bloque de recta final.

### el-momento-del-mes-sale-de-la-jornada
**WHEN** se decide en qué momento del mes está el resumen
**THEN** se decide con la fecha de la jornada y el calendario, no con el reloj de quien lo ejecuta: el mismo
resumen sale igual lo ejecute quien lo ejecute y cuando lo ejecute.

### un-nombre-no-puede-avisar-a-todo-el-canal
**WHEN** un jugador tiene en su nombre de Slack caracteres con significado para Slack —`<!channel>`, `<@U…>`,
`<https://…|texto>`, `&`—
**THEN** el mensaje que publica el bot los enseña como texto: no avisa a nadie, no crea enlaces y no cambia el
resto del mensaje

### la-participacion-se-comenta-si-es-noticia
**WHEN** la jornada bate el récord de jugadores del canal, trae tres o más debutantes, o junta bastante más
gente de lo normal (un cuarto más que la mediana de las últimas veinte jornadas de temporada)
**THEN** el resumen lo cuenta tras la jornada: cuántos han jugado, si es récord y cuánto es lo normal, y una
coletilla pop que rota por jornada (decisión del dueño, 2026-10-02).

### un-dia-normal-no-habla-de-participacion
**WHEN** la participación de la jornada es la de siempre, o el canal no tiene jornadas anteriores con las que
compararla
**THEN** no sale el bloque: contar cada día cuántos juegan sería ruido, y sin historia no hay récord ni
«normal».

### los-debutantes-se-nombran
**WHEN** hay debutantes —quien publica su primer resultado en el canal— en una jornada que es noticia
**THEN** se les da la bienvenida por su nombre; con más de tres se nombran tres y se resume el resto con
«y N más», para que el mensaje no crezca con el grupo.

### el-ultimo-dia-sale-la-victoria
**WHEN** la jornada del resumen es el último día laborable del mes
**THEN** no se publica el resumen diario: se publica el mensaje de la victoria del mes
([[podio-de-cierre-de-mes]]), que lleva debajo lo esencial de esa última jornada

### sin-jornada-no-hay-resumen
**WHEN** no hay resultados
**THEN** el mensaje no inventa premios: se publica sin las secciones que no tienen datos.

### el-resumen-no-recalcula
**WHEN** se compone el resumen
**THEN** el marcador y el álbum salen del mismo cálculo que publica la web, sin una segunda versión de las
reglas dentro del publicador.

### el-mensaje-no-crece-con-el-grupo
**WHEN** la temporada tiene muchos jugadores
**THEN** el mensaje no crece con ellos: está acotado por construcción —dos líneas, tres podios de tres
puestos con como mucho tres nombres por escalón, y el bloque del momento del mes— y por eso cabe siempre en el
comentario de Slack.

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
