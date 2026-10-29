---
slice: indicadores-de-juego
status: shipped
kind: action
actor: jugador
trigger:
  type: ui
  surface: web
  detail: "/t/<AAAA-MM>/j/<U…> — el bloque «Cómo juegas» de la ficha: eficiencia, apertura, suerte y acierto más milagroso"
events:
  emits: []
  consumes: []
specs:
  - estadisticas
  - dashboard
tests_root: tests/slices/indicadores-de-juego/
blocked: null
---

# La ficha cuenta cómo juega cada uno: eficiencia, apertura, suerte y su acierto más milagroso

**Actor:** quien mira su ficha o la de otro jugador
**Trigger:** abrir `/t/<AAAA-MM>/j/<U…>`

## Contexto

La media dice cuántos intentos necesita alguien, pero no **por qué**: si abre bien, si exprime cada intento o si la
suerte le acompaña. El dueño pidió que cada uno pueda verlo en su ficha.

Todo sale de la cuadrícula de cada partida y de la respuesta del día. Con los colores de cada fila se estima
cuántas soluciones seguían siendo posibles antes de cada intento —las **candidatas**—. Acertar con una sola
candidata es saber la palabra; acertar con treinta es suerte.

**No hay medidor de trampas.** Con una cuarentena de jugadores, cada mes alguien tiene una racha que por puro azar
solo ocurre un 1–2 % de las veces, y una etiqueta junto al nombre de un compañero en una web pública sería una
acusación hecha por un número. El bloque habla de juego y de suerte, en tono de juego (decisión del dueño).

## Trigger técnico

La ficha lee el bloque `indicadores` de la instantánea de la temporada, que calcula el pipeline en cada
materialización a partir de `wordle_results.pattern` y de la lista de soluciones de La Palabra del Día. La lista
se usa **solo hasta la última jornada jugada** y no se guarda: la instantánea no lleva ninguna palabra.

## Comportamiento observable

### el-bloque-sale-en-la-ficha
**WHEN** se abre la ficha de un jugador con partidas de la temporada
**THEN** aparece el bloque «Cómo juegas» con cuatro indicadores: eficiencia, apertura, suerte y acierto más
milagroso

### la-eficiencia-se-compara-con-el-optimo-y-con-el-grupo
**WHEN** se pinta la eficiencia
**THEN** se ve la media del jugador en la temporada junto a la del grupo y a la de referencia de un solucionador
que conoce la lista de soluciones y elige siempre el intento que más informa

### la-apertura-cuenta-cuantas-quedan-tras-cada-intento
**WHEN** se pinta la apertura
**THEN** se ven las candidatas que le quedan al jugador tras su primer y su segundo intento —la mediana de sus
partidas de la temporada— junto a las del grupo

### la-suerte-son-aciertos-reales-menos-esperados
**WHEN** se calcula la suerte de una partida
**THEN** cada intento suma lo que acertó (1 o 0) menos la probabilidad de acertarlo por azar, uno entre las
candidatas que quedaban; la suerte del jugador es la suma de sus partidas: positiva si acertó más de lo que le
tocaba, negativa si menos

### acertar-sabiendo-la-palabra-no-es-suerte
**WHEN** el intento que acierta llega con una sola candidata posible
**THEN** ese intento suma cero de suerte

### el-acierto-mas-milagroso-es-el-de-mas-candidatas
**WHEN** se pinta el acierto más milagroso
**THEN** es la partida de la temporada resuelta con más candidatas aún posibles, con su jornada, su resultado y
la probabilidad de acertar por azar; a igualdad de candidatas, la jornada más antigua; si siempre acertó con una
sola candidata, se dice así

### con-pocas-partidas-no-hay-conclusiones
**WHEN** el jugador tiene menos partidas con cuadrícula en la temporada que el mínimo para los indicadores
**THEN** el bloque dice cuántas le faltan en lugar de enseñar cifras

### una-cuadricula-incompatible-se-descarta
**WHEN** los colores de una partida no los puede producir ninguna palabra de la lista contra la respuesta del día,
o la partida no tiene cuadrícula
**THEN** esa partida no cuenta para los indicadores y el resto sí

### el-calculo-es-determinista
**WHEN** se materializa dos veces la misma temporada con los mismos resultados y la misma lista
**THEN** los indicadores son idénticos

### la-instantanea-no-lleva-palabras
**WHEN** se materializan los indicadores
**THEN** la instantánea no contiene ninguna palabra de la lista de soluciones, y la lista no se consulta más allá
de la última jornada de la tabla

### sin-lista-no-hay-indicadores
**WHEN** la lista de soluciones no se puede descargar
**THEN** la instantánea se materializa igual sin el bloque, y la ficha dice que los indicadores no están
disponibles mientras el resto se pinta como siempre

### el-bloque-no-habla-de-trampas
**WHEN** se pinta el bloque
**THEN** no contiene las palabras «trampa», «tramposo» ni «sospecha»

## Estado después

La instantánea de cada temporada lleva `indicadores`: por jugador y para el grupo, con la referencia del
solucionador. La ficha pinta el bloque «Cómo juegas». No cambia el esquema ni se escribe nada fuera de
`season_snapshots`.

## Edge cases

- **Respuestas con tilde**: la lista trae tildes y el juego no las distingue al jugar; la Ñ sí es una letra propia.
- **Partidas falladas (X)**: cuentan para la apertura y restan suerte (no acertaron), y no tienen acierto milagroso.
- **Jugador sin cuadrículas** (resultados antiguos sin `pattern`): con pocas partidas, aplica el mínimo.
- **La estimación de candidatas**: no se conocen las palabras probadas, solo sus colores; se estima con la propia
  lista y con un sorteo de semilla fija por jornada. Es una estimación, y el bloque lo dice.

## Slices compañeros

- [[ficha-de-jugador]] — la página donde vive el bloque.
- [[album-de-figuras]] — el precedente: un bloque propio en la ficha, calculado en la instantánea.
- [[palabra-del-dia]] — de donde sale la lista de soluciones y su guardarraíl.
