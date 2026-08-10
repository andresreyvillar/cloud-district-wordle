# Deltas de `ingesta` — feat-voz-de-la-jornada

## ADDED Requirements

### Requirement: El canal se lee al publicar, y de él solo salen números

La publicación de la tarde lee los mensajes del día en el canal con `conversations.history`, la misma llamada
y el mismo token que ya usa la ingesta horaria. **No hace falta ningún permiso nuevo.**

De esa lectura se derivan **señales**, y nada más: a qué hora publicó cada jugador su resultado, cuántas
reacciones recibió cada mensaje, cuántas respuestas tiene cada hilo y quién no publicó nada. **El texto de los
mensajes no sale de la función que los lee.** El repositorio es público y el canal contiene conversaciones de
compañeros identificables, así que la restricción no se cumple a medias: si la señal se puede expresar con un
número, viaja como número.

Las señales **no se persisten**. Viven lo que dura la ejecución del cron y se descartan al publicar. Dos
razones, y la segunda es de corrección y no de comodidad: no hace falta esquema nuevo para datos de
comportamiento de personas identificables, y **las reacciones son un dato vivo** — guardarlas en la ingesta
horaria las congelaría a media mañana, mientras que leerlas a las 17:00 cuenta el día completo.

Se ignoran los mensajes del **propio bot**: publica todas las tardes y sería siempre el más aplaudido de su
propio resumen. Y se distingue un mensaje **con resultado** de la charla: solo los primeros dan hora de
publicación, porque contar un «jajaja» como resultado falsearía tanto la hora como la ausencia.

La lectura es **best-effort**: si falla o devuelve vacío, el resumen se publica con lo que sale de la tabla.
Un canal caído no puede impedir que el marcador se publique.

```yaml
checks:
  - type: slack-api
    method: conversations.history
    note: la misma llamada de la ingesta horaria; sin scopes nuevos
```

#### Scenario: la hora de publicación es la del canal
- GIVEN un mensaje de resultado publicado a una hora concreta
- WHEN se derivan las señales del día
- THEN la hora que se usa es la del mensaje, no la del registro de la fila

#### Scenario: del canal no sale texto
- GIVEN un día con mensajes de resultado y con charla
- WHEN se derivan las señales
- THEN lo que se devuelve son horas y recuentos, y ningún contenido de mensaje

#### Scenario: el bot no compite en su propio resumen
- GIVEN que el bot publicó su mensaje de la tarde anterior con reacciones
- WHEN se busca el mensaje más aplaudido del día
- THEN el del bot no se considera

#### Scenario: la charla no da hora de publicación
- GIVEN alguien que escribió en el canal pero no publicó resultado
- WHEN se derivan las señales
- THEN no consta como que haya publicado a esa hora

#### Scenario: un canal que no responde no tumba el resumen
- GIVEN que la lectura del canal falla
- WHEN se compone el resumen
- THEN se publica con lo que sale de la tabla, sin las menciones que dependen del canal

verified-by:
  - tests/slices/voz-de-la-jornada/test_senales.py
