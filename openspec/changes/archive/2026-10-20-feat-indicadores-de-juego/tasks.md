# Tareas — feat-indicadores-de-juego

1. **`tools/indicadores.py`**, puro, sin red:
   - `normaliza(palabra)`: minúsculas y sin tildes; la Ñ se conserva.
   - `colores(intento, respuesta)`: `G`/`Y`/`.` como el juego, con letras repetidas.
   - `candidatas_antes(filas, respuesta, universo, semilla)`: para cada intento, cuántas soluciones del universo
     siguen siendo compatibles. El primero es el tamaño del universo; los siguientes se estiman sorteando, con
     `random.Random(semilla)`, palabras del universo que den cada fila contra la respuesta, y tomando la mediana.
     Devuelve `None` si alguna fila no la produce ninguna palabra.
   - `suerte_de_partida(filas, candidatas)`: Σ (acierto − 1/candidatas) por intento.
   - `indicadores(resultados, temporada, soluciones, hasta)`: por jugador (`media`, `apertura` [mediana tras 1.º
     y 2.º], `suerte`, `partidas`, `milagro` {jornada, intentos, candidatas}) y `grupo`; constantes
     `MINIMO_DE_PARTIDAS` y `MEDIA_DEL_SOLUCIONADOR` (3,41, medida con un solucionador por entropía sobre la
     lista). Usa `palabra.palabra_de` para no pasar de `hasta`.
2. **`tools/seasons.py`**: `instantanea(..., soluciones=None)` añade `"indicadores"` si hay lista.
3. **`tools/materialize_seasons.py`** y **`tools/local_stack.py`**: `descarga_soluciones()` + `descifra()` en el
   borde, con repliegue a `None`.
4. **`v2/js/ui/jugador.js`**: `tarjetaDeIndicadores(indicadores, jugador)` exportada y pintada tras el álbum;
   estilos en `v2/css/styles.css`.

```bash
.venv/bin/python3 -B -m pytest tests/slices/indicadores-de-juego
node --test tests/slices/indicadores-de-juego/
```
