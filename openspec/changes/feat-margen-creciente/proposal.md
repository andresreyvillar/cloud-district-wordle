# El castigo por faltar crece con las ausencias

## El fallo

Con un margen igual para cada falta, **la regla premiaba no aparecer**. En agosto de 2026:

```
                 jugadas   media    puesto
Carlos                 1    4,80       14º
Clara C               18    4,90       16º
```

Carlos jugó **un día de veintiuno** y quedaba por delante de Clara C, que jugó dieciocho. Veinte ausencias le
costaban 0,80 en total.

La causa está en el propio modelo: `max(dificultad, media_personal)` existe para que faltar no pueda mejorarte
la media, pero tiene el efecto lateral de **blindar a quien casi no juega** — se le aplica su propia media como
suelo, así que el castigo real se reduce al margen. Lo vio el dueño.

## Qué cambia

```
antes:  margen = 0,5                            fijo para cada falta
ahora:  margen(n) = 0,5 + 0,15 × (n − 1)        n = enésima ausencia del mes
```

La primera falta cuesta 0,5; la segunda 0,65; la décima 1,85; la veinteava 3,35. El tope del fallo sigue
mandando: ninguna ausencia penaliza más que la peor partida posible.

## Por qué creciente y no un margen fijo mayor

Se midieron cuatro opciones sobre agosto, comparando **cuánto cuesta faltar** a cada uno:

| | 20 faltas | 15 | 4 | 3 |
|---|---|---|---|---|
| actual 0,5 fijo | +0,80 | +0,54 | +0,21 | +0,07 |
| fijo 1,0 | +1,27 | +0,90 | **+0,31** | +0,14 |
| **creciente 0,15** | **+2,14** | **+1,37** | **+0,28** | +0,11 |
| creciente 0,25 | +2,45 | +1,64 | +0,33 | +0,15 |

El fijo sube el castigo a todos por igual; el creciente **lo concentra en quien no aparece sin tocar a quien
falta poco**. Con 0,25 el tramo medio se desordena: quien jugó 11 de 21 caía seis puestos.

Resultado en la tabla de agosto: Carlos pasa del 14º al 16º y Clara C del 16º al 13º. **El campeón es el mismo
con las cuatro opciones** — lo que se corrige es la mitad baja.

## El test que estaba en verde mientras el defecto existía

El escenario `jugar-poco-no-da-ventaja` ya cubría esto, y pasaba: su fixture tiene **cinco jornadas**, y a esa
escala el margen fijo basta. El defecto solo aparece con la escala de un mes real. El test nuevo usa 21
jornadas, que es lo que lo reproduce.

## Qué no hace

- **No cambia el `max`** que impide que faltar mejore la media, ni el tope del fallo.
- No toca la temporada 0, que no imputa.
- No cambia quién ganó agosto.

## Aviso registrado

El repositorio ya consta de que **el modelo de imputación se aplicó sin que el canal lo votase** y que «cambia
quién gana». Esto lo endurece de forma desigual: la media de agosto de Carlos pasa de 4,80 a 6,04. Con
septiembre en marcha, conviene decirlo en el canal.
