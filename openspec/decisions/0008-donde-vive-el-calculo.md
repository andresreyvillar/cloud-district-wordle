---
adr: 0008
titulo: Dónde vive el cálculo — Python calcula, la web pinta
estado: aceptado
fecha: 2026-08-05
decide: Andrés Rey
afecta: [ranking, estadisticas, dashboard, publicacion]
sustituye_parcialmente: 0004
---

## Contexto

El [ADR 0004](0004-stack-de-la-v2.md) eligió mantener el cálculo en JavaScript (opción B: vanilla con
módulos ES y el dominio separado del render) y dejó un disparador explícito y por escrito:

> **Límite declarado:** si aparece un segundo consumidor de las reglas (un endpoint, un bot que responda
> en el canal, un export), esta decisión se revisa a favor de la opción D. El disparador es explícito:
> **dos consumidores del mismo cálculo**.

**El disparador se ha cumplido**, y no de forma hipotética. Al ir a escribir el modelo de temporada de la
web, estas reglas ya existen implementadas en Python:

| Regla | Implementada en | La web la necesita para |
|---|---|---|
| Día laborable de la temporada | `tools/calendario.py` | toda vista de temporada |
| Muestra mínima del día (≥5 jugadores) | `tools/badges.py` | dificultad del día, imputación |
| Las siete medallas y sus umbrales | `tools/badges.py` | ficha de jugador, medallero |
| Modelo de imputación por dificultad | [brief](../../docs/context/briefs/reglas-temporadas.md), sin implementar | la clasificación mensual |

El pack de medallas ya lo anotó como deuda al implementarlas: *"las medallas tienen dos consumidores
previstos —este resumen en Python y la ficha de jugador en JavaScript—, y el ADR 0004 debería revisarse
antes de escribir el dominio de la web, o habrá dos implementaciones de los mismos umbrales"*.

**Lo que está en juego no es elegancia.** El bot publica cada día en el canal quién va ganando, y la web
muestra quién va ganando. Si las dos implementaciones divergen —un umbral recalibrado en un sitio y no en
el otro, un redondeo distinto— **el grupo lo ve en Slack**, y eso no se arregla con un `git revert`.

## Opciones

**A. Mantener la opción B: la web recalcula en JavaScript.**
*Pro:* la web es autónoma; cambiar de temporada recalcula al instante sin ir al servidor; el dominio se
prueba con `node --test`, que ya funciona.
*Contra:* cuatro familias de reglas implementadas dos veces y en dos lenguajes. La divergencia no es un
riesgo teórico: los umbrales de medallas ya se recalibraron una vez, y las cifras de un brief ya estuvieron
mal dos veces (`docs/lecciones.md`). Mantener dos implementaciones sincronizadas a mano es exactamente el
tipo de trabajo que este proyecto ya ha demostrado que se le escapa.

**B. Opción D del ADR 0004: Python calcula y materializa, la web lee y pinta.**
*Pro:* una sola implementación de cada regla, en el lenguaje donde ya está y con el `pytest` que ya está
montado; el bot y la web comparten números **por construcción**, no por disciplina; recalibrar un umbral es
un cambio en un sitio.
*Contra:* aparece un artefacto materializado que hay que invalidar; la web pierde la capacidad de
recalcular en cliente; y el cálculo pasa a depender de que el cron corra.

**C. Híbrido: las reglas del juego en Python, la presentación en JavaScript.**
*Pro:* menos duplicación que A y más interactividad que B.
*Contra:* hay que decidir caso por caso a qué lado va cada cálculo, y esa frontera se difumina con el
tiempo. La primera vez que una distribución necesite la media imputada, el híbrido se rompe.

## Decisión

**Opción B: Python calcula y materializa; la web lee y pinta.**

El argumento que decide no es la duplicación en sí, es **dónde se paga el error**: una divergencia entre
el bot y la web se publica delante de quince personas. Y el proyecto tiene evidencia propia de que
mantener dos verdades sincronizadas a mano no le sale bien.

### El artefacto: una instantánea por temporada, con carga útil JSONB

Tabla nueva `season_snapshots`, **aditiva** y sin tocar nada de lo que lee la v1
([ADR 0005](0005-hosting-y-convivencia-v1-v2.md)):

```
season_snapshots
  temporada    text primary key      -- 'AAAA-MM'
  payload      jsonb not null        -- todo lo calculado de esa temporada
  updated_at   timestamptz not null
```

**Por qué JSONB y no columnas.** El modelo de temporada **no está cerrado**: los podios separados, la nota
ponderada, las rachas y la remontada siguen bloqueados por el grupo (Fase 3 del roadmap). Con columnas,
cada regla que el grupo cierre sería una migración; con una carga útil, es una clave más. La consecuencia
aceptada es que el artefacto no se puede consultar con SQL — y no hace falta: tiene un solo productor
(el cron) y un solo consumidor (la web), y son diez temporadas.

**Qué NO va en la instantánea:** los resultados crudos. La vista `/datos` y la de `/hoy` leen
`wordle_results` directamente, porque son la tabla tal cual y no un cálculo.

### Cómo se invalida

El cron horario que ya corre (`update_stats.yml`) recalcula la instantánea de **la temporada en curso**
después de ingerir. Las cerradas se recalculan solo si se pide a mano, y por eso recalibrar un umbral
exige un comando explícito: es una decisión, no un efecto secundario.

## Consecuencias

**Se vuelve fácil:** que el mensaje del canal y la web digan lo mismo, por construcción; probar cualquier
regla del juego con `pytest`, que ya tiene fixtures y prueba de mutación; recalibrar un umbral en un solo
sitio; y que la web sea trivial —lee un objeto y lo pinta—, lo que hace las vistas más rápidas de escribir.

**Se vuelve difícil:** la web ya no puede inventarse una vista sin tocar Python. Un filtro nuevo que
necesite un agregado que no está en la instantánea deja de ser una tarde de JavaScript y pasa a ser un
cambio en el pipeline más un recálculo.

**Se vuelve difícil también:** hay un estado derivado que puede quedar rancio. Si el cron falla, la web
muestra la instantánea vieja **sin saber que es vieja**, salvo que se mire `updated_at`. Mitigación
obligatoria: la web muestra la antigüedad de lo que pinta cuando pasa de un umbral, y eso es un Requirement
de `dashboard`, no un detalle.

**Lo que el ADR 0004 conserva:** vanilla con módulos ES, sin build, y `js/domain/` separado del render. Lo
que cambia es qué vive dentro de `js/domain/`: **presentación y formato**, no reglas del juego. El router,
el borde de datos y el armazón del [esqueleto](../changes/chore-esqueleto-v2/proposal.md) siguen siendo
válidos tal cual.

**Deuda declarada:** las medallas ya están calculadas en `tools/badges.py` pero **no materializadas**. Hasta
que la instantánea las incluya, la ficha de jugador no puede mostrarlas. Va en el slice del medallero, no
aquí.
