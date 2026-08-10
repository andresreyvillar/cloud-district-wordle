# Deltas de `estadisticas` — feat-voz-de-la-jornada

## ADDED Requirements

### Requirement: Las señales del canal producen menciones, y cada una exige evidencia

De las señales del día se derivan menciones, y **ninguna se concede por defecto**. Cada una tiene su umbral, y
si no se cumple, no sale nadie nombrado — igual que la obra del día se declara desierta antes que dársela a un
abstracto.

| Mención | Señal | Cuándo se concede |
|---|---|---|
| madrugador | hora del mensaje | publicó destacadamente antes que el resto del grupo |
| rezagado | hora del mensaje | publicó destacadamente después que el resto |
| más aplaudido | reacciones | su resultado recibió más reacciones que cualquier otro, y al menos una |
| más comentado | respuestas del hilo | abrió el hilo con más respuestas del día, y con al menos una |
| ausente | falta de mensaje | juega habitualmente y hoy no publicó |

Los umbrales de «destacadamente» **se miden antes de fijarlos**, sobre el histórico del canal, y no se
escriben a ojo: un umbral que nombra a alguien todos los días deja de ser una mención y pasa a ser una
columna, y uno que no nombra a nadie nunca es código muerto. El criterio es que la mención salga **en una
minoría clara de las jornadas**.

Un empate no se rompe con el orden en que llegaron los mensajes: se nombran todos los empatados, igual que
hace el jugador del día. Con diez personas y recuentos pequeños, el empate es lo normal.

Estas menciones **no tocan la clasificación**. No dan puntos, no quitan puntos y no aparecen en el marcador:
son texto para el canal. Es la misma frontera que ya separa el álbum del marcador.

```yaml
checks:
  - type: cli-command
    command: python3 tools/calibrate_menciones.py
    note: mide la frecuencia de cada mención sobre el histórico del canal antes de fijar su umbral
```

#### Scenario: la mención sin evidencia no se concede
- GIVEN un día en que ningún resultado recibió reacciones
- WHEN se derivan las menciones
- THEN no hay más aplaudido

#### Scenario: el empate nombra a todos
- GIVEN dos resultados con el mismo número de reacciones, y es el máximo del día
- WHEN se deriva la mención
- THEN se nombran los dos

#### Scenario: con una sola persona no hay madrugador
- GIVEN una jornada con un único resultado
- WHEN se derivan las menciones
- THEN no hay madrugador ni rezagado, porque no hay con quién comparar

#### Scenario: las menciones no dan puntos
- GIVEN una jornada con menciones
- WHEN se calcula la clasificación de la temporada
- THEN es la misma que sin ellas

verified-by:
  - tests/slices/voz-de-la-jornada/test_menciones.py
