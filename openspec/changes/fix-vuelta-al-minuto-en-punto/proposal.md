# Vuelta al minuto en punto: la medida contra la recomendación

## Qué pasó

El 27 de agosto moví los dos cron fuera del minuto `:00`, **porque lo recomienda la documentación de
GitHub**: «para reducir la probabilidad de retraso, programa tu workflow a una hora distinta del comienzo de
la hora». Salió al revés.

```
20-25 ago   cron 0 * * * *    21-23 ejecuciones de 24 al día
26 ago      cron 0 * * * *    16                              ← incidentes de Actions
──────────  cambio a 23 * * * * el 27 a las 13:36  ──────────
27 ago      cron 23 * * * *    2
28 ago                         2
29 ago                         5
30 ago                         6
31 ago                         2
```

Huecos de 6, 8, 12 y hasta **18,5 horas** entre ejecuciones. Y con el resumen igual: con `0 17` se publicaba
puntualmente a las 17:36-17:39 todos los días; con `:07` y `:37` llegó entre las 00:56 y las 02:07, siete u
ocho horas tarde.

## Qué se sabe y qué no

**Lo que matiza el diagnóstico:** el primer hueco grande —27 de agosto, de 04:28 a 22:58— empezó **nueve horas
antes** del cambio. La degradación la arrancaron los incidentes de GitHub del día 26, no el cambio de minuto.

**Lo que no se puede defender:** que el cambio la haya arreglado, y que se sostenga contra la medida. No se
conoce el mecanismo por el que el `:00` funcionaría mejor —capacidad reservada, o menos prioridad para un
horario recién registrado— y no se va a inventar uno.

## Decisión

Se vuelve a los minutos medidos, no a los recomendados. Cuando la documentación general y la medida de este
repositorio se contradicen, gana la medida.

Las tres ventanas del resumen se conservan, en `0 17`, `30 17` y `0 18`: son seguras desde que la guarda de
duplicados funciona, y cubren el caso de que se descarte la primera.

Si el planificador se recupera y esto sigue mal, el siguiente paso es un **disparador externo** que llame al
`workflow_dispatch`, no probar otro minuto.
