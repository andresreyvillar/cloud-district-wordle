# Las frases concuerdan en género, con una tabla declarada

## Por qué

Tres frases del registro llevaban `@` porque el sistema no tiene el dato:

```
{jugador} está sembrad@ hoy 🌟
{jugador} hoy no estaba inspirad@ 😅
{jugador} ha resuelto en {dato} y se ha quedado tan anch@ 🤨
```

La tabla solo guarda `player_name` y `slack_user_id`. La `@` era un apaño tipográfico.

## Cómo, y por qué así

**Una tabla declarada, no una inferencia en el momento.** El dueño pidió deducirlo del nombre; se planteó el
riesgo —son compañeros identificables en un canal del trabajo, y equivocarse ahí no es un fallo de
concordancia sino dirigirse mal a alguien delante del grupo— y la solución acordada fue declararlo:

- **20 formas** las dio el dueño directamente;
- **3 se preguntaron** antes de escribirlas, porque no estaban claras: Cata (femenino), Gabi (masculino) y
  Dani Sanchez (masculino).

Lo que hace segura la tabla es que **es un dato en un solo sitio**: si alguna está mal se corrige ahí y no en
once frases. Y **quien no aparece sale en neutro**, así que un jugador nuevo no hereda una suposición.

## Reglas de concordancia

```
una persona declarada    su forma
varias, todas femeninas  femenino
varias, mixtas           masculino     ← lo que hace el castellano
ninguna declarada        neutro (@)    ← no se supone nada
```

## Un test existente que se puso en rojo con el código correcto

`test_ninguna_frase_deja_huecos_sin_rellenar` formateaba las plantillas a mano, y el hueco de género se
resuelve **antes** del formateo —la tabla se indexa por nombre, y después de formatear el nombre ya está
dentro del texto—. Atado ahora al camino real (`frase`), que además prueba más: recorre las cuatro
combinaciones de forma sobre todas las plantillas.

## Qué no hace

- No infiere nada en tiempo de ejecución: lo que no está declarado sale neutro.
- No toca el resto de las 406 frases, que no llevan género.
