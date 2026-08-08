# Deltas de `dashboard` — feat-tabla-de-datos

## ADDED Requirements

### Requirement: La tabla cruda permite comprobar que el marcador no se ha inventado nada

Hay una vista con **un resultado por fila, sin filtrar ni agregar**: fecha, jugador, jornada e intentos, de
la más reciente a la más antigua. Es la que se mira cuando alguien no se fía de una cifra, y por eso filtrar
sería justo lo que le quitaría el sentido.

Lleva una columna que la v1 no podía tener: **si esa fila cuenta para su temporada**, con el motivo cuando no
cuenta. Con las reglas nuevas, «¿por qué mi resultado del sábado no sale en el marcador?» tiene respuesta, y
su sitio es esta tabla.

#### Scenario: la tabla lista todos los resultados
- GIVEN resultados guardados
- WHEN se abre la tabla
- THEN hay una fila por resultado, sin filtrar ninguno

#### Scenario: el orden es estable y de lo más reciente a lo más antiguo
- GIVEN resultados de varios días
- WHEN se listan
- THEN salen de la fecha más reciente a la más antigua, y dos cargas dan la misma lista

#### Scenario: una fila que no cuenta lo declara con su motivo
- GIVEN una fila cuya jornada no está entre los días válidos de su temporada
- WHEN se muestra
- THEN declara que no cuenta y dice si es por fin de semana o por falta de muestra

#### Scenario: el fallo se distingue de un seis
- GIVEN un resultado sin resolver
- WHEN se muestra
- THEN aparece como fallo, no como un 7

### Requirement: La temporada de un resultado la decide el modelo, también en la web

En la web, la temporada de una fecha se resuelve con **una única función** que lee el límite de las reglas
publicadas en la instantánea. Comparar el mes de la fecha con el identificador de una temporada está
prohibido: con la temporada 0 no coincide nunca y falla en silencio.

El borde de datos llama `mes` al mes de una fila, no `temporada`, para que el error no vuelva a estar a
un descuido de distancia.

#### Scenario: una fila anterior al límite pertenece a la temporada 0
- GIVEN una fila con fecha anterior al mes en que empiezan las temporadas numeradas
- WHEN se resuelve su temporada
- THEN es la temporada 0, y se compara con la instantánea de la 0

#### Scenario: sin el límite publicado no se adivina la temporada
- GIVEN una instantánea sin las reglas
- WHEN se resuelve la temporada de una fila
- THEN no se afirma ninguna

verified-by:
  - tests/slices/tabla-de-datos/tabla.test.js
