# El mensaje abre con la palabra y su significado, a medianoche de Madrid

## Por qué

El grupo comparte cuadrículas de colores todo el día y **nadie ve nunca la palabra escrita**. Cada uno sabe la
suya y ya. Y menos aún su significado: de las 25 últimas jugadas hay `vitre`, `agraz`, `taxón`, `merlo`,
`friso` y `curia`.

Es lo único que el mensaje puede aportar que el grupo no tenga ya, así que **abre el mensaje**.

## Por qué a medianoche de Madrid, y no a las 19:00

El juego avanza su índice a medianoche de **Nueva York**, o sea a las 06:00 de Madrid. A las 00:00 de Madrid la
palabra sigue siendo la que el grupo ha jugado todo el día, así que **coincide con la jornada que resume el
mensaje**. A las 19:00 también coincidiría, pero la partida estaría abierta once horas más; a las 07:00 el
índice ya habría cambiado y se publicaría la palabra del día siguiente.

Riesgo de destripar la partida, medido sobre 1748 resultados del canal: **2 se publicaron entre las 00:00 y las
06:00 de Madrid**, un 0,1%.

```
0 22 * * 1-5   → 00:00 Madrid en verano · 23:00 en invierno
30 22 * * 1-5  → 00:30 · 23:30
0 23 * * 1-5   → 01:00 · 00:00
```

**Deriva de invierno aceptada por el dueño**: los cron de GitHub son UTC y no saben de horario de verano.

## Cómo se obtiene

Del propio juego. Se confirmó que el grupo juega «La palabra del día» y no el Wordle del NYT por dos vías
independientes que coinciden: la numeración de la tabla sitúa la jornada 1 el 2022-01-07, y el cliente del
juego declara ese mismo `firstDay`. **El identificador de la tabla es el índice del juego**, sin desplazamiento.

El fichero de soluciones está ofuscado —gzip, XOR con una clave que viaja en el propio cliente, y msgpack—, y
esto reimplementa esa lógica de cliente. Verificado: 2.000 entradas con `id`, `solution` y un `extras` vacío en
todas, así que **la definición no está ahí** y se busca en el Wikcionario.

Se busca **por `id`** y no por posición: reproducir su aritmética de índices sería un acoplamiento más.

## El guardarraíl

`palabra_de` **se niega a devolver una palabra posterior a la última jornada de la tabla**, aunque esté en el
fichero. Con 2.000 entradas, sin esto bastaría cambiar un número para leer meses por delante, y este
repositorio es público y la liga es competitiva. Que exista es lo que hace que no sea una chuleta, y la prueba
de mutación lo confirma: quitarlo pone dos escenarios en rojo.

**Nada se persiste.** Se descarga, se usan dos campos y se descarta, igual que la lectura del canal. Hay un
test sobre el árbol sintáctico del módulo que lo comprueba.

## Cobertura del diccionario

Medida sobre las 25 jornadas jugadas más recientes: **24 de 25 (96%)**. La única sin definición es `vitre`, y
sale publicada sin acepción. `troya` se recupera con el respaldo por mayúscula inicial, porque el juego usa
minúsculas y el Wikcionario respeta el nombre propio.

La primera medición dio 18 de 25, y era **falsa**: veinticinco peticiones seguidas activaron el límite de
Wikimedia. En producción es una al día.

## Qué no hace

- **No falla la publicación.** Si el juego o el Wikcionario no responden, el mensaje sale sin esa línea, como
  cualquier sección sin datos.
- No usa la rareza de la palabra para nada todavía —lo de cruzarla con la sospecha sigue pendiente.
- No toca la web ni el esquema.
