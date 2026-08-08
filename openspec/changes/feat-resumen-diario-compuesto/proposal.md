# Proposal — feat-resumen-diario-compuesto

> **Slice:** `resumen-diario-compuesto` (openspec/slices/publicacion/resumen-diario-compuesto.md)

## Why

El mensaje diario era una frase fija, las medallas y un enlace. Todo lo que pasó en la jornada estaba en la
captura, que es **una imagen**: no se lee en la notificación del móvil, no se puede citar y no se puede
buscar.

## What Changes

```
tools/resumen.py        NUEVO · PURO: jugador del día, obra del día, top 5 y cabeza del álbum
tools/post_ranking.py   `comentario` acepta los resultados y añade el resumen
tools/local_stack.py    el ensayo en seco imprime el mensaje completo
```

**La captura se conserva.** Sustituirla es una pregunta abierta del brief —menos dependencias frente a
perder el gráfico— y no la decide este slice.

## Decisiones

- **Dos premios y no uno**, por evidencia: exigir mejor puntuación *y* figura reconocible deja el premio
  vacío el 94% de las jornadas. La figura sale de las partidas que salen mal.
- **La rareza sale del reparto de la propia temporada**, no de una tabla escrita a mano: recalibrar el
  clasificador cambia qué figura es rara, y una lista fija se quedaría atrás en silencio.
- **Los empates se nombran todos.** Con diez jugadores y notas de 1 a 7 el empate es lo normal; elegir uno
  por el orden de las filas sería arbitrario y no determinista.
- **El emoji del top es el de hoy.** Poner el de otro día haría que el resumen contase una jornada que no es.
- **Ninguna sección se inventa**: la que no tiene datos no se imprime.

## Dos tests flojos, cazados midiendo

- El del **límite de Slack** comparaba 499 caracteres contra 3000: no ejercitaba nada. Al medirlo se vio que
  el mensaje **está acotado por construcción** —dos líneas, cinco del top, tres del álbum— así que el
  recorte que había escrito era código para un caso imposible. Se quitó, y el escenario pasa a afirmar la
  propiedad de verdad: el mensaje no crece con el grupo.
- El del **jugador del día** afirmaba `"Ana" in texto`, y Ana aparece también en el top y en el álbum: el
  test pasaba aunque el premio se lo llevara otro. Lo cazó el mutante que cambia `min` por `max`.

## Impact

- Cierra el punto 5.5.
- Deja la sección de comentarios (5.6) como lo único que falta del mensaje.
- **No cambia nada en producción hasta mergear**: el cron de `main` sigue publicando el mensaje viejo.
