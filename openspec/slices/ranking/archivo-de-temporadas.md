---
slice: archivo-de-temporadas
status: proposed
kind: action
actor: grupo
trigger:
  type: ui
  surface: web
  detail: "/temporadas — el archivo: cada temporada con su campeón y el medallero acumulado"
events:
  emits: []
  consumes: []
specs:
  - ranking
  - dashboard
tests_root: tests/slices/archivo-de-temporadas/
blocked: null
---

# El grupo puede ver el archivo de temporadas y quién ha ganado cada una

**Actor:** cualquiera del grupo
**Trigger:** abrir `/temporadas`

## Contexto

Con temporadas mensuales, el histórico deja de ser una lista de partidas y pasa a ser **un palmarés
colectivo**: quién ganó cada mes. Es la vista que da sentido a reiniciar el marcador — sin archivo, ganar
agosto no deja rastro en septiembre.

**Hoy tiene dos filas**, y eso es correcto y no un defecto: la temporada 0 es un bloque único con todo el
histórico anterior a agosto (decisión del 2026-08-05), y agosto es la primera numerada. Crecerá una fila al
mes. El roadmap hablaba de «las 9 cerradas» porque se escribió antes de esa decisión.

La temporada 0 **se marca como lo que es**: un bloque que se jugó con otras reglas. Presentarla junto a las
mensuales sin decirlo invitaría a comparar una media de 181 jornadas sin imputar con una de 20 imputada.

## Comportamiento observable

### el-archivo-lista-las-temporadas-de-la-mas-reciente-a-la-mas-antigua
**WHEN** se abre el archivo
**THEN** hay una entrada por temporada materializada, ordenada por su número de orden descendente, con la
temporada 0 al final.

### cada-temporada-cerrada-muestra-su-campeon
**WHEN** una temporada está cerrada
**THEN** muestra a quien la ganó con su media, y sus totales: jornadas válidas, jugadores y resultados.

### la-temporada-en-curso-no-tiene-campeon-todavia
**WHEN** una temporada está en curso
**THEN** aparece marcada como abierta y quien va primero se presenta como **quien va ganando**, no como
campeón.

### el-medallero-acumula-todas-las-temporadas
**WHEN** se mira el medallero
**THEN** cuenta las medallas de cada jugador sumando todas las temporadas, ordenado de más a menos, y dice
cuántas temporadas ha ganado cada uno.

### la-temporada-cero-se-marca-como-bloque-historico
**WHEN** se muestra la temporada 0
**THEN** queda marcada como bloque histórico jugado con otras reglas, para que su media no se lea como
comparable con la de un mes.

### cada-temporada-enlaza-a-su-marcador
**WHEN** se pulsa una temporada del archivo
**THEN** se abre su marcador.

### sin-temporadas-materializadas-lo-dice
**WHEN** no hay ninguna instantánea
**THEN** el archivo lo declara en lugar de mostrar una lista vacía.

## Estado después

Ninguno: solo lee.

## Edge cases

- **Una temporada vacía** (un mes sin ningún día con muestra suficiente) aparece en el archivo con cero
  jornadas y sin campeón: hacerla desaparecer borraría un mes de la historia.
- **Un empate en el primer puesto** no puede darse: la clasificación ya lo rompe por participación y por
  nombre, así que el archivo se limita a leer el primero.
- **Una temporada cuyo campeón no clasificó** no existe: quien no clasifica no ocupa posición, así que el
  primero de la tabla es siempre alguien clasificado o no hay nadie.

## Fuera de alcance, y por qué

- **El medallero por identidad.** Las medallas se publican por nombre en la instantánea porque
  `tools/badges.py` agrupa por `player_name`; el archivo suma por nombre. Arreglarlo es un slice de
  identidad, y va declarado aquí igual que en [[ficha-de-jugador]].
- **Comparar temporadas entre sí** (evolución del grupo mes a mes): necesita la escala fija comparable
  (Fase 4.4).
- **Cerrar una temporada a mano.** El estado se deriva de los datos: la más reciente con resultados está en
  curso ([[temporada-mensual]]).

## Slices compañeros

- [[temporada-mensual]] — define las temporadas que este archivo lista y de dónde sale su estado.
- [[clasificacion-de-temporada]] — de su tabla sale el campeón de cada entrada.
- [[ficha-de-jugador]] — el otro palmarés, el individual.
