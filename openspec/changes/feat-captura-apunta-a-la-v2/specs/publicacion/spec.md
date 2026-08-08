# Deltas de `publicacion` — feat-captura-apunta-a-la-v2

## ADDED Requirements

### Requirement: El objetivo de la captura diaria es configurable, y va entero

De qué web se saca la captura sale de la configuración del entorno, no de una constante en el código. Y lo
configurable es **el objetivo completo** —URL, el selector que confirma que hay datos y el que se
fotografía—, porque son tres datos de la misma decisión: los de la v1 no sirven para la v2.

Cambiar solo la URL dejaba el workflow esperando quince segundos un elemento inexistente y el resumen sin
publicar. Yendo juntos, ese estado roto deja de ser expresable.

El enlace del mensaje es el del **mismo** objetivo capturado: una foto de una web con un enlace a otra es la
forma más rápida de que nadie se fíe de ninguna de las dos.

#### Scenario: el objetivo sale del entorno
- GIVEN la configuración pide un objetivo concreto
- WHEN se prepara la publicación
- THEN se usa ese, con su URL y sus selectores

#### Scenario: sin configuración se usa lo que está desplegado
- GIVEN ninguna configuración
- WHEN se prepara la publicación
- THEN el objetivo es la v1

#### Scenario: el enlace apunta a donde la captura
- GIVEN un objetivo
- WHEN se compone el texto
- THEN el enlace es el de ese objetivo

#### Scenario: un objetivo desconocido aborta
- GIVEN una configuración que pide un objetivo inexistente
- WHEN se prepara la publicación
- THEN la ejecución falla, en lugar de usar el objetivo por defecto

### Requirement: Una publicación fallida termina en error

Si la captura o la subida fallan, la ejecución termina con código distinto de cero.

Hasta ahora cualquier fallo se imprimía y la ejecución terminaba bien: el grupo dejaba de recibir el
resumen y en Actions estaba todo verde. Un fallo silencioso en la única salida visible del sistema es peor
que un fallo ruidoso.

#### Scenario: una captura fallida sale en rojo
- GIVEN que la captura lanza
- WHEN termina la ejecución
- THEN el código de salida no es cero

#### Scenario: una subida fallida sale en rojo
- GIVEN que la subida a Slack no publica
- WHEN termina la ejecución
- THEN el código de salida no es cero

verified-by:
  - tests/slices/captura-apunta-a-la-v2/test_captura.py
