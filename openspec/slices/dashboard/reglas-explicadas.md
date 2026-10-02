---
slice: reglas-explicadas
status: proposed
kind: action
actor: grupo
trigger:
  type: ui
  surface: web
  detail: "/info — la pestaña Info: cómo se juega, las competiciones, lo que publica el bot y las reglas vigentes; /reglas y /t/<AAAA-MM>/reglas llevan a /info"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - ranking
tests_root: tests/slices/reglas-explicadas/
blocked: null
---

# La pestaña Info explica cómo se juega y las reglas que se aplican

**Actor:** el grupo
**Trigger:** abrir `/info`

## Contexto

Las reglas del juego están decididas en tres sitios distintos —un hilo de Slack, conversaciones de diseño y
briefs del repositorio— y **el grupo no tiene dónde leerlas**. Eso ya ha tenido consecuencias: la regla de
días laborables se aplicó sin que nadie del canal la votase, y el modelo de imputación **cambia quién gana
en 6 de 8 meses** sin que el grupo lo haya visto.

Una clasificación que castiga ausencias y una medalla que exige quince partidas necesitan estar explicadas,
o se leen como arbitrariedad. Esta página es el sitio.

## El riesgo que este slice tiene que evitar

Si el texto se escribe a mano en la web, **la página empezará a mentir** en cuanto alguien recalibre un
umbral: dirá "quince partidas" cuando el código exija catorce. Ese desfase es peor que no tener página,
porque el grupo confiaría en él.

Por eso los parámetros **no se copian**: cada regla referencia la constante que el cálculo usa de verdad, y
un test comprueba que lo que se muestra es lo que se aplica.

## Trigger técnico

La página lee las reglas de la **instantánea de la temporada**, donde el pipeline las materializa junto al
resto del cálculo ([ADR 0008](../../decisions/0008-donde-vive-el-calculo.md)). Info enseña las de la
**temporada en curso**, porque cuenta cómo se juega hoy; cada temporada cerrada sigue guardando en su
instantánea las reglas con las que se calculó.

## Comportamiento observable

### las-reglas-se-agrupan-por-eje
**WHEN** el grupo abre las reglas de Info
**THEN** las ve agrupadas por eje —la temporada y la clasificación, las medallas, las figuras— en lugar de
como una lista plana.

### la-pestana-info-explica-como-se-juega
**WHEN** alguien abre la pestaña Info
**THEN** lee cómo se juega —se juega la palabra de lapalabradeldia.com, se pega el resultado en el canal
#wordle-line y el bot hace el resto—, qué competiciones hay —el marcador, el SuperWordleBros, el álbum de
figuras y las medallas— y qué publica el bot —el resumen de cada noche y la victoria del último día—

### la-explicacion-no-lleva-numeros
**WHEN** se pinta la explicación de Info
**THEN** no escribe ninguna cifra a mano: los números —días, jugadores, puntos, horas— solo aparecen en las
reglas, que los leen de las constantes del cálculo

### solo-se-ensenan-las-reglas-vigentes
**WHEN** se pintan las reglas de Info
**THEN** solo aparecen las que se aplican hoy: ni las propuestas sin decidir, ni las de la temporada 0, ni las
marcas de si el grupo las votó

### el-superwordlebros-tiene-sus-reglas
**WHEN** se pintan las reglas de Info
**THEN** hay un apartado del SuperWordleBros con sus reglas —puntos por puesto, las estrellas por delante del
tiempo, cuándo se congela y se cierra cada nivel, y que el del último día laborable cuenta en el mes
siguiente—, con sus números leídos del código

### los-parametros-son-los-que-el-calculo-usa
**WHEN** una regla tiene un umbral o un parámetro
**THEN** el número que la página muestra es el que usa el cálculo, no una copia escrita a mano.

### las-propuestas-siguen-en-el-catalogo
**WHEN** una regla está en discusión
**THEN** sigue en el catálogo del repositorio diciendo **qué falta decidir**, pero no sale en la web hasta que
se aplica: la pestaña Info cuenta lo que hay, no lo que se discute

### una-regla-explica-por-que-existe
**WHEN** el grupo lee una regla
**THEN** encuentra qué hace y **por qué está**, no solo su enunciado: una regla sin motivo se lee como
arbitrariedad.

### los-enlaces-viejos-llevan-a-info
**WHEN** alguien abre `/reglas` o `/t/<AAAA-MM>/reglas`
**THEN** llega a la pestaña Info, con las reglas vigentes; las de cada temporada siguen guardadas en su
instantánea, pero la web ya no las enseña

### sin-instantanea-la-pagina-lo-dice
**WHEN** no hay instantánea de la que leer
**THEN** la página lo explica en lugar de quedarse vacía.

## Estado después

Nada cambia en la base de datos por leer las reglas. La página es una vista sobre lo que el pipeline ya
materializa.

## Edge cases

- **Una regla implementada que el grupo no ha votado** —los umbrales de las medallas, las reglas del
  SuperWordleBros— sale en Info como vigente, sin marca de votación: a quien juega le basta saber que se
  aplica. Si está votada o no se sigue leyendo en el catálogo (`tools/rules.py`), que es donde se discute.
- **Una regla con dos consumidores** (el bot y la web) se enuncia una vez: el parámetro sale del mismo sitio
  que el cálculo, así que no puede divergir.
- **Un umbral de figuras sin calibrar** no sale en Info hasta que se aplique. Un número provisional en
  una página de reglas se lee como definitivo.

## Fuera de alcance, y por qué

- **Que el grupo pueda votar desde la web.** Las reglas se deciden en el canal, que es donde el grupo
  conversa. La página informa; no es una urna.
- **El histórico de cambios de una regla.** Sería valioso —"esto cambió el 5 de agosto"— pero exige guardar
  versiones, y hoy la instantánea solo tiene la última. Se anota.
- **Explicar el clasificador de figuras en detalle.** Sus umbrales no están calibrados; hasta entonces la
  página dice que el eje existe y que no puntúa todavía.

## Slices compañeros

- [[temporada-mensual]] — materializa la instantánea donde estas reglas viajan.
- [[clasificacion-de-temporada]] (TBD) — el modelo de imputación que esta página tiene que explicar antes de
  que nadie lo sufra en la tabla.
