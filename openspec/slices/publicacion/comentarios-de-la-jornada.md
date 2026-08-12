---
slice: comentarios-de-la-jornada
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
  - estadisticas
tests_root: tests/slices/comentarios-de-la-jornada/
blocked: null
---

# El resumen se ríe de lo que ha pasado hoy

**Actor:** sistema (cron de las 17:00)
**Trigger:** la ejecución programada que publica en el canal

## Contexto

El resumen ya cuenta la jornada ([[resumen-diario-compuesto]]) pero la cuenta en seco. Lo que hace que el
grupo lo lea es el comentario: que alguien resolviera en dos un día imposible, que otro se dejara la
partida, que alguien no apareciera justo el día duro.

**Los hechos se detectan; la gracia se escribe.** Detectar es determinista y se cubre con tests; la
redacción es una plantilla del catálogo. La detección es lo que este slice fija.

**Fuera de alcance: la redacción generativa.** El brief la contempla —un modelo escribiendo el chiste— y no
entra aquí: no hay proveedor decidido ni credencial en el entorno, y llamar a un modelo por jornada tiene un
coste que decide el dueño. La estructura queda preparada: los detectores emiten **hechos**, y quien redacte
—plantilla hoy, modelo mañana— consume esos hechos.

## Trigger técnico

`post_ranking.py`, en la misma composición del mensaje. Los detectores reciben los resultados del día y la
dificultad de la jornada, que ya calcula `standings`.

## Comportamiento observable

### sospechoso-es-el-chiste-raro
**WHEN** alguien resuelve en dos intentos o menos, **sea el día que sea**
**THEN** el resumen le lanza la pulla, sin exigir además que la jornada fuera dura.

Antes hacía falta que la media del grupo fuera alta y el aviso salía en el 6% de las jornadas: casi nunca.
Sin esa condición sale en el **29%** —una de cada tres— y reparte: quien más acumula en todo el histórico
llega a nueve, así que no se ceba con nadie. La pulla no afirma que el día fuera duro, porque ya no lo
comprueba.

### sembrado-y-no-inspirado-son-simetricos
**WHEN** alguien queda muy por debajo o muy por encima de la media del día
**THEN** se comenta, con márgenes calibrados para que ninguno de los dos salga casi a diario.

### rajado-usa-el-modelo-de-dificultad
**WHEN** un día difícil hay gente de la temporada que no publica
**THEN** se comenta la ausencia, usando el **mismo umbral de día difícil** que las medallas y no uno propio.

### el-rezagado-se-nota
**WHEN** el último en publicar llega mucho después que el resto y con el día ya avanzado
**THEN** se comenta; y **solo** si su hora de registro es utilizable, es decir si cae el mismo día que el
puzzle — las filas del backfill se insertaron todas de golpe en otra fecha y su hora no dice nada.

### la-suerte-sospechosa-se-senala
**WHEN** alguien acierta a la primera, o resuelve muy por debajo de la media de un día duro, o publica el
último **y además** con una nota muy por encima de lo que ha hecho el grupo
**THEN** el resumen lo señala, y cuanto más raro es el caso antes sale.

### un-hecho-no-se-repite-en-dos-comentarios
**WHEN** un jugador dispara más de un detector el mismo día
**THEN** aparece una sola vez, con el hecho más notable, en lugar de dos líneas sobre la misma persona.

### los-comentarios-se-limitan
**WHEN** una jornada dispara muchos detectores
**THEN** el resumen publica como mucho unos pocos, para que la sección siga siendo un remate y no un muro.

### sin-hechos-no-hay-seccion
**WHEN** la jornada no dispara ningún detector
**THEN** no hay sección de comentarios, en lugar de una frase de relleno.

### la-frase-concuerda-en-numero
**WHEN** un comentario habla de más de una persona
**THEN** la frase concuerda en número: «no han aparecido» y no «no ha aparecido».

### la-frase-varia-sin-azar
**WHEN** el mismo hecho se detecta en dos jornadas distintas
**THEN** el texto puede variar, pero **de forma reproducible**: dos ejecuciones sobre la misma jornada dan
exactamente el mismo mensaje.

## Estado después

El mensaje diario gana una sección final de comentarios. No se escribe nada en ningún sitio: el resumen es
una lectura.

Frecuencias medidas sobre las 186 jornadas que cuentan, con las reglas actuales:

| Comentario | Disparador | Frecuencia |
|---|---|---|
| Sospechoso | ≤2 intentos con media del día ≥4,0 | 0,07 |
| Sembrado | 1,5 mejor que la media del día | 0,24 |
| No inspirado | 2,0 peor que la media del día | 0,24 |
| Rajado | ausencia en día de media ≥4,5 | 0,18 |

**Las del brief eran otras**, medidas antes de la regla de días laborables: daban 0,71 a «no inspirado» con
margen 1,5, y con las reglas de hoy ese margen da 0,48. El brief ya pedía subirlo a 2,0, y con 2,0 la
frecuencia real es 0,24.

## Edge cases

- **Jornada sin dificultad calculable** (menos de cinco jugadores): no se comenta nada, porque la media del
  día no calibra.
- **Todos empatan**: nadie está sembrado ni sin inspiración, y la sección no aparece.
- **Un jugador dispara dos detectores**: sale una vez.
- **Reejecución**: el mismo día produce exactamente el mismo texto. Sin azar y sin reloj (§10).

## Slices compañeros

- [[resumen-diario-compuesto]] — el mensaje en el que se inserta la sección.
- [[medallas-en-el-resumen-diario]] — de donde sale el umbral de día difícil, que aquí se reutiliza.
