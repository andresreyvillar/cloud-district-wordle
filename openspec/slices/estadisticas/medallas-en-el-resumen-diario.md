---
slice: medallas-en-el-resumen-diario
status: proposed
kind: scheduled
actor: grupo
trigger:
  type: cron
  surface: pipeline
  detail: "0 17 * * 1-5 — workflow post_ranking.yml: el mensaje que acompaña a la captura"
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

**Solo cuentan los días laborables** (regla de temporada acordada, ver
[brief](../../../docs/context/briefs/reglas-temporadas.md)). Las partidas de sábado y domingo se siguen
capturando y guardando, pero no cuentan para ninguna medalla. Sin esta regla, `Metrónom@` es inganable: los
días de la temporada se derivan de los datos, así que **una sola persona jugando un domingo se lo bloquea
a todo el grupo** — medido, 0 de 123 parejas jugador-mes lo logran; con la regla, 6.

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

### partida-de-fin-de-semana-no-cuenta-para-umbrales
**WHEN** un jugador tiene partidas en sábado o domingo
**THEN** esas partidas no cuentan para los umbrales de ninguna medalla, ni para bien ni para mal.

### fin-de-semana-no-fija-dificultad
**WHEN** un sábado o domingo lo juegan cinco personas o más y su media es alta
**THEN** ese día tampoco cuenta como difícil: la regla no depende de que el fin de semana tenga poca
muestra, sino de que no es día de temporada.

### metronomo-solo-exige-los-dias-laborables
**WHEN** un jugador juega todos los días laborables de la temporada, y otra persona además jugó un domingo
**THEN** obtiene Metrónom@, porque el domingo no es un día de la temporada que él haya faltado.

### jornada-de-fin-de-semana-no-anuncia-medallas
**WHEN** la jornada que se publica cae en sábado o domingo
**THEN** el resumen no anuncia ninguna medalla nueva, porque en un día que no cuenta no se gana nada.

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
- **Una temporada que solo tenga fines de semana** no otorga nada, igual que una recién empezada. No es
  un caso hipotético: pasa en agosto de 2026, cuyos días 1 y 2 son sábado y domingo.
- **Un jugador que solo juega los fines de semana** no obtiene ninguna medalla. Es la consecuencia
  aceptada de la regla, no un efecto colateral: sus partidas siguen guardadas y visibles.

## El cron también es de lunes a viernes

El workflow pasa a `0 17 * * 1-5`. No es cosmético: la jornada se deriva de `max(wordle_id)` de los datos,
y en fin de semana no llegan filas nuevas, así que **un cron dominical habría republicado la jornada del
viernes con sus medallas**. Comprobado antes de cambiarlo, ejecutando `seccion_de_medallas` tres veces
sobre los mismos datos: devuelve el mismo texto las tres. Con el cron restringido, el caso no ocurre.

La ingesta **no** se restringe: `update_stats.yml` sigue corriendo cada hora los siete días, que es lo que
mantiene la decisión de seguir capturando y guardando los resultados de fin de semana.

Queda un caso residual, y no lo arregla este slice: si un lunes a las 17:00 UTC nadie ha publicado todavía,
la última jornada con datos sigue siendo la del viernes y el mensaje repetiría sus medallas. Exige decidir
qué publica el resumen un día sin jornada nueva, y eso es [[resumen-diario-compuesto]] (TBD).

## Fuera de alcance, y por qué

`ser el mejor del día` (Verdugo) **no exige muestra mínima**, así que un día laborable de dos jugadores
otorga el crédito igual. Medido: 25 de los 447 créditos históricos salen de días con menos de cinco
jugadores; la regla de días laborables solo tapa 10 de esos 25. Corregirlo es una regla distinta —¿el
mejor del día exige muestra?— que el grupo tiene que decidir, y va anotada como abierta en
[el brief](../../../docs/context/briefs/medallas.md). Este slice no la toca.

## Slices compañeros

- [[medallas-de-figuras]] (TBD) — las cinco que dependen del clasificador.
- [[resumen-diario-compuesto]] (TBD) — cuando el resumen deje de ser una captura, esta sección se integra
  en el mensaje nuevo.
