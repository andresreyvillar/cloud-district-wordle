---
slice: palabra-del-dia
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0 22 * * 1-5 — workflow post_ranking.yml: post_ranking.py"
events:
  emits: []
  consumes: []
specs:
  - publicacion
tests_root: tests/slices/palabra-del-dia/
blocked: null
---

# El mensaje abre diciendo qué palabra era y qué significa

**Actor:** sistema (cron del resumen)
**Trigger:** la ejecución programada que publica en el canal

## Contexto

El grupo comparte cuadrículas de colores durante todo el día y **nadie ve nunca la palabra escrita**. Cada uno
sabe la suya y ya. Menos aún su significado: varias de las jugadas son palabras que casi nadie usa —`vitre`,
`agraz`, `taxón`, `merlo`—.

Este slice pone la palabra y su primera acepción **al principio del mensaje**, que es lo único que el mensaje
puede aportar que el grupo no tenga ya.

## Por qué a medianoche de Madrid

El juego avanza su índice a medianoche de **Nueva York**, que son las 06:00 de Madrid. A las 00:00 de Madrid la
palabra sigue siendo la que el grupo ha jugado todo el día, así que coincide con la jornada que resume el
mensaje. A cualquier otra hora habría desfase de un día.

Y el riesgo de destripar la partida está medido: **2 de 1748 resultados** del canal se publicaron entre las
00:00 y las 06:00 de Madrid, un 0,1%.

## Trigger técnico

`post_ranking.py`. La palabra se busca en el **borde** —el cron— y entra en el compositor por parámetro, igual
que las señales del canal: `resumen.py` no toca la red y el mensaje sigue fijándose en un test.

## Comportamiento observable

### la-palabra-abre-el-mensaje
**WHEN** se conoce la palabra de la jornada
**THEN** el mensaje empieza con ella en mayúsculas y su primera acepción.

### sin-acepcion-se-publica-la-palabra-sola
**WHEN** la palabra no tiene definición disponible
**THEN** se publica la palabra sin acepción, en lugar de callarse las dos cosas.

### sin-palabra-el-mensaje-sale-igual
**WHEN** no se puede averiguar la palabra
**THEN** el mensaje se publica sin esa línea, como cualquier sección sin datos, y la ejecución no falla.

### nunca-una-palabra-sin-jugar
**WHEN** se pide la palabra de una jornada posterior a la última que hay en la tabla
**THEN** no se devuelve, aunque esté disponible en el origen: el sistema no puede entregar respuestas de
partidas que el grupo todavía no ha jugado.

### la-acepcion-se-recorta-para-caber
**WHEN** la acepción es más larga de lo que cabe en una línea
**THEN** se corta por la primera frase, o por la última palabra entera, y nunca a mitad de palabra.

### la-definicion-se-busca-tambien-con-mayuscula
**WHEN** la palabra no tiene entrada en minúsculas
**THEN** se prueba con mayúscula inicial, porque los nombres propios están capitalizados.

### nada-de-la-palabra-se-guarda
**WHEN** se publica el mensaje
**THEN** ni la palabra ni la lista de soluciones se escriben en ningún sitio: se leen, se usan y se descartan.

## Estado después

El mensaje diario gana una línea de apertura. No se escribe nada en Supabase.

## Edge cases

- **El origen no responde**: no hay línea y el resumen sale igual.
- **La palabra no está en el Wikcionario** (`vitre`, medido 1 de 25): sale la palabra sin acepción.
- **El nombre propio en minúsculas** (`troya`): se resuelve con el respaldo por mayúscula.

## Slices compañeros

- [[resumen-diario-compuesto]] — el mensaje al que se le añade la línea.
- [[captura-apunta-a-la-v2]] — el flujo de publicación donde vive el borde.
