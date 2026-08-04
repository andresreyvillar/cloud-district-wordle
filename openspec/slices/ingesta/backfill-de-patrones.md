---
slice: backfill-de-patrones
status: proposed
kind: maintenance
actor: sistema
trigger:
  type: command
  surface: pipeline
  detail: "python3 tools/backfill_patterns.py — ejecución manual puntual"
events:
  emits: []
  consumes: []
specs:
  - ingesta
  - resultados
tests_root: tests/slices/backfill-de-patrones/
blocked: null
---

# El histórico recupera los dibujos que se habían descartado

**Actor:** sistema (ejecución manual)
**Trigger:** comando puntual sobre el pipeline

## Contexto

[[captura-del-patron]] hace que los resultados nuevos guarden su cuadrícula, pero las filas ya
registradas —más de mil quinientas desde noviembre de 2025— se guardaron sin ella. Sin recuperarlas, el
ranking de figuras nacería vacío y tardaría meses en tener material.

El canal **sí conserva los mensajes**: comprobado a 240 días de antigüedad, las cuadrículas siguen
accesibles. El histórico es recuperable.

Este slice **solo rellena patrones**. No inserta resultados, no corrige puntuaciones y no toca
identidades, aunque al recorrer el canal se encuentre con resultados que nunca llegaron a la tabla:
esos son problema de otros slices, y mezclarlo aquí haría imposible revisar el diff.

## Trigger técnico

Un comando que se ejecuta a mano una vez (y se puede repetir sin daño). Recorre el histórico del canal
paginando, extrae el patrón de cada mensaje de resultado con las mismas reglas que la ingesta, y lo
escribe en la fila correspondiente.

La correspondencia entre mensaje y fila se establece por el número de puzzle y el autor del mensaje. La
resolución de identidad es la que ya usa la ingesta hoy: este slice no la mejora ni la cambia `?` — si un
mensaje pertenece a un jugador que la tabla registró con otro nombre, la fila no se encuentra y se
reporta como no resuelta.

## Comportamiento observable

### rellena-filas-sin-patron
**WHEN** el comando encuentra en el canal el mensaje correspondiente a una fila sin patrón
**THEN** la fila queda con el patrón de ese mensaje, en el mismo formato que produce la ingesta.

### no-modifica-filas-con-patron
**WHEN** una fila ya tiene patrón almacenado
**THEN** el comando la deja intacta, de modo que dos ejecuciones seguidas producen el mismo resultado.

### no-inserta-resultados-nuevos
**WHEN** el canal contiene un resultado que no existe como fila en la tabla
**THEN** el comando no crea ninguna fila y lo reporta como resultado sin registrar.

### recorre-todo-el-historico
**WHEN** el histórico del canal excede el tamaño de una página de respuesta
**THEN** el comando continúa por las páginas siguientes hasta agotar el histórico, sin quedarse en la
primera.

### fila-sin-mensaje-se-reporta
**WHEN** una fila sin patrón no tiene mensaje localizable en el canal
**THEN** la fila queda sin patrón y el comando la incluye en su recuento de no resueltas.

### recuento-final
**WHEN** el comando termina
**THEN** informa de cuántas filas ha rellenado, cuántas ha dejado intactas y cuántas no ha podido
resolver.

### ensayo-no-escribe
**WHEN** el comando se ejecuta en modo ensayo
**THEN** produce el mismo recuento que produciría la ejecución real, sin modificar ninguna fila.

## Estado después

Las filas del histórico con mensaje localizable tienen patrón; el resto sigue sin él y consta en el
recuento. Ninguna otra columna cambia. La tabla no gana ni pierde filas: el número de resultados antes y
después es idéntico.

## Edge cases

- **Reejecución**: es idempotente por diseño (`no-modifica-filas-con-patron`), así que se puede lanzar
  varias veces mientras se depuran los casos no resueltos.
- **Límite de la API de Slack**: el recorrido consume la cuota de lectura del canal. El comando es
  manual y puntual, no programado, precisamente para no competir con la ingesta horaria.
- **Mensajes de resultado en hilos**: no se recuperan, porque el histórico del canal solo devuelve
  mensajes raíz. Es la misma limitación que tiene hoy la ingesta y se resuelve en su propio slice
  [[resultados-publicados-en-hilos]] (TBD).

## Slices compañeros

- [[captura-del-patron]] — aporta el formato del patrón y las reglas de extracción que este slice reutiliza.
- [[resultados-publicados-en-hilos]] (TBD) — ingesta de los resultados publicados dentro de hilos.
