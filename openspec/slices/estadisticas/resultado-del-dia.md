---
slice: resultado-del-dia
status: proposed
kind: action
actor: grupo
trigger:
  type: ui
  surface: web
  detail: "/hoy — la jornada en curso: quién ha jugado, quién falta y cómo se ha dado la palabra"
events:
  emits: []
  consumes: []
specs:
  - estadisticas
  - dashboard
tests_root: tests/slices/resultado-del-dia/
blocked: null
---

# El grupo puede ver cómo va la jornada de hoy

**Actor:** cualquiera del grupo
**Trigger:** abrir `/hoy`

## Contexto

Es la vista que se va a mirar a diario, y la única que habla de una jornada **abierta**. Todas las demás
miran periodos cerrados o casi.

Y por eso es la única que tiene que decir algo incómodo: **hoy puede no contar todavía**. Un día solo forma
parte de la temporada si lo juegan cinco personas y es laborable
([[temporada-mensual]]), así que a media mañana la jornada existe, tiene resultados y **aún no puntúa**.
Callarlo haría que alguien mirara su nota, luego la viera cambiar y pensara que el sistema miente.

## Dónde vive el cálculo, y por qué aquí es distinto

El [ADR 0008](../../decisions/0008-donde-vive-el-calculo.md) dice que Python calcula y la web pinta, para
que el bot y la web no puedan divergir. **Esta vista es la excepción declarada**: la jornada en curso no
está materializada —el cron corre cada hora, y una hora de retraso en la vista de "hoy" es justo donde más
se nota—, así que la media del día se calcula en el navegador sobre las filas crudas.

Lo que **no** se duplica son los umbrales. La muestra mínima se lee de las **reglas que viajan dentro de la
instantánea**, que a su vez salen de la constante que usa el cálculo (`tools/rules.py`). Escribir un `5` en
JavaScript sería exactamente la divergencia que la página de reglas existe para evitar.

## Comportamiento observable

### el-dia-en-curso-se-deriva-de-los-datos
**WHEN** se abre la vista del día
**THEN** la jornada que muestra es la más alta con resultados, no la que diga el reloj del navegador, así que
la vista es reproducible y no queda vacía a las 00:05.

### quien-ha-jugado-aparece-con-su-resultado
**WHEN** hay resultados de la jornada
**THEN** aparece cada jugador con sus intentos, del mejor al peor, y el fallo se distingue de un 6.

### quien-falta-aparece-declarado
**WHEN** algún jugador de la temporada no tiene resultado en la jornada
**THEN** aparece en la lista de quien falta, contado, porque es la mitad de la información del día.

### la-dificultad-del-dia-se-compara-con-la-temporada
**WHEN** hay al menos un resultado
**THEN** se ve la media del día y si ha salido más dura o más fácil que la media de la temporada, con la
diferencia.

### un-dia-que-aun-no-cuenta-lo-dice
**WHEN** la jornada tiene menos resultados que la muestra mínima
**THEN** la vista declara que todavía no cuenta para la temporada y **cuántos faltan** para que cuente.

### un-dia-no-laborable-no-cuenta
**WHEN** la jornada cae en sábado o domingo
**THEN** los resultados se muestran igual y la vista declara que ese día no puntúa, sin importar cuánta gente
haya jugado.

### el-umbral-sale-de-las-reglas-y-no-del-codigo-de-la-vista
**WHEN** se comprueba si la jornada cuenta
**THEN** el número de jugadores mínimo se toma de las reglas publicadas en la instantánea, de modo que
recalibrarlo en Python cambia esta vista sin tocarla.

### sin-resultados-no-hay-jornada
**WHEN** no hay ningún resultado
**THEN** la vista lo dice en lugar de inventar una jornada cero.

## Estado después

Ninguno: solo lee.

## Edge cases

- **Un resultado publicado con retraso** puede hacer que la jornada más alta no sea la de hoy. Es correcto:
  la vista muestra **la última jornada con datos**, y dice su fecha, así que no engaña.
- **Un jugador de la temporada que ya no está en el grupo** aparece como ausente hasta que la temporada
  cambie. Se acepta: la lista de quien falta sale de quien ha jugado la temporada, y no hay padrón.
- **La jornada de hoy con muestra suficiente pero en fin de semana** no cuenta: los dos filtros son
  independientes y hacen falta los dos.

## Fuera de alcance, y por qué

- **La figura de cada patrón.** El clasificador ya está calibrado pero vive en Python; portarlo a
  JavaScript crearía dos definiciones de la misma regla. Entra cuando la instantánea publique la figura.
- **El resumen que publica el bot**: es [[resumen-diario-compuesto]] (TBD), y es otra superficie.
- **Avisar a quien falta.** Escribir en el canal fuera del workflow está prohibido por el propio repositorio.

## Slices compañeros

- [[temporada-mensual]] — de ahí salen los dos filtros que deciden si el día cuenta.
- [[ficha-de-jugador]] — cada jugador del día enlaza a su ficha.
- [[reglas-explicadas]] — publica el umbral que esta vista lee.
