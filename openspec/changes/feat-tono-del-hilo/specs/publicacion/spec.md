# Deltas de `publicacion` — feat-tono-del-hilo

## ADDED Requirements

### Requirement: El resumen dice de qué iba el hilo del día, no solo cuánto midió

Contar respuestas no distingue una ovación de un juicio. El mensaje ya sabía decir que alguien «armó el hilo
del día», y el día que un hilo se llenó de acusaciones lo publicó como un mérito. La mención del hilo lleva
por tanto **de qué iba la conversación**, y no solo su tamaño.

De qué iba lo decide una clasificación cerrada del hilo —el tono dominante, si hubo acusación, si hubo
defensa, si se propuso cambiar alguna regla, y cuánta temperatura tuvo—, no el recuento.

#### Scenario: la mención del hilo incorpora su tono
- GIVEN el hilo más comentado de la jornada, con su clasificación
- WHEN se compone el resumen
- THEN el texto refleja de qué iba la conversación además de cuántas respuestas tuvo

```yaml
checks:
  - type: regex
    file: tools/tono.py
    pattern: 'class Tono'
    describe: la clasificación es un objeto cerrado y sin campos de texto
```

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py


### Requirement: La frase que comenta el hilo sale del registro del repositorio

La frase publicada es **una de las del refranero**, elegida por la clasificación y por el número de jornada,
igual que el resto de la voz del mensaje. Ninguna palabra redactada por el modelo aparece en el canal.

La razón no es de estilo. En este canal la gente **ya le escribe al bot**, así que publicar prosa de un modelo
que acaba de leer el canal permitiría a cualquiera dictar lo que el bot dice sobre un compañero identificable
delante de todo el grupo. Con la frase saliendo del registro, una instrucción colada en el hilo como mucho
cambia una casilla del esquema, y la casilla no redacta.

Por lo mismo, del objeto que devuelve el modelo **solo se leen los campos del esquema**: cualquier campo
adicional se ignora en lugar de abrirse camino hasta el mensaje. Dos consecuencias que parecen detalles y no
lo son:

- **De quién es el hilo lo decide el repositorio, no el modelo.** Es el dato que determina a quién nombra el
  mensaje delante de todo el canal, así que no puede venir de fuera ni deducirse del recuento de respuestas
  —ese recuento incluye la charla, y respondiendo muchas veces a un mensaje intrascendente de otra persona se
  conseguía que el bot la señalara a ella por una conversación que no era la suya—.
- **Las cifras que se publican también tienen tope.** Cuántas personas dudan sale interpolado en la frase, así
  que una cifra sin límite serían dígitos publicados que no ha escrito el repositorio, y además empujaría el
  mensaje por encima de lo que Slack acepta.

**El registro es de cachondeo, no de sentencia.** Las frases se burlan como se burla el canal —amistosas y
con guasa— y **el bot no dictamina nada**: ni declara culpable a nadie, ni anuncia medidas, ni habla como un
juzgado. Las decisiones sobre el juego las toma el dueño cuando las pide; el mensaje de la tarde solo cuenta
lo que pasó y se ríe un rato. Hay un test que prohíbe el vocabulario judicial en el registro, porque la
primera versión derivó justo ahí.

#### Scenario: la frase publicada pertenece al registro
- GIVEN una clasificación del hilo
- WHEN se elige la frase que lo comenta
- THEN esa frase es una de las del registro del repositorio

#### Scenario: el texto que venga del modelo no se publica
- GIVEN una clasificación que trae además campos de texto libre
- WHEN se compone el resumen
- THEN ese texto no aparece en el mensaje

#### Scenario: la misma jornada da la misma frase
- GIVEN la misma clasificación y la misma jornada
- WHEN se compone el resumen dos veces
- THEN la frase del hilo es la misma

```yaml
checks:
  - type: regex
    file: tools/refranero.py
    pattern: 'TONO_DEL_HILO'
    describe: las frases del hilo viven en el registro del repositorio
```

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py


### Requirement: Sin clasificación válida, el resumen se publica sin esa frase

La clasificación es un adorno, no un requisito. Si la llamada falla, tarda de más, se queda sin cuota o
devuelve algo que no encaja en el esquema, el resumen sale con todo lo demás y sin la frase del hilo.

Es la misma regla que ya gobierna la lectura del canal: un servicio de fuera no puede impedir que el grupo vea
su marcador.

La credencial que se usa para preguntar tampoco puede escaparse por el camino: el destino se exige por TLS,
y una redirección **no se sigue**, porque al cambiar de host la cabecera de autorización viajaría con ella.
El plazo que se le da es **total y no por operación de red**: un servidor que gotee bytes no dispara el
tiempo de espera de un socket, y el marcador del día se publica después de esto.

#### Scenario: la clasificación no llega
- GIVEN que la clasificación del hilo no está disponible
- WHEN se compone el resumen
- THEN el mensaje se publica con el resto de sus menciones y sin la frase del hilo

#### Scenario: la clasificación no encaja en el esquema
- GIVEN una respuesta que no cumple el esquema esperado
- WHEN se interpreta
- THEN se descarta entera, en lugar de usar los campos que sí se entiendan

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py


### Requirement: Un hilo templado no se publica como juicio

La frase de tono solo sale cuando la clasificación llega a una temperatura mínima. Un hilo de felicitaciones,
o de tres respuestas sueltas, no se comenta: dramatizar una conversación que no lo fue es la forma más rápida
de que el mensaje deje de ser creíble.

#### Scenario: un hilo tranquilo no genera frase
- GIVEN una clasificación por debajo de la temperatura mínima
- WHEN se compone el resumen
- THEN no se publica frase de tono

verified-by:
  - tests/slices/voz-de-la-jornada/test_tono.py
