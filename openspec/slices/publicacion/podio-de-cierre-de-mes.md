---
slice: podio-de-cierre-de-mes
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0 9 1-7 * * — workflow post_podium.yml: post_podium.py"
events:
  emits: []
  consumes: []
specs:
  - publicacion
tests_root: tests/slices/podio-de-cierre-de-mes/
blocked: null
---

# Al empezar el mes, el canal ve el podio del que cierra

**Actor:** sistema (cron de los primeros días del mes)
**Trigger:** la ejecución programada que publica en el canal

## Contexto

El marcador se reinicia cada mes, y hasta ahora eso pasaba **sin que nadie lo dijera**: un día la tabla
estaba llena y al siguiente vacía. Ni se felicitaba al que había ganado ni se marcaba el arranque.

Este slice publica, una vez al empezar el mes, el podio del mes que cierra —con su imagen— la felicitación al
campeón y el ánimo para la temporada nueva.

## Por qué del 1 al 7 y no solo el 1

**«El primer día de competición del mes» no se puede expresar en cron.** Al restringir día del mes y día de la
semana a la vez, cron los interpreta como **O**: `1-7 * 1-5` dispararía además todos los laborables. Así que la
condición vive en el código y sale de los datos.

Y del 1 al 7 porque el mensaje es idempotente y **GitHub descarta ventanas** —medido en este repositorio, un
86% en los peores días—: si el 1 no corre, se publica el 2 y el cierre no se pierde.

## Comportamiento observable

### el-mes-que-cierra-sale-de-los-datos
**WHEN** se decide qué mes celebrar
**THEN** es el anterior al del último resultado de la tabla, no el que diga el reloj.

### sin-mes-nuevo-no-se-celebra-nada
**WHEN** el mes nuevo todavía no tiene ningún resultado
**THEN** no se publica nada y la ejecución termina bien, porque celebrar «el anterior» sería felicitar otra vez
a quien ganó un mes ya celebrado.

### la-temporada-cero-no-se-celebra
**WHEN** la única temporada anterior es la histórica
**THEN** no se celebra: no cerró un mes, es el bloque anterior a que existieran las temporadas.

### el-podio-lleva-los-empates-enteros
**WHEN** dos personas empatan en un puesto del podio
**THEN** suben las dos, porque cortar por número de filas partiría el empate por la mitad.

### se-felicita-al-campeon-con-sus-medallas
**WHEN** hay un campeón único
**THEN** se le nombra y se enseñan las medallas que ganó **en esa temporada**, de la más difícil a la más común.

### con-empate-en-el-primer-puesto-se-felicita-a-todos
**WHEN** el primer puesto está empatado
**THEN** se felicita a todos los empatados y no se eligen medallas de uno solo.

### el-cierre-no-se-publica-dos-veces
**WHEN** el canal ya tiene el podio de ese mes
**THEN** no se vuelve a publicar y la ejecución termina bien.

### la-imagen-es-la-de-la-web
**WHEN** se publica el podio
**THEN** la imagen es la captura del podio de esa temporada en la web, no un dibujo aparte: así el mensaje y la
página no pueden decir cosas distintas.

## Estado después

El canal recibe un mensaje al mes con el podio del anterior. No se escribe nada en Supabase.

## Edge cases

- **El día 1 a primera hora, sin resultados del mes nuevo**: no se celebra, y se reintenta al día siguiente.
- **Un mes sin nadie clasificado**: no hay podio y no se publica.
- **Salto de meses** (un mes entero sin jugar): no se celebra, porque el mes en curso ha de ser consecutivo al
  cerrado.

## Slices compañeros

- [[resumen-diario-compuesto]] — el mensaje diario, que no cambia.
- [[captura-apunta-a-la-v2]] — la maquinaria de captura que aquí se reutiliza.
- [[archivo-de-temporadas]] — la página de la temporada cerrada que se fotografía.
