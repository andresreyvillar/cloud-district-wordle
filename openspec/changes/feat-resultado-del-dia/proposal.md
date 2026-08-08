# Proposal — feat-resultado-del-dia

> **Slice:** `resultado-del-dia` (openspec/slices/estadisticas/resultado-del-dia.md)

## Why

Es la vista que se va a mirar a diario y la única que habla de una jornada **abierta**. Todas las demás
miran periodos cerrados.

Y por eso es la única que tiene que decir algo incómodo: **hoy puede no contar todavía**. Un día entra en la
temporada si es laborable y lo juegan cinco personas, así que a media mañana la jornada existe, tiene
resultados y aún no puntúa.

## What Changes

```
v2/js/data/dia.js        PURO: filas crudas + instantánea → la jornada en curso
v2/js/ui/hoy.js          la vista
v2/js/app.js             /hoy deja de estar pendiente
v2/css/styles.css        tarjetas de resultado, veredicto del día y ausentes
```

## La excepción declarada al ADR 0008

El [ADR 0008](../../decisions/0008-donde-vive-el-calculo.md) dice que Python calcula y la web pinta. **Esta
vista es la excepción, y va declarada:** la jornada abierta no está materializada, el cron corre cada hora y
una hora de retraso en la vista de "hoy" es justo donde más se nota. Así que la media del día se calcula en
el navegador sobre las filas crudas.

Lo que **no** se duplica son los umbrales. La muestra mínima se lee de las reglas que viajan dentro de la
instantánea, que salen de la constante de Python. Un test lo fija: con el umbral publicado en cinco la
jornada no cuenta, con el mismo dato y el umbral en tres sí, **sin tocar la vista**. Y si la instantánea no
trae el umbral, la vista dice que no puede afirmarlo en lugar de asumir un cinco.

## Impact

- Solo lee. Sin efectos en datos.
- Cierra el punto 2.4 de la Fase 2.
- La figura de cada patrón queda fuera: el clasificador está calibrado pero vive en Python, y portarlo a
  JavaScript crearía dos definiciones de la misma regla. Entra cuando la instantánea publique la figura.
