# Deltas de `dashboard` — feat-nivel-congelado

## ADDED Requirements

### Requirement: La pestaña juega el último nivel congelado, no uno calculado al abrirla

La pestaña del juego lee de `game_levels` **el último nivel congelado** —jornada, fecha y nivel— y lo juega;
el ranking que enseña es el de esa jornada. La web ya no ejecuta `nivelDe`: así el nivel de ayer no cambia
durante la madrugada porque llegue tarde una cuadrícula, y todos los tiempos de un ranking son sobre el mismo
escenario.

Si no hay ningún nivel congelado, o no se puede leer, la pestaña lo dice en lugar de pintar un escenario.

#### Scenario: se juega lo que dice game_levels
- GIVEN niveles congelados de varias jornadas
- WHEN se abre la pestaña
- THEN se lee el de jornada más alta y se juega ese, con su jornada y su fecha en la cabecera

#### Scenario: sin nivel congelado, se dice
- GIVEN ningún nivel congelado, o un fallo al leerlos
- WHEN se abre la pestaña
- THEN dice que todavía no hay nivel y no monta el lienzo

```yaml
checks:
  - type: regex
    file: v2/js/ui/juego.js
    pattern: 'const congelado = await nivelParaJugar\(niveles\);'
    describe: la pestaña juega el nivel que lee de la fuente de niveles congelados
  - type: regex
    file: v2/js/data/results.js
    pattern: "\\.from\\('game_levels'\\)[\\s\\S]*?\\.order\\('jornada', \\{ ascending: false \\}\\)[\\s\\S]*?\\.limit\\(1\\)"
    describe: se lee el último nivel congelado
```

verified-by:
  - tests/slices/nivel-congelado/web.test.js


### Requirement: El cron congela el nivel de la jornada de ayer a partir de las 04:00 de Madrid

Tras cada sincronización de `update_stats.yml`, `node tools/congelar_nivel.mjs` congela en `game_levels` el
nivel de la **última jornada asentada**: desde las 04:00 de Madrid, la de ayer; antes, la de anteayer —que
normalmente ya estará congelada—. La de hoy, nunca. El nivel lo genera el **mismo** `nivelDe` que la web
usaba, ejecutado con Node: una sola implementación.

La hora sale de medir: en 60 días, 2 de 490 cuadrículas llegaron después de medianoche, la más tardía a las
02:57. El reloj entra solo en el borde (`ahoraEnMadrid`), y `--hoy`/`--hora` lo sustituyen.

El script dice qué congela —jornada, fecha, tramos— antes de escribir, o por qué no congela nada; con `--seco`
no escribe. Una jornada ya congelada no se reescribe: la consulta lo ve antes, y la inserción ignora el
duplicado si otra ejecución se adelantó.

#### Scenario: a las 04:00 se congela la de ayer
- GIVEN el día D a las 04:00 o después, sin nivel congelado para D-1
- WHEN corre el cron
- THEN guarda el nivel de `nivelDe` para D-1 con su jornada y su fecha

#### Scenario: antes de las 04:00 no
- GIVEN el día D antes de las 04:00
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
    file: .github/workflows/update_stats.yml
    pattern: '&& node tools/congelar_nivel\.mjs; then'
    describe: el cron congela el nivel en cada vuelta, después de sincronizar
  - type: regex
    file: tools/congelar_nivel.mjs
    pattern: "Prefer: 'resolution=ignore-duplicates"
    describe: la inserción no pisa una jornada que otra ejecución congeló a la vez
  - type: regex
    file: v2/js/domain/superbros.js
    pattern: "export const HORA_DE_CONGELAR = '04:00';"
    describe: la hora que decidió el dueño
```

verified-by:
  - tests/slices/nivel-congelado/congelar.test.js
