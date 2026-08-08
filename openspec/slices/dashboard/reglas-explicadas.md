---
slice: reglas-explicadas
status: proposed
kind: action
actor: grupo
trigger:
  type: ui
  surface: web
  detail: "/reglas y /t/<AAAA-MM>/reglas — la página que explica todas las reglas que se aplican"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - ranking
tests_root: tests/slices/reglas-explicadas/
blocked: null
---

# El grupo puede leer todas las reglas que se le aplican

**Actor:** el grupo
**Trigger:** abrir `/reglas`

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
resto del cálculo ([ADR 0008](../../decisions/0008-donde-vive-el-calculo.md)). Consecuencia buscada: una
temporada cerrada conserva las reglas con las que se calculó, así que mirar marzo explica marzo y no el mes
que viene.

## Comportamiento observable

### las-reglas-se-agrupan-por-eje
**WHEN** el grupo abre la página de reglas
**THEN** las ve agrupadas por eje —la temporada y la clasificación, las medallas, las figuras— en lugar de
como una lista plana.

### cada-regla-dice-si-se-aplica
**WHEN** una regla está acordada pero todavía no implementada
**THEN** la página lo dice, en lugar de presentarla como vigente.

### los-parametros-son-los-que-el-calculo-usa
**WHEN** una regla tiene un umbral o un parámetro
**THEN** el número que la página muestra es el que usa el cálculo, no una copia escrita a mano.

### las-reglas-sin-decidir-se-declaran
**WHEN** una regla está en discusión
**THEN** aparece marcada como pendiente y dice **qué falta decidir**, para que el grupo sepa qué tiene sobre
la mesa.

### una-regla-explica-por-que-existe
**WHEN** el grupo lee una regla
**THEN** encuentra qué hace y **por qué está**, no solo su enunciado: una regla sin motivo se lee como
arbitrariedad.

### la-temporada-cerrada-conserva-sus-reglas
**WHEN** se consultan las reglas de una temporada cerrada, en `/t/<AAAA-MM>/reglas`
**THEN** son las que estaban en vigor cuando se calculó, no las de hoy — y navegar a Reglas desde una
temporada conserva esa temporada.

### sin-instantanea-la-pagina-lo-dice
**WHEN** no hay instantánea de la que leer
**THEN** la página lo explica en lugar de quedarse vacía.

## Estado después

Nada cambia en la base de datos por leer las reglas. La página es una vista sobre lo que el pipeline ya
materializa.

## Edge cases

- **Una regla implementada que el grupo no ha votado** —hoy, la temporada 0 y los umbrales de las
  medallas— aparece como aplicada **y** marcada como no votada. Es la información más útil de la página:
  es lo que el grupo tiene que ratificar o tumbar.
- **Una regla con dos consumidores** (el bot y la web) se enuncia una vez: el parámetro sale del mismo sitio
  que el cálculo, así que no puede divergir.
- **Un umbral de figuras sin calibrar** se muestra como pendiente, no como número provisional. Un número
  provisional en una página de reglas se lee como definitivo.

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
