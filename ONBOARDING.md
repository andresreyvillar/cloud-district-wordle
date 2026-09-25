# SuperWordleBros en la web — handoff para Joel

> Para Joel y para su Claude. Explica cómo está montado tu juego dentro de la web del Wordle de CloudDistrict,
> qué se ha cambiado de tu prototipo y cómo se trabaja en este repositorio para que sigas manteniendo la
> pestaña.

## Para pegar en Claude Code

```text
Voy a mantener la pestaña SuperWordleBros de la web de wordle-stats (repo andresreyvillar/cloud-district-wordle).
Antes de tocar nada, lee en este orden: ONBOARDING.md, CLAUDE.md, openspec/slice-system.md (la constitución),
docs/juego-contrato.md y openspec/slices/dashboard/juego-de-la-jornada.md, nivel-congelado.md y
ranking-del-juego.md. Después resúmeme cómo está montado el juego y qué partes son mías, y espera a que te
diga qué cambio quiero. Todo cambio de comportamiento del juego va como slice (/slice-propose y luego
/slice-implement), en una rama, y acaba en un PR que revisa y mergea Andrés. No escribas en la base de datos de
producción ni publiques en Slack.
```

## 1. Qué hay publicado

- **Web:** https://cloud-district-wordle.clouddistrict.workers.dev/2/juego (pestaña **SuperWordleBros**, con
  el sticker «¡NUEVO!» hasta el 9 de octubre). La cabecera dice que el juego es tuyo: «un juego de Joel».
- **El nivel es la jornada de ayer**, con las cuadrículas de todos como escenario, tal como lo diseñaste:
  8 columnas por jugador, la cuadrícula en las 5 centrales, de abajo arriba, verde y naranja como bloques.
- **El nivel se congela.** Un cron lo genera una vez al día, **a partir de las 02:00 de Madrid**, y lo guarda
  en la tabla `game_levels`. Desde ese momento no cambia, así que todos juegan el mismo escenario. Hasta las
  02:00 se sigue jugando el de anteayer.
- **Ranking por nivel.** Debajo del juego, cada uno elige su nombre («¿Quién eres?») y cada llegada a la meta
  guarda su tiempo. Solo se sobrescribe si mejora la marca. Sin login: es un juego de confianza.
- **Compartir.** Al terminar sale un texto para copiar y pegar en el canal, como el Wordle.

## 2. Qué se ha cambiado de tu prototipo

Tu motor está en `v2/js/juego/motor.js`. Es tu código, y cada cambio va marcado en el fichero con
`ADAPTACIÓN n`:

| # | Qué | Por qué |
|---|---|---|
| 1 | El nivel llega por parámetro (`montar(lienzo, nivel, Phaser)`) | lo genera la web desde la tabla, no desde Slack: salen todos los jugadores y con su nombre de la web |
| 2 | Se monta en el lienzo de la pestaña, con escala `FIT`, teclado solo en el lienzo y la rueda libre | para no robarle el teclado ni el scroll al resto de la web |
| 3 | Al llegar a la meta dispara el evento `superbros:fin` con `{ segundos, estrellas }` | la página escribe el texto para compartir y guarda el tiempo en el ranking |
| 4 | **El pisotón** (propuesta, no tuya) | el nivel del 24 de septiembre era injugable: ver abajo |
| 5 | Aviso `superbros:pista-pisoton` justo antes del primer muro que el salto normal no sube (propuesta) | la página enseña un GIF tutorial la primera vez |

### El pisotón, y por qué está

Con tu física, el salto máximo sube 3,52 bloques, pero una cuadrícula puede levantar una pared de 4, 5 o 6. El
nivel del 24 de septiembre empezaba con una pared de 4 y no se podía terminar. Andrés pidió una mecánica
exigente que no rompiera el reto:

- En el aire, **↓ (o S)**: caes en picado.
- Si pulsas **Espacio** en los 0,1 s siguientes a tocar el suelo, rebotas **5 casillas** hacia arriba y
  sales disparado hacia delante a velocidad de carrera, con un destello y chispas.
- Se consigue mejor corriendo con **Shift**.

**Es una propuesta y la decisión es tuya**: quedártela, ajustarla (`PISOTON_VENTANA`, `PISOTON_CASILLAS`) o
cambiarla por otra cosa (doble salto, salto más alto…). Si la cambias, ten en cuenta que dependen de ella la
guía de controles y el tutorial (`v2/js/ui/juego.js`), el GIF `v2/assets/juego/pisoton.gif` y el aviso
`superbros:pista-pisoton`. El GIF se grabó del propio motor con un script que no está en el repositorio: si
cambias la mecánica, habrá que grabarlo de nuevo.

Problemas conocidos: una pared de 6 **desde el suelo** no se salva ni con el pisotón (sí desde lo alto del
tramo anterior), y una de 5 desde el suelo se pasa por un margen de unos 5 píxeles que depende de la duración
del fotograma.

## 3. Qué es tuyo y qué no

| Tuyo | No tuyo (cambiar solo con slice y avisando) |
|---|---|
| `v2/js/juego/motor.js` — el motor | `v2/js/domain/superbros.js` — el generador `nivelDe` (lo ejecuta el cron) |
| `v2/assets/juego/` — tus recursos | `v2/js/ui/juego.js` — la pestaña: cabecera, guía, tutorial, ranking, compartir |
| | `tools/congelar_nivel.mjs` y `.github/workflows/` — el cron |
| | `supabase/migrations/` — las tablas y la función del ranking |

Lo que tu motor tiene que seguir cumpliendo está en **`docs/juego-contrato.md`**, que es el contrato
completo. Lo esencial:

- **`superbros:fin` en cada partida terminada**, también tras reiniciar con R, con `segundos` sin redondear.
  El ranking usa centésimas.
- **Teclado solo en el lienzo** (`keyboard: { target: lienzo }`) y `preventDefaultWheel: false`.
- **Acepta la forma del nivel que ya existe.** Los niveles congelados conservan su forma: el día que entre tu
  cambio, el nivel en juego se congeló con la anterior.
- **La velocidad máxima importa al ranking.** La base de datos rechaza tiempos por debajo de
  `tramos × 8 × 32 px ÷ 450 px/s` (tu `RUN_SPEED` de 300 con un 50 % de margen). Si subes `RUN_SPEED` o el
  impulso por encima de 450 px/s, o cambias `TILE`, hay que tocar la función `registrar_tiempo`.
- **El motor no habla con Supabase ni con Slack.** Nada de datos por su cuenta, ni código cargado en caliente.
  Phaser 3.70.0 ya lo carga la página, con la versión fijada.

## 4. Cómo está montado el repositorio

- **Pipeline** (Python 3.12, GitHub Actions): lee el canal de Slack y guarda los resultados en Supabase, calcula
  la temporada, publica el resumen diario y, desde ahora, congela el nivel del juego.
- **Web v2** (`v2/`): HTML, CSS y JavaScript sin build, publicada por Cloudflare Workers en `/2/`. La v1 sigue
  en `/`.
- **Datos:** Supabase. La web usa la clave pública, que solo puede leer, más la función `registrar_tiempo` del
  ranking.
- **Mergear a `main` despliega.** La web se publica sola en segundos y los cron corren con el código nuevo.

```
openspec/slice-system.md     ← la constitución del método: leer antes de nada
openspec/slices/dashboard/   ← juego-de-la-jornada · nivel-congelado · ranking-del-juego
openspec/changes/<id>/       ← un change pack por cambio (propuesta, tareas, deltas, runs)
v2/js/juego/motor.js         ← tu motor
tests/slices/<slice>/        ← los tests de cada slice
docs/juego-contrato.md       ← el contrato entre la web y tu motor
docs/lecciones.md            ← lo que ha salido mal y la regla que dejó
```

## 5. Cómo se trabaja: slices

El repositorio se desarrolla **por slices verificables**: la especificación es la fuente de verdad y el código
se demuestra con tests.

- Un **slice** describe un comportamiento observable con escenarios `WHEN / THEN`. El juego ya tiene tres:
  `juego-de-la-jornada`, `nivel-congelado` y `ranking-del-juego`. Cambiar cómo se juega es **modificar**
  `juego-de-la-jornada`, no crear otro.
- Cada cambio va en un **change pack** (`openspec/changes/<id>/`): propuesta, tareas, deltas de la spec y el
  registro de ejecuciones.
- **TDD:** primero los tests de cada escenario, en rojo; luego el código. Cada test lleva la anotación
  `/** @scenarios <slug> */`.
- **Gates:** validar el slice, 100 % de escenarios con test, los gates mecánicos y una **prueba de mutación**:
  romper a propósito el código nuevo tiene que poner en rojo justo el escenario que lo cubre.
- Tu Claude tiene los skills en `.claude/skills/`: **`/slice-propose`** para especificar el cambio y
  **`/slice-implement`** para implementarlo con los gates.

## 6. Entorno local

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt   # harness y tests de Python
.venv/bin/playwright install chromium                                    # para las pruebas de navegador
node --version                                                           # 20.19 o superior (22 en CI)
python3 tools/serve_v2.py                                                # http://localhost:8788/2/juego
```

> ⚠️ **La web local usa la base de datos de producción.** Lee los datos reales, y **si eliges nombre y
> terminas el nivel, tu tiempo se guarda en el ranking de verdad**. Para probar, no elijas nombre, o intercepta
> la llamada a `rpc/registrar_tiempo` en tus pruebas de Playwright. Y no uses `tools/local_stack.py`: escribe en
> Supabase.

No necesitas `.env` ni ninguna clave para trabajar en el motor.

## 7. Antes de abrir el PR

```bash
node --check v2/js/juego/*.js
node --test tests/
python3 -m tools.wslice slice validate juego-de-la-jornada
python3 -m tools.wslice slice coverage juego-de-la-jornada
python3 -m tools.wslice verify gates --slice juego-de-la-jornada --change-id <tu-change-id>
.venv/bin/python3 -B -m pytest
```

Y **pruébalo en el navegador como lo usará el grupo**, porque los tests de Node no montan el motor. Dos fallos
de esta semana solo se vieron así: el juego no arrancaba con la suite en verde, y la pestaña llevaba a la
portada porque todas las pruebas entraban escribiendo la URL.

1. Entra **pulsando la pestaña** desde otra sección, no escribiendo la URL.
2. Comprueba primero que **el personaje se mueve**; luego lo que hayas cambiado.
3. Termina un nivel y comprueba que sale el texto para compartir (sin elegir nombre).

## 8. Reglas del repositorio

- **Es público y los datos son de compañeros.** Nada de datos del canal en el repo, ni tokens en código, tests
  o documentación.
- **Nunca se trabaja en `main`.** Rama `feat/<change-id>` en este mismo repositorio (eres colaborador), PR, y
  **Andrés revisa y mergea**: mergear despliega. `main` está protegida: sin PR y sin la aprobación de Andrés no
  entra nada, una aprobación se invalida si subes algo después, y no se puede hacer force-push ni borrarla.
- **Los secretos del repositorio están a tu alcance**, también desde tus ramas: el token del bot de Slack (lee
  el historial del canal y sube archivos) y la clave de servicio de Supabase (escribe en todo). Úsalos con
  cabeza. No lances a mano `post_ranking` ni `post_podium`: publican delante de todo el grupo.
- **Nada de escrituras exploratorias en producción**, ni publicar en Slack fuera del workflow.
- Commits en inglés, sin trailers de atribución y sin mencionar herramientas de IA. Especificaciones y
  documentación en español.

## 9. Ideas abiertas que son tuyas

- Qué hacer con los muros imposibles: quedarse con el pisotón o cambiarlo por otra mecánica.
- **Controles táctiles**: en el móvil hoy se ve pero no se juega.
- El criterio del tutorial: hoy sale una vez por navegador. Una alternativa es enseñarlo hasta el primer
  pisotón conseguido.
