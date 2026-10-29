# Deltas de `dashboard` — fix-hora-de-congelar

## MODIFIED Requirements

### Requirement: El cron congela el nivel de la jornada de ayer a partir de las 02:00 de Madrid

Tras cada sincronización de `update_stats.yml`, `node tools/congelar_nivel.mjs` congela en `game_levels` el
nivel de la **última jornada asentada**: desde las **02:00** de Madrid, la de ayer; antes, la de anteayer
—que normalmente ya estará congelada—. La de hoy, nunca. El nivel lo genera el **mismo** `nivelDe` que la web
usaba, ejecutado con Node: una sola implementación.

La hora la decide el dueño. Primero se fijó a las 04:00, que recogía todas las llegadas tardías medidas; se
adelanta a las 02:00 para que el nivel nuevo llegue antes, **sabiendo lo que cuesta**: en 60 días, 1 de 490
cuadrículas llegó después de las 02:00 (a las 02:57), y una así ya no entra en el nivel de su jornada —sí en
todo lo demás, que no depende del nivel—. El reloj entra solo en el borde (`ahoraEnMadrid`), y
`--hoy`/`--hora` lo sustituyen.

El script dice qué congela —jornada, fecha, tramos— antes de escribir, o por qué no congela nada; con `--seco`
no escribe. Una jornada ya congelada no se reescribe: la consulta lo ve antes, y la inserción ignora el
duplicado si otra ejecución se adelantó.

#### Scenario: a las 02:00 se congela la de ayer
- GIVEN el día D a las 02:00 o después, sin nivel congelado para D-1
- WHEN corre el cron
- THEN guarda el nivel de `nivelDe` para D-1 con su jornada y su fecha

#### Scenario: antes de las 02:00 no
- GIVEN el día D antes de las 02:00
- WHEN corre el cron
- THEN no congela D-1; congela D-2 solo si no lo estaba

#### Scenario: lo ya congelado no se reescribe
- GIVEN una jornada congelada y una cuadrícula suya que llega tarde
- WHEN corre el cron otra vez
- THEN no escribe nada y el nivel sigue igual

#### Scenario: dice lo que hace
- GIVEN cualquier ejecución
- WHEN el script decide
- THEN escribe una línea con la jornada que congela antes de escribir, o con el motivo por el que no

```yaml
checks:
  - type: regex
    file: v2/js/domain/superbros.js
    pattern: "export const HORA_DE_CONGELAR = '02:00';"
    describe: la hora que decidió el dueño
  - type: regex
    file: .github/workflows/update_stats.yml
    pattern: '&& node tools/congelar_nivel\.mjs; then'
    describe: el cron congela el nivel en cada vuelta, después de sincronizar
  - type: regex
    file: v2/js/ui/juego.js
    pattern: 'se congela a las 02:00 del día siguiente'
    describe: la pestaña dice la hora de verdad cuando aún no hay nivel
```

verified-by:
  - tests/slices/nivel-congelado/congelar.test.js
