---
slice: ficha-de-jugador
status: proposed
kind: action
actor: jugador
trigger:
  type: ui
  surface: web
  detail: "/t/<AAAA-MM>/j/<U…> — la ficha de un jugador dentro de una temporada, desde el marcador"
events:
  emits: []
  consumes: []
specs:
  - estadisticas
  - dashboard
  - identidad
tests_root: tests/slices/ficha-de-jugador/
blocked: null
---

# Un jugador puede ver de qué se compone su media

**Actor:** cualquiera del grupo, desde el marcador
**Trigger:** pulsar un nombre en la clasificación

## Contexto

El marcador dice que tu media de temporada es 4,12 y no dice de dónde sale. Con el modelo de imputación eso
ya no es un detalle: **parte de tu media son jornadas que no jugaste**, y un número que penaliza sin poder
mirarse dentro es un número que el grupo no va a aceptar.

Hoy la clasificación lista 21 jugadores y **ninguna fila lleva a ningún sitio**. La ficha es el sitio.

Esta vista **no calcula nada**: todo lo que pinta está ya en la instantánea de la temporada, que es lo que
publica el bot ([ADR 0008](../../decisions/0008-donde-vive-el-calculo.md)). Lo único que arma es el
**palmarés**, y lo arma cruzando instantáneas que la web ya tiene cargadas.

El identificador de la ruta es el **de Slack** y no el nombre: un renombre no puede romper un enlace pegado
en el canal ([ADR 0006](../../decisions/0006-estructura-de-informacion-v2.md), actualización del 2026-08-05).

## Comportamiento observable

### ficha-resume-la-temporada-del-jugador
**WHEN** se abre la ficha de un jugador que jugó la temporada
**THEN** se ven su puesto, su media de temporada, su media de las partidas jugadas, cuántas jornadas jugó de
las que la temporada tiene, y su mejor y su peor partida.

### la-ficha-desglosa-jornada-a-jornada
**WHEN** se mira el desglose de la temporada
**THEN** aparece una entrada por cada jornada con su nota, y **las imputadas se distinguen de las jugadas**,
con la fecha y el número de jornada de cada una.

### la-ficha-dice-lo-que-costo-faltar
**WHEN** un jugador tiene jornadas imputadas
**THEN** la ficha dice cuántas son y cuánto separan su media de temporada de la de sus partidas jugadas, con
el signo explícito: es el número que convierte la regla en algo comprobable.

### distribucion-de-intentos-del-jugador
**WHEN** se mira la distribución
**THEN** hay un recuento por número de intentos, del 1 al fallo, y suma exactamente las partidas jugadas.

### palmares-de-todas-las-temporadas
**WHEN** se mira el palmarés
**THEN** aparece una línea por cada temporada con datos de ese jugador —la 0 incluida—, con su puesto y su
media, ordenadas de la más reciente a la más antigua, y la temporada que se está mirando queda señalada.

### medallas-del-jugador-en-la-temporada
**WHEN** el jugador ganó medallas en esa temporada
**THEN** la ficha las muestra; si no ganó ninguna, lo dice en lugar de dejar el hueco vacío.

### jugador-que-no-jugo-la-temporada
**WHEN** se abre la ficha de un jugador que no tiene resultados en esa temporada
**THEN** la ficha lo dice y ofrece las temporadas en que sí jugó, en lugar de una página vacía o un error.

### el-marcador-enlaza-a-la-ficha
**WHEN** se pinta el marcador de una temporada
**THEN** cada jugador enlaza a su ficha **de esa misma temporada**, con su identificador de Slack en la ruta.

## Estado después

Ninguno: la vista solo lee. No escribe en Supabase, no toca la instantánea y no guarda nada en el navegador.

## Edge cases

- **Una temporada sin imputación** (la 0) no tiene jornadas imputadas, así que el coste de faltar es cero y
  la ficha no inventa una comparación: dice que esa temporada no imputa.
- **Un jugador sin puesto** (por debajo del mínimo de la temporada 0) tiene ficha igual, con su media y su
  desglose, y se declara por qué no ocupa posición.
- **Un identificador que no existe** en ninguna temporada cae en el mismo caso que el jugador sin datos: la
  ficha lo dice. Con el fallback SPA del Worker no hay 404 que lo haga por nosotros.
- **Una temporada con muchas jornadas** (la 0 tiene 181) no cabe como tira de casillas: el desglose se
  agrupa y la tira se omite, igual que ya hace el marcador por encima de 40 jornadas.

## Fuera de alcance, y por qué

- **La gráfica de evolución.** Necesita la escala fija comparable (Fase 4.4) para no mentir al comparar dos
  temporadas; entra con ella.
- **El álbum de figuras del jugador.** El clasificador ya está calibrado, pero el álbum es
  [[album-de-figuras]] (TBD) y tiene su propia decisión de puntuación abierta.
- **Que las medallas se agrupen por identidad y no por nombre.** `tools/badges.py` agrupa por
  `player_name`, que es el fallo que [[identidad-canonica-de-jugador]] arregló en los resultados. Hoy la
  relación es 1:1 y la ficha cruza por nombre; arreglarlo es un slice de identidad, no de esta vista, y va
  declarado aquí para que no se pierda.

## Slices compañeros

- [[clasificacion-de-temporada]] — el marcador desde el que se entra, y la fuente de todo lo que la ficha
  pinta.
- [[identidad-canonica-de-jugador]] — el que hace que el identificador de la ruta sea estable.
- [[temporada-mensual]] — define qué jornadas tiene la temporada, que es el denominador de la ficha.
