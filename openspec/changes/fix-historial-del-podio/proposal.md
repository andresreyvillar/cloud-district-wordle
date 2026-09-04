# El podio de agosto se publicó dos veces

## Qué pasó

```
pos  0  ·  09-04 13:05  ·  Podio del mes · 2026-08   ← el duplicado
pos 44  ·  09-01 13:52  ·  Podio del mes · 2026-08   ← el original
```

La guarda de idempotencia leía **los últimos 30 mensajes** del canal, y el podio original estaba en la
posición **44**. Se había salido de la ventana, la comprobación no lo encontró, y el cron del día 4 lo
republicó.

## Por qué

`mensajes_recientes` se escribió para el **resumen diario**, que reconoce un mensaje publicado minutos antes:
con una ventana de 30 le sobra. El cierre de mes lo reutilizó sin más, y su problema es distinto — el cron
corre **del día 1 al 7**, así que la marca puede estar a siete días de distancia.

Medido, el canal mueve hasta **17 mensajes al día**, unos 120 en esa ventana. Con 30 era imposible que
funcionara más allá del primer día.

Es el mismo fallo de fondo que el del emoji en el título, y el mismo aprendizaje: una guarda de idempotencia
falla en silencio, y falla **publicando**.

## Qué cambia

`mensajes_recientes` gana un parámetro de páginas y pagina con el cursor de Slack. El cierre de mes pide
**cinco páginas** —150 mensajes, con margen sobre los 120 que necesita—; el resumen diario sigue con una, que
es lo que le corresponde.

Se paginan siempre en lugar de parar al encontrar la marca: esto corre una vez al mes, y cinco llamadas de
más no compensan la complejidad.

## Qué no hace

- **No borra el mensaje duplicado.** Ya lo ha visto el grupo; borrarlo del canal es una decisión del dueño, no
  un efecto secundario de arreglar el código.
- No cambia la ventana del resumen diario, que no tiene este problema.
