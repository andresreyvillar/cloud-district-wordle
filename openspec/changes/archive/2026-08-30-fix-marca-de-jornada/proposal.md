# La guarda de duplicados no reconocía su propio título

## Qué pasó

El grupo recibió el resumen **por triplicado** los días 28 y 29 de agosto de 2026:

```
28 ago  01:27 · 01:38 · 02:07
29 ago  00:57 · 01:09 · 01:37
```

Tres ventanas de cron, tres publicaciones. La idempotencia se añadió justo para que solo publicara la primera.

## Por qué

**Slack convierte el emoji del título a su código corto.** Se envía `Ranking Wordle del Día 🏆 · #1694` y
`conversations.history` devuelve `Ranking Wordle del Día :trophy: · #1694`. La guarda comparaba el título
**entero** con `==`, así que la igualdad no se cumplía nunca: no detectaba nada y las tres ventanas publicaban.

Y el test que debía cazarlo **construía el mensaje falso llamando a `titulo_de`**, así que coincidía por
construcción y nunca ejercitó la ida y vuelta real por Slack. Es la tercera vez en este proyecto que un test
prueba una función sin su uso.

## Qué cambia

Se busca **la marca de la jornada** dentro del título, no el título completo, así que cualquier
transformación del emoji da igual. La marca va anclada para que no coincida por prefijo: `· #1694` no puede
darse por bueno dentro de `· #16940`, cosa que destapó su propio test.

El test nuevo usa el **texto literal que devolvió Slack** el 28 de agosto, no uno construido con la función.

## Lo que esto NO arregla

La hora. El resumen sale de madrugada porque **GitHub está descartando y retrasando las ventanas
programadas**, y eso no se puede arreglar desde el repositorio. Medido sobre este repo:

- el cron horario declarado a las `:23` corrió a los minutos 45, 24, 47, 35, 06, 11, 50, 27, 56 y 58;
- **10 ejecuciones en tres días** en lugar de 72, o sea un 86% descartado;
- las tres ventanas del resumen —17:07, 17:37 y 18:07 UTC— dispararon todas entre las 00:56 y las 02:07,
  con entre siete y ocho horas de retraso.

Con esta corrección el retraso sigue, pero ya solo publica **una vez**.
