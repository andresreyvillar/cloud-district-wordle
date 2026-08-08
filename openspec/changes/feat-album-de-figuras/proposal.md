# Proposal — feat-album-de-figuras

> **Slice:** `album-de-figuras` (openspec/slices/dashboard/album-de-figuras.md)

## Why

El álbum ya se calcula y viaja en la instantánea ([`feat-clasificacion-de-figuras`](../feat-clasificacion-de-figuras/proposal.md)),
y **nadie lo ve**. Este pack es la vista, y nada más: no calcula ni reordena.

Es el segundo eje del juego y premia a otra gente que el marcador — en la temporada 0 los dos podios no
comparten a nadie. Ponerlo al lado del marcador es lo que convierte esa afirmación en algo que el grupo
comprueba de un vistazo en lugar de leerlo en una spec.

## Un supuesto de 5.3 que resultó falso: JSONB no conserva el orden de las claves

La instantánea de 5.3 publicaba el vocabulario como **diccionario** `{loro: 🦜, flores: 🌷, …}`. Comprobado
contra la instantánea real de producción, Postgres devuelve las claves de un `jsonb` **ordenadas por
longitud y luego alfabéticamente**:

```
claves de logros: verdugo, fondista, suertudo, impecable, dia-imposible, superviviente
```

Con ese orden, `abstracto` (9 letras) llegaría **antes** que `geometrico` (10) y la web pintaría el ruido en
medio de las figuras que puntúan. El catálogo pasa a viajar como **lista ordenada** de
`{clave, emoji, puntua}`, y un test lo fija comparándolo con el orden que aplicaría JSONB.

No es cosmético: el fallo habría aparecido solo en producción, porque en los tests de Python el diccionario
conserva su orden de inserción.

## What Changes

```
tools/album.py             `categorias()`: catálogo ordenado en lugar de `vocabulario` (diccionario)
v2/js/data/album.js        NUEVO · PURO: tira, albumDeTemporada, albumDeJugador
v2/js/ui/temporada.js      `bloqueDeAlbum` y `tiraDeFiguras`, exportados para verificarlos sin navegador
v2/js/ui/jugador.js        `tarjetaDeAlbum` en la ficha
v2/css/styles.css          la tira agrupada, la fila del álbum y su versión de móvil
tools/local_stack.py       arreglo de una llamada que se quedó atrás (ver abajo)
```

## Decisiones

- **La tira va agrupada** (`🦜8 🌷60 📐3 🌀15`): cuatro entradas por muchas partidas que haya. Con 135
  partidas la tira literal satura la línea, y es la única forma de la tira que no crece con el histórico.
- **El ruido se apaga** al 45% de opacidad. Está para que el recuento sea honesto, no para competir con las
  figuras.
- **Una instantánea sin álbum no pinta el bloque.** No es un caso hipotético: es el estado de producción
  hasta que la rama llegue a `main`, así que es la primera cosa que la vista tiene que saber hacer.
- **Un jugador sin partidas clasificadas no ve un 0%**, que diría que dibujó mal, sino que aún no hay álbum.
  Un jugador con partidas y sin figuras sí ve su 0%: eso sí es cierto.

## Verificado en navegador, con los datos reales

| | Resultado |
|---|---|
| Temporada 0 | 21 filas, 18 con puesto · Juan (Kokuma) 83% con `🦜8 🌷60 📐3 🌀15` |
| Ficha del líder | bloque ÁLBUM entre MES A MES y MEDALLAS, con su tira y su puesto |
| Agosto 2026 | 11 filas sin puesto y el aviso: hacen falta 5 partidas y 61 no tienen cuadrícula |
| Móvil (390px) | la tira cabe; el bloque del álbum no desborda |
| Consola | sin errores |

## Dos cosas encontradas de camino

- **`tools/local_stack.py` estaba roto** desde `feat-captura-apunta-a-la-v2`: llamaba a `comentario(medallas)`
  cuando la firma pasó a `comentario(medallas, objetivo)`. Reventaba al llegar al paso 3. Arreglado, porque
  bloqueaba la verificación local de este slice.
- **La vista de temporada desborda horizontalmente en móvil**, y no es de este slice: lo causan las 181
  barras de `.columnas` en ESTADÍSTICAS, con o sin el álbum (comprobado quitándolo). Queda **reportado, no
  arreglado**: cambiar esa vista sin slice sería justo lo que el protocolo prohíbe.

## Impact

- Cierra el punto 5.4 del roadmap.
- Desbloquea 6.2 (`medallas-de-figuras`), que necesita el álbum a la vista para que las medallas se entiendan.
- El bloque **no se verá en producción** hasta que `wordle_2` se mergee: sin el pipeline nuevo, la
  instantánea no trae álbum y la vista se pinta sin él, que es exactamente lo que hace el escenario
  `instantanea-sin-album-no-rompe`.
