# La jornada no se publica dos veces, y el cron tiene más de una oportunidad

## Por qué

El 26 de agosto de 2026 el grupo recibió el mismo resumen **dos veces**, a las 18:47 y a las 19:13. La causa
en cadena:

1. GitHub tuvo una caída crítica de Actions (15:11 → 18:01) y el cron de las 17:00 no se disparó.
2. Al ver que faltaba el mensaje, se lanzó a mano a las 18:47.
3. El programado llegó a las 19:11, con **2h11m de retraso**, y publicó otra vez.

El fallo de fondo no es el retraso de GitHub, que no está en nuestra mano: es que `post_ranking` **no tenía
ninguna guarda**. Publicar dos veces dependía del criterio de quien lo lanzara, y ese criterio falló.

## Qué se midió

El planificador de GitHub descarta ejecuciones incluso sin incidentes, y este repo lo sufre a diario:

| Día | Ejecuciones del cron horario |
|---|---|
| 18-25 ago (normales) | 21-23 de 24 |
| 26 ago (caída) | 16 de 24 |
| 27 ago (12h) | **1 de 12** |
| 17 ago | 5 de 24 |

Y las que salen llegan tarde: con `0 * * * *` caían a las :22, :36, :55 — entre 20 y 60 minutos de retraso
todos los días. **El minuto en punto es el más disputado de GitHub**, y esa cola es la primera que se
descarta cuando hay presión.

## Qué cambia

**Idempotencia.** El título de la captura pasa a llevar la jornada (`Ranking Wordle del Día 🏆 · #1694`), y
antes de publicar se comprueba si el canal ya tiene esa captura. Si la tiene, se sale con éxito **sin abrir el
navegador**: descubrir que no hay que publicar después de la captura gastaría el runner para nada.

Se prefirió la marca en el título a comparar fechas porque una publicación muy retrasada puede cruzar la
medianoche UTC, y ahí la comparación por fecha diría que no se publicó.

**Tres ventanas para el resumen, y ninguna en punto:** 17:07, 17:37 y 18:07. Son seguras justamente por la
guarda anterior: publica la primera que entre y las otras dos son red de seguridad. El horario pasa a
`23 * * * *`.

## Qué no hace

- **No arregla las caídas de GitHub.** Nada aquí puede. Lo que hace es que un descarte no deje al grupo sin
  mensaje, y que un lanzamiento manual no produzca un duplicado.
- **No recupera ventanas perdidas**: GitHub no reintenta, y esto no añade un reintento propio.
- Un canal ilegible **publica**: entre dejar al grupo sin resumen y arriesgar un duplicado con Slack caído, se
  elige publicar. Es una decisión, no un descuido.
