---
slice: tabla-de-datos
status: proposed
kind: action
actor: grupo
trigger:
  type: ui
  surface: web
  detail: "/datos — la tabla cruda: un resultado por fila, tal como está guardado"
events:
  emits: []
  consumes: []
specs:
  - dashboard
tests_root: tests/slices/tabla-de-datos/
blocked: null
---

# El grupo puede ver los datos en crudo, sin cálculo de por medio

**Actor:** cualquiera del grupo
**Trigger:** abrir `/datos`

## Contexto

La v1 tenía una pestaña «Datos» con la tabla en bruto: fecha, usuario, wordle y intentos, de la más reciente
a la más antigua. Es la vista que se mira cuando **no te fías de una cifra**, y por eso conviene portarla
antes de retirar la v1: es lo que permite comprobar que el ranking no se ha inventado nada.

Se porta **tal cual**, con una columna nueva que la v1 no podía tener: **si esa fila cuenta para su
temporada**. Con las reglas nuevas —solo laborables, y un mínimo de jugadores por día— la pregunta «¿por qué
mi resultado del sábado no aparece en el marcador?» tiene respuesta, y su sitio es esta tabla y no un hilo
de Slack.

Esa columna **no recalcula nada**: mira si la jornada está entre los días que la instantánea publica como
válidos ([ADR 0008](../../decisions/0008-donde-vive-el-calculo.md)).

## Comportamiento observable

### la-tabla-lista-todos-los-resultados
**WHEN** se abre la tabla
**THEN** hay una fila por resultado guardado, sin filtrar nada: es la vista cruda, y filtrar sería
justamente lo que impide comprobar el resto.

### orden-de-la-mas-reciente-a-la-mas-antigua
**WHEN** se listan los resultados
**THEN** salen de la fecha más reciente a la más antigua y, dentro del mismo día, en un orden estable, para
que dos cargas no den listas distintas.

### la-tabla-dice-si-una-fila-cuenta-y-por-que
**WHEN** una fila pertenece a una jornada que no forma parte de su temporada
**THEN** la tabla lo declara y dice el motivo: fin de semana, o día sin la muestra mínima.

### la-temporada-de-una-fila-la-decide-el-modelo
**WHEN** una fila es anterior al mes en que empiezan las temporadas numeradas
**THEN** se compara con la instantánea de la **temporada 0**, no con la del mes de su fecha, que no existe
como temporada. El límite se lee de las reglas publicadas y no está escrito en la vista.

### una-fila-de-temporada-sin-materializar-no-afirma-nada
**WHEN** la instantánea de la temporada de una fila no está disponible
**THEN** la tabla no afirma si cuenta ni si no cuenta.

### el-fallo-se-distingue-de-un-seis
**WHEN** un resultado es un fallo
**THEN** se muestra como fallo y no como un 7, que es un número que nadie ha sacado nunca en una partida.

### sin-resultados-la-tabla-lo-dice
**WHEN** no hay resultados
**THEN** lo declara en lugar de mostrar una tabla vacía sin explicación.

## Estado después

Ninguno: solo lee.

## Edge cases

- **Un resultado de una temporada sin instantánea** no bloquea la tabla: sale con su columna en blanco.
- **La tabla entera son miles de filas.** Se vuelcan todas, como en la v1: es una tabla cruda y recortarla
  la haría inútil para lo que sirve. El contenedor tiene su propio desplazamiento.

## Fuera de alcance, y por qué

- **Filtrar y ordenar por columna.** La v1 no lo tenía y nadie lo ha pedido; añadir controles a una vista de
  comprobación es la clase de cosa que se decide viéndola en uso.
- **La figura del patrón.** Vive en Python; la web la pintará cuando la instantánea la publique.
- **Descargar en CSV.** No se ha pedido, y publicar un botón de descarga de datos de personas identificables
  merece decidirse a propósito.

## Slices compañeros

- [[temporada-mensual]] — publica los días válidos de los que sale la columna de si cuenta.
- [[resultado-del-dia]] — la otra vista que declara cuándo una jornada no cuenta, en la que está abierta.
