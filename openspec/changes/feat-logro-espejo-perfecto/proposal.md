# El espejo perfecto tiene su logro

## Por qué

La simetría era un rasgo invisible. El clasificador la detecta (`rasgos(...).espejo`) pero en `figura()` se
consulta en **último lugar**, así que solo rescata abstractos: una cuadrícula simétrica que además cumple la
regla de la flor se etiqueta «flores» y su simetría no aparece en ninguna parte.

Le pasó a la mejor cuadrícula del histórico. El 27 de agosto de 2026, en la jornada #1694:

```
Y...Y      ← dos amarillos en fila limpia: es lo que la marca como flor
GG.GG
GG.GG
GG.GG
GGGGG
```

Cuatro filas de cuerpo, simétrica fila a fila, y etiquetada «flores». Ni siquiera ganó la obra del día: ese
desempate ordena **primero por rareza de categoría**, y un geométrico cualquiera —hay 6 en agosto frente a
103 flores— la gana antes de que la simetría se llegue a consultar.

## El umbral es el logro

Medido sobre las 1.706 cuadrículas con patrón del histórico:

| Cuerpo mínimo | Espejos | % | Jugadores distintos | En agosto |
|---|---|---|---|---|
| ≥ 1 | 19 | 1,10% | **10 de 23** | 3 |
| ≥ 2 | 12 | 0,70% | 9 | 2 |
| **≥ 3** | **7** | **0,41%** | **7** | **1** |
| ≥ 4 | 1 | 0,06% | 1 | 1 |

Con cuerpo ≥ 1 lo tendría el 43% del grupo, que es el error ya cometido con una medalla que tenían quince de
dieciséis. Siete de los 19 espejos son de una sola fila (`.GGG./GGGGG`): simétricos por accidente. Con ≥ 4
existiría uno solo en toda la historia.

Con **≥ 3** sale uno cada cinco meses y lo han logrado siete personas distintas: raro y de verdad.

## Qué cambia

- `Medalla("espejo-perfecto", "Espejo perfecto", "🪞", "legendario", "permanente")`. Permanente como
  `suertudo` y `dia-imposible`: es una gesta puntual, no un acumulado del mes.
- Se concede mirando **el rasgo y no la categoría**. Si dependiera de la etiqueta se perdería justo en la
  cuadrícula que lo motivó, que es una «flor».
- Se anuncia el día que ocurre, por el camino que ya existe (`medallas_permanentes(…, jornada=…)`).
- Entra también en el catálogo de la web y en el sprite de iconos, con su regla explicada.

Comprobado sobre producción: lo tienen siete jugadores y **Juan (Kokuma) lo gana en la jornada #1694**.

## Qué no hace

- **No toca la clasificación de figuras ni el álbum.** Ninguna categoría cambia, así que no hay que
  rematerializar nada ni se mueve la puntuación de nadie.
- No cambia el desempate de la obra del día: la simetría sigue por debajo de la rareza de categoría. Es una
  decisión pendiente aparte.
- Los logros son reglas del juego y **las decide el grupo en el canal**. Esta va sin votar, como otras cinco.
