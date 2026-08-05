# Tasks — chore-esqueleto-v2

Plan para un implementador **sin contexto previo**. Si un paso no verifica, **para** y reporta.

`Slice: N/A` — plantilla sin comportamiento observable. No hay escenarios que cubrir; sí hay que probar el
router, que es la única lógica del pack.

## Tarea 0 — Preflight

```bash
node --version          # hace falta 18+ para `node --test`
.venv/bin/python3 -B -m pytest -q
```

## Tarea 1 — El router y sus unitarios

`v2/js/router.js`: función **pura** `resolver(ruta)` con el mapa del ADR 0006, más `rutaDe()` (la inversa,
para construir enlaces) y `seccionDe()` (qué sección de la navegación contiene una vista).

Tests en `tests/v2/router.test.js`:

```bash
node --test tests/v2/
```

Cuidado con dos cosas que no son obvias:

- **Un mes que no existe no es una temporada.** `2026-13` tiene la forma correcta; el patrón tiene que
  rechazarlo.
- **Un nombre en el segmento de jugador no puede colar.** El identificador es el de Slack, y aceptar un
  nombre reintroduciría el problema que la Fase 1 arregló.

## Tarea 2 — El borde de datos

`v2/js/data/results.js`: lectura de Supabase **paginando de forma explícita** (PostgREST devuelve 1000 por
página; contar sobre una sola ya produjo una cifra falsa una vez) y `normalizar()` como **único** punto de
mapeo de la forma de una fila.

`leerTodo()` recibe el cliente por parámetro para poder sustituirlo; `cargarResultados()` crea el real.

## Tarea 3 — Armazón y documento

`v2/js/ui/shell.js` (cabecera, navegación, selector, marcador de posición) y `v2/index.html`. Todo lo que
entra al DOM desde datos pasa por `escapar()`.

`v2/js/domain/` se queda **vacío**: cada regla del juego llega con su slice.

## Tarea 4 — Arranque local

`tools/serve_v2.py`, con el mismo fallback que el Worker: `index.html` con 200 para cualquier ruta que no
sea un archivo real.

```bash
python3 tools/serve_v2.py
```

**No sirve `python3 -m http.server`**: devuelve 404 en `/t/2026-07` y el router no llegaría a ejecutarse.

**Verificación de las rutas:**

```bash
for r in / /t/2026-07 /t/2026-07/j/U08U27DFDL2 /temporadas /hoy /datos /ruta-mala; do
  curl -s -o /dev/null -w "$r %{http_code} %{content_type}\n" "http://localhost:8788$r"
done
#   esperado: 200 text/html en las siete
curl -s -o /dev/null -w "%{content_type}\n" http://localhost:8788/js/router.js
#   esperado: text/javascript — sin ese MIME los módulos ES no cargan
```

## Tarea 5 — El Worker y la convivencia con la v1

`wrangler.v2.jsonc` con `directory: "./v2"` y `not_found_handling: "single-page-application"`.

Y **`v2/` en `.assetsignore`**: el Worker de la v1 publica la raíz del repo, así que sin esa línea serviría
la v2 a medio hacer en `/v2/index.html`.

```bash
grep -q '^v2/$' .assetsignore
```

## Tarea 6 — Verificación en navegador

No es opcional y no se sustituye por los unitarios: lo que hay que comprobar es que el documento **pinta**.
Con Playwright, que ya está en el entorno:

```bash
python3 tools/serve_v2.py &
# recorrer las siete rutas, y por cada una:
#   [data-vista] section existe
#   la sección activa de la navegación es la que corresponde
#   el selector de temporada tiene opciones (prueba de que la carga de Supabase funcionó)
#   la consola no tiene errores
```

**Esta comprobación cazó un fallo que los unitarios no veían**: en la ficha de jugador no se marcaba
ninguna sección activa. De ahí salió `seccionDe()`.

## Tarea 7 — Gates

```bash
node --check v2/js/router.js v2/js/app.js v2/js/ui/shell.js v2/js/data/results.js
node --test tests/v2/
.venv/bin/python3 -B -m pytest -q
```

**Gate 4c — mutación** sobre el router (`git add -A` antes, re-stagear tras cualquier arreglo). Ojo: en zsh
una variable sin comillas **no** se parte en palabras, así que el comando de test va escrito en línea.

| Mutación | Test que debe caer |
|---|---|
| el patrón de temporada acepta cualquier mes | `un mes que no existe no es una temporada` |
| el jugador no se contiene en Temporada | `la ficha de jugador se navega dentro de la sección Temporada` |
| el segmento de jugador acepta cualquier cosa | `un nombre en el segmento de jugador no cuela` |
| las rutas transversales ignoran segmentos de sobra | `lo que no encaja se declara desconocido` |

**Gate 4e — security review:** la clave de Supabase del cliente es la **publicable**, con RLS de solo
lectura, la misma que la v1 ya expone. Todo lo que entra al DOM desde datos pasa por `escapar()`.

## Tarea 8 — Registrar y cerrar

1. Entrada en `runs.yaml`.
2. `git add -A` y **parar**.
