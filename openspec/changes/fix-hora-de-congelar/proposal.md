# El nivel se congela a las 02:00

> Slice: `nivel-congelado` (modificación).

## Por qué

El dueño adelanta la hora de congelar de las 04:00 a las **02:00**, para que el nivel de la jornada de ayer
llegue antes a la pestaña.

## Qué cambia

- `HORA_DE_CONGELAR = '02:00'` en `v2/js/domain/superbros.js`, y con ella el script del cron.
- El aviso de la pestaña sin nivel, el comentario del workflow, el contrato con Joel y el slice.
- Los escenarios se renombran a `se-congela-a-la-hora` y `antes-de-la-hora-no-se-congela`: el nombre ya no
  depende de la hora, así que el próximo cambio no obliga a renombrarlos.

## Lo que cuesta

En 60 días, 1 de 490 cuadrículas llegó a la tabla después de las 02:00 (a las 02:57). Con la hora nueva, una
así no entra en el nivel de su jornada; sí en la clasificación, el álbum y el resumen, que no dependen del
nivel.

## Efecto al desplegar

Si se despliega pasadas las 02:00, la siguiente vuelta del cron congela la jornada de ayer en ese momento.
