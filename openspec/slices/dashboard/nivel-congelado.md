---
slice: nivel-congelado
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "update_stats.yml — tras cada sincronización, `node tools/congelar_nivel.mjs` congela el nivel de la jornada de ayer a partir de las 02:00 (Madrid)"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - resultados
tests_root: tests/slices/nivel-congelado/
blocked: null
---

# El nivel de cada jornada se congela una vez, y todos juegan el mismo

**Actor:** el sistema (cron de sincronización)
**Trigger:** la primera sincronización a partir de las 02:00 de Madrid

## Contexto

Hasta ahora el nivel se calculaba en el navegador cada vez que alguien abría la pestaña. Eso hacía que el
nivel de ayer **pudiera cambiar durante la madrugada**: una cuadrícula publicada tarde, o que la ingesta aún
no había recogido —GitHub retrasa los cron entre 100 y 110 minutos—, añadía un tramo. Y con el ranking por
nivel ([[ranking-del-juego]]), eso mezclaba en la misma tabla tiempos de dos escenarios distintos.

Ahora el nivel **se congela una vez** en `public.game_levels` y no vuelve a cambiar. La hora la decide el
dueño: **las 02:00**. Primero se fijó a las 04:00, que recogía todas las llegadas tardías medidas (en 60 días,
2 de 490 cuadrículas después de medianoche, la más tardía a las 02:57); luego se adelantó para que el nivel
nuevo llegue antes, sabiendo que deja fuera esa rara cuadrícula de después de las 02:00. Hasta la hora, la
pestaña sigue ofreciendo el nivel anterior.

El nivel lo genera el **mismo módulo JavaScript** que ya lo generaba (`nivelDe` en
`v2/js/domain/superbros.js`), ejecutado con Node desde el cron. Una sola implementación: el escenario de un
día no depende de quién lo calcule.

## Trigger técnico

- `update_stats.yml`, dentro del latido: después de `add_results.py` y `materialize_seasons.py`, cada vuelta
  ejecuta `node tools/congelar_nivel.mjs` con `SUPABASE_URL` y `SUPABASE_SERVICE_ROLE_KEY`.
- El reloj entra **en el borde**: el script calcula la fecha y la hora de Madrid al arrancar y se las pasa a
  la función pura `jornadaACongelar(resultados, hoy, hora)`. `--hoy AAAA-MM-DD --hora HH:MM` las sustituye, y
  `--seco` calcula sin escribir.

## Comportamiento observable

### se-congela-a-la-hora
**WHEN** el cron corre el día D a las 02:00 de Madrid o después, y la jornada de D-1 no tiene nivel congelado
**THEN** genera su nivel con `nivelDe` y lo guarda en `game_levels` con su jornada y su fecha

### antes-de-la-hora-no-se-congela
**WHEN** el cron corre el día D antes de las 02:00
**THEN** la jornada de D-1 no se congela todavía; si la de D-2 no lo estaba —el cron estuvo caído—, se congela
esa

### un-nivel-congelado-no-cambia
**WHEN** el cron vuelve a correr, o llega tarde una cuadrícula de una jornada ya congelada
**THEN** el nivel guardado no cambia: el script no lo reescribe, y la base de datos rechaza cualquier
`update`, `delete` o `truncate` sobre `game_levels`, también con la clave de servicio

### el-cron-declara-lo-que-escribe
**WHEN** el script corre
**THEN** dice qué jornada va a congelar —con su fecha y sus tramos— antes de escribir, o por qué no congela
nada (ya estaba, todavía no toca, nadie tiene cuadrícula); con `--seco` no escribe

### la-web-juega-el-ultimo-nivel-congelado
**WHEN** se abre la pestaña del juego
**THEN** se juega el último nivel congelado, con su jornada y su fecha en la cabecera, y el ranking es el de
esa jornada; la web ya no calcula el nivel

### sin-nivel-congelado-lo-dice
**WHEN** no hay ningún nivel congelado, o no se puede leer
**THEN** la pestaña lo dice en lugar de pintar un escenario

### el-ranking-se-mide-contra-el-nivel-congelado
**WHEN** se llama a `registrar_tiempo`
**THEN** solo acepta jornadas con nivel congelado, y el tiempo mínimo y el máximo de estrellas salen de ese
nivel —sus tramos y sus coleccionables—, no de las filas de `wordle_results`

## Estado después

- Una fila por jornada en `public.game_levels`: `jornada`, `fecha`, `nivel` (el objeto de `nivelDe`, tal
  cual) y `frozen_at`. La clave pública solo la lee.
- `registrar_tiempo` reemplazada, misma firma y mismos permisos.
- Nada cambia en `wordle_results` ni en `season_snapshots`.

## Edge cases

- **Un cambio en `nivelDe` solo afecta a las jornadas futuras.** Las congeladas conservan su forma, así que
  el motor tiene que seguir aceptando niveles con la forma de antes.
- **Arreglar un nivel a mano** exige quitar el trigger a propósito. Es deliberado: un nivel con marcas no se
  cambia sin querer.
- **Fin de semana.** `update_stats.yml` corre todos los días, así que las jornadas de sábado y domingo
  también se congelan.
- **Idempotente.** La inserción ignora el duplicado; dos vueltas seguidas dejan una sola fila.

## Slices compañeros
- [[juego-de-la-jornada]] — el generador (`nivelDe`) y la pestaña que ahora leen el nivel congelado.
- [[ranking-del-juego]] — el ranking por nivel, que ahora se mide contra el nivel congelado.
