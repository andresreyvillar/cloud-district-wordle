---
slice: clasificacion-de-temporada
status: proposed
kind: action
actor: grupo
trigger:
  type: ui
  surface: web
  detail: "/ y /t/<AAAA-MM> — la vista del mes con su clasificación"
events:
  emits: []
  consumes: []
specs:
  - ranking
  - dashboard
tests_root: tests/slices/clasificacion-de-temporada/
blocked: null
---

# El grupo ve quién va ganando el mes

**Actor:** el grupo
**Trigger:** abrir la web, o elegir una temporada en el selector

## Contexto

[[temporada-mensual]] define qué es una temporada; esto la ordena. Es la primera vista con contenido real
de la v2.0 y la que responde la pregunta que el grupo hace a diario.

**La clasificación no se calcula sobre las partidas jugadas sino sobre los días de la temporada.** A quien
no jugó un día se le imputa un resultado en función de lo que el grupo sufrió ese día
([brief](../../../docs/context/briefs/reglas-temporadas.md)):

```
imputado(día) = min( max( dificultad(día), media_personal ) + margen , 7 )

dificultad(día)  = media de intentos del grupo ese día
media_personal   = media del jugador en la temporada, contando SOLO sus días jugados
margen(n)        = 0,5 + 0,15 × (n − 1)   ← n es la enésima ausencia del mes
```

Cada pieza está por una razón medida: `dificultad` hace que faltar un día fácil apenas penalice y faltar un
día duro sí; `max(…, media_personal)` impide que faltar mejore tu media (sin ella ocurría en 9 ocasiones del
histórico, con hasta −0,18 de "premio" por faltar); `margen` impide que ausentarse sea mejor que publicar un
mal resultado; y `min(…, 7)` pone el tope en el fallo.

**Efecto medido, y es fuerte:** aplicado a los 8 meses con datos suficientes, el modelo **cambia el campeón
en 6**. En cinco de esos seis, el campeón actual jugó menos de la mitad de los días. La lectura no es que el
modelo sea severo: es que **hoy el ranking lo gana quien juega poco**, porque promediar solo lo jugado
depura los peores días.

## Trigger técnico

El cálculo vive en Python y llega a la web dentro de la instantánea de la temporada
([ADR 0008](../../decisions/0008-donde-vive-el-calculo.md)). La vista lee y pinta: no recalcula, así que
lo que muestra la web y lo que publica el bot no pueden divergir.

## Comportamiento observable

### clasificacion-ordena-por-media-imputada
**WHEN** el grupo abre la temporada
**THEN** los jugadores salen ordenados por su media con las ausencias imputadas, de menor a mayor.

### faltar-nunca-mejora-la-media
**WHEN** un jugador falta un día en el que su media personal es peor que la dificultad del día
**THEN** su media final no mejora respecto a haber jugado ese día con su media habitual.

### ausencia-en-dia-dificil-penaliza-mas
**WHEN** dos jugadores iguales faltan un día cada uno, uno fácil y otro difícil
**THEN** el que faltó el día difícil queda por detrás.

### jugar-poco-no-da-ventaja
**WHEN** un jugador con muy buena media juega solo unos pocos días de la temporada
**THEN** no adelanta a quien ha jugado todos los días con una media parecida.

### faltar-mucho-cuesta-mas-que-faltar-poco
**WHEN** dos jugadores faltan un número muy distinto de días
**THEN** el castigo por ausencia **crece con las ausencias**, de modo que faltar un día sigue costando poco y
faltar casi todo el mes cuesta mucho; con un castigo igual para cada falta, quien jugó 1 de 21 jornadas
quedaba por delante de quien jugó 18.

### empate-se-rompe-por-participacion
**WHEN** dos jugadores tienen la misma media final
**THEN** va delante **en la lista** el que ha jugado más días — pero **comparten puesto**, porque empatar en
la media es haber hecho la misma temporada. El desempate existe para que el orden sea determinista, no para
fabricar una diferencia que no está en los datos (ver [[empates-comparten-puesto]]).

### la-tabla-hace-auditable-la-imputacion
**WHEN** el grupo mira la clasificación
**THEN** cada jugador muestra sus días jugados y su media real además de la final, de modo que se puede
comprobar de dónde sale la diferencia.

### temporada-sin-dias-lo-dice
**WHEN** la temporada elegida no tiene ningún día válido
**THEN** la vista lo explica, en lugar de mostrar una tabla vacía.

### el-titular-cuenta-la-pelea-por-el-primer-puesto
**WHEN** varios jugadores comparten el primer puesto, o el segundo está a una distancia que se remonta en una
jornada
**THEN** el titular lo cuenta como lo que es —un empate o una pelea— y nunca como una ventaja de cero.

### la-vista-dice-cuando-se-calculo
**WHEN** el grupo mira una clasificación
**THEN** la vista indica cuándo se calculó, porque es un dato derivado que puede quedar rancio si el cron
falla.

## Estado después

Nada cambia en la base de datos por mirar la web. La clasificación es una clave más de la instantánea de la
temporada, que el cron recalcula al ingerir.

## Edge cases

- **Un jugador con un solo día jugado** aparece, y aparece abajo. No hay umbral de elegibilidad: la
  imputación ya hace ese trabajo, y verlo en su puesto es más informativo que no verlo
  ([brief](../../../docs/context/briefs/reglas-temporadas.md)).
- **La temporada en curso es volátil la primera semana** por construcción: el día 3 una ausencia es un
  tercio de la nota. Es una consecuencia declarada del modelo, no un fallo.
- **Un día sin muestra suficiente no existe** para este cálculo, así que faltar ese día no penaliza a nadie.

## Fuera de alcance, y por qué

- **Podios separados de intentos y de participación** (Fase 3): el grupo no ha decidido cuál sería el podio
  principal.
- **Nota ponderada media + participación**: con este modelo la participación **ya está dentro** de la media;
  ponderarla otra vez la contaría dos veces.
- **Rachas y remontada**: bloqueadas por el grupo.
- **Las medallas en esta vista**: van con el medallero.

## Nota de proceso, y es importante

**El grupo no ha validado este modelo.** Las temporadas mensuales se votaron 6-0; la imputación se acordó en
conversación de diseño. Como cambia quién gana en 6 de 8 meses, conviene llevarla al canal antes de
publicarla — con el diagnóstico delante, no con la fórmula. Implementarlo no la publica: nada llega al
grupo hasta el merge a `main`.

## Slices compañeros

- [[temporada-mensual]] — define la temporada que este slice ordena.
- [[archivo-de-temporadas]] (TBD) — el mismo cálculo, visto como archivo de las cerradas.
