---
slice: empates-comparten-puesto
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0 * * * * — materialize_seasons.py, y de ahí a la web y al resumen diario"
events:
  emits: []
  consumes: []
specs:
  - ranking
tests_root: tests/slices/empates-comparten-puesto/
blocked: null
---

# Dos que empatan comparten puesto

**Actor:** sistema
**Trigger:** el cálculo de la clasificación de una temporada

## Contexto

La tabla ordena por media y reparte puestos **correlativos**: dos jugadores con exactamente 3,58 salen como
2º y 3º. El que queda tercero no ha hecho nada peor que el segundo — la diferencia la decide el desempate
interno, que existe para que el orden sea determinista, no para separar a quien va igual.

En el marcador de la temporada 0 ocurre ahora mismo: Andrés R. y Flavia Venturi, los dos con 3,58.

**No es un detalle raro.** Medido sobre las 186 jornadas que cuentan, el **62%** tiene empate en la mejor
nota del día. Empatar es lo normal en un juego con notas de 1 a 7 y diez jugadores.

## Trigger técnico

`standings.clasificacion`, de donde salen el marcador de la web, la ficha, el archivo y el resumen diario.

## Comportamiento observable

### empatados-comparten-numero
**WHEN** dos jugadores tienen la misma media de temporada
**THEN** ocupan el mismo puesto.

### el-siguiente-salta
**WHEN** dos comparten el puesto 2
**THEN** el siguiente es el 4, no el 3: el hueco dice cuánta gente va por delante.

### el-orden-sigue-siendo-determinista
**WHEN** dos comparten puesto
**THEN** el orden en que se listan sigue siendo el mismo en cada ejecución, aunque el puesto sea el mismo.

### el-empate-se-mide-sobre-la-media-publicada
**WHEN** dos medias difieren solo por debajo de los decimales que se publican
**THEN** cuentan como empate, porque a la vista son el mismo número.

### quien-no-clasifica-sigue-sin-puesto
**WHEN** alguien no llega al mínimo para clasificar
**THEN** sigue sin puesto, y no comparte ninguno.

## Estado después

La clave `posicion` de cada fila puede repetirse. La web y el resumen la pintan tal cual, así que las dos
enseñan lo mismo sin tocarlas.

Con los datos de hoy, la temporada 0 pasa a tener un **2º compartido** entre Andrés R. y Flavia Venturi, y
el siguiente es el 4º.

## Edge cases

- **Empate a tres o más**: todos comparten y el siguiente salta lo que corresponda.
- **Empate en el primer puesto**: hay dos líderes. El titular de la vista lo tiene que decir en plural.
- **Temporada 0**: sin imputación, las medias son de partidas jugadas y los empates son más probables.

## Slices compañeros

- [[clasificacion-de-temporada]] — la tabla a la que afecta.
- [[resumen-diario-compuesto]] — el mensaje que la publica en el canal.
