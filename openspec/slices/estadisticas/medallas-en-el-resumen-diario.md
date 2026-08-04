---
slice: medallas-en-el-resumen-diario
status: proposed
kind: scheduled
actor: grupo
trigger:
  type: cron
  surface: pipeline
  detail: "0 17 * * * — workflow post_ranking.yml: el mensaje que acompaña a la captura"
events:
  emits: []
  consumes: []
specs:
  - estadisticas
  - publicacion
tests_root: tests/slices/medallas-en-el-resumen-diario/
blocked: null
---

# El grupo ve qué medallas lleva ganadas este mes

**Actor:** el grupo (lectores del canal)
**Trigger:** la publicación diaria del resumen

## Contexto

El ranking dice quién va primero, pero no reconoce nada más: quien no falta ni un día, quien resuelve el
día que el resto se atasca o quien acierta a la primera no tiene dónde lucirlo. Las medallas son ese
tercer eje, y no cambian la clasificación
([brief](../../../docs/context/briefs/medallas.md)).

Este slice implementa las **siete que no dependen del clasificador de figuras**, porque sus umbrales
están calibrados contra datos verificados y no van a moverse: solo usan puntuaciones y fechas. Las cinco
de figuras esperan a que el clasificador esté calibrado.

Se calculan, no se guardan. Una medalla es una función de los resultados, así que recalibrar un umbral
recalcula el palmarés histórico sin migrar nada.

## Trigger técnico

El workflow que publica el resumen a las 17:00 UTC compone el texto que acompaña a la captura. Ese texto
gana una sección con **las medallas que alguien ha ganado en esa jornada**, no con el estado acumulado del
mes.

La diferencia se decidió con el ensayo delante: el estado acumulado produce un muro de diez nombres por
línea que se repite idéntico veinte días seguidos, porque las tres medallas comunes las tiene entre el 34%
y el 48% del grupo. Una medalla tiene gracia el día que se gana.

## Comportamiento observable

### medalla-nueva-se-anuncia
**WHEN** un jugador alcanza una medalla en la jornada que se está publicando
**THEN** el texto del resumen la anuncia con su nombre.

### medalla-ya-anunciada-no-se-repite
**WHEN** un jugador ya tenía una medalla antes de la jornada que se publica
**THEN** el resumen no la vuelve a anunciar.

### sin-medallas-no-hay-seccion
**WHEN** en la jornada que se publica nadie ha ganado ninguna medalla nueva
**THEN** el resumen no incluye la sección de medallas, en lugar de mostrarla vacía.

### umbral-exacto-otorga
**WHEN** un jugador alcanza exactamente el umbral de una medalla
**THEN** la medalla se le otorga.

### umbral-por-debajo-no-otorga
**WHEN** un jugador se queda a uno del umbral
**THEN** la medalla no se le otorga.

### dia-imposible-exige-las-dos-condiciones
**WHEN** un jugador resuelve rápido pero el día fue fácil para el grupo, o el día fue duro pero él no lo
resolvió rápido
**THEN** no obtiene la medalla del día imposible, que exige las dos cosas a la vez.

### repeticion-se-cuenta
**WHEN** un jugador cumple la misma medalla de temporada en varias temporadas
**THEN** el resumen muestra cuántas veces la lleva.

### dia-con-poca-muestra-no-cuenta
**WHEN** un día lo juegan menos de cinco personas
**THEN** ese día no cuenta como difícil para ninguna medalla, aunque su media sea alta.

### el-resumen-conserva-lo-que-ya-publicaba
**WHEN** se compone el texto del resumen, con medallas o sin ellas
**THEN** sigue conteniendo el saludo y el enlace a la web que ya publicaba.

### calculo-determinista
**WHEN** se calculan las medallas dos veces sobre los mismos resultados y la misma temporada
**THEN** el resultado es idéntico, sin depender del reloj ni del orden de las filas.

## Estado después

El mensaje publicado en el canal contiene la sección de medallas. **Nada se escribe en la base de datos**:
las medallas son derivadas. El resto del resumen —la captura y el enlace— no cambia.

## Edge cases

- **Temporada recién empezada**: el día 1 nadie cumple umbrales mensuales, así que no hay sección. Es el
  comportamiento correcto, no un vacío que haya que rellenar.
- **Jugador con una sola partida**: no alcanza ningún umbral. Ninguna medalla premia jugar poco.
- **Un día con dos jugadores y media alta** no es un día difícil: es un día sin datos. El escenario
  `dia-con-poca-muestra-no-cuenta` lo fija, y usa el mismo umbral de muestra que el modelo de
  participación para no tener dos definiciones de "día difícil" en el proyecto.

## Slices compañeros

- [[medallas-de-figuras]] (TBD) — las cinco que dependen del clasificador.
- [[resumen-diario-compuesto]] (TBD) — cuando el resumen deje de ser una captura, esta sección se integra
  en el mensaje nuevo.
