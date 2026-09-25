# Deltas de `ingesta` — feat-tono-del-hilo

## ADDED Requirements

### Requirement: El hilo de la jornada se lee entero, y sale del borde sin nombres

Hasta ahora del canal se leían las cabeceras: quién publicó, cuándo, cuántas reacciones y cuántas respuestas
colgaban. Para saber de qué iba una conversación hay que leerla, así que el hilo del resultado más comentado
de la jornada se pide entero.

Lo que se manda fuera va **anonimizado, contenido incluido**: cada persona aparece con un rol —quien abrió
el hilo, y el resto como participantes numerados— y del texto se retiran las marcas de Slack, que traen
identificadores en crudo, y los nombres del grupo, que la gente escribe a mano. El nombre lo reinserta el
repositorio al componer el mensaje, que ya lo sabe.

Anonimizar **solo la etiqueta de quien habla no anonimiza nada**, y se comprobó: en cuanto alguien menciona a
un compañero —lo normal en un hilo— su identificador sale tal cual dentro del texto.

Y un participante no puede fabricar participantes: los saltos de línea de una respuesta se colapsan, porque
si no una sola persona escribe «participante 7: …» dentro de su propio mensaje y el modelo cuenta dos
personas donde hay una.

Tapar un nombre es sustituir **la palabra**, no la subcadena: con una «Ana» o una «Cata» en la liga,
sustituir por subcadena convertía «mañana» en «mañalguien» y el texto que decide si se publica un reproche
llegaba ilegible.

Se excluye lo que escribe quien abrió el hilo: la conversación que interesa es la del grupo sobre su jugada,
no su defensa.

#### Scenario: la transcripción no lleva nombres
- GIVEN el hilo de un jugador con respuestas de otros
- WHEN se prepara la transcripción para clasificarla
- THEN ningún nombre de jugador ni identificador de Slack aparece en ella

#### Scenario: quien abrió el hilo no cuenta como participante
- GIVEN un hilo donde su autor también responde
- WHEN se prepara la transcripción
- THEN sus propias respuestas no se cuentan como conversación del grupo

```yaml
checks:
  - type: regex
    file: tools/tono.py
    pattern: 'def transcripcion'
    describe: la transcripción que sale del borde se arma aquí, sin nombres
```

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py


### Requirement: Solo se lee el hilo de la jornada que se publica

La ventana que se pide al canal son treinta días, porque las aperturas se cuentan sobre el histórico. La
clasificación, en cambio, mira **un solo hilo**: el de la jornada que se está publicando.

Sin ese recorte se repetiría el defecto que ya tuvo la mención del hilo antes de acotarla: el mensaje acabó
presentando como «el hilo del día» una conversación de tres semanas atrás.

#### Scenario: los hilos de otros días no se clasifican
- GIVEN una ventana del canal con hilos de jornadas anteriores
- WHEN se elige el hilo a clasificar
- THEN se elige el de la jornada que se publica

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py
