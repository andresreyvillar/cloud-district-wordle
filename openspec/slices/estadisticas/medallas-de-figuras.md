---
slice: medallas-de-figuras
status: proposed
kind: scheduled
actor: sistema
trigger:
  type: cron
  surface: pipeline
  detail: "0 * * * * — materialize_seasons.py · y 0 17 * * 1-5 — post_ranking.py"
events:
  emits: []
  consumes: []
specs:
  - estadisticas
  - dashboard
tests_root: tests/slices/medallas-de-figuras/
blocked: null
---

# Dibujar bien también da medallas

**Actor:** sistema (los dos cron)
**Trigger:** la materialización de la temporada y el resumen diario

## Contexto

Hay siete medallas y **ninguna mira el dibujo**: todas salen de puntuaciones y fechas. El eje de figuras
tiene ranking ([[album-de-figuras]]) pero no logros, así que premia solo a quien encabeza y no a quien
consigue algo concreto.

Este slice añade las cinco que dependían del clasificador y que quedaron desbloqueadas al calibrarlo:
Ornitólog@, Arquitect@, Florista, Coleccionista y Abstract@.

**Los umbrales del brief no valen y se rehacen aquí.** Estaban medidos con el clasificador desmentido, y el
propio brief lo declaraba: «hay que rehacerlos junto a la calibración, no por separado». Con el clasificador
bueno, `Florista` (5 flores) la lograría el 63% —era «raro, 8%»— y `Abstract@` (12 abstractos) el 0,8%, que
era «común, 24%».

## Trigger técnico

`badges.medallas_de_temporada`, que ejecutan los dos cron: el horario al materializar la instantánea y el
de las 17:00 al componer el resumen diario.

Los recuentos por categoría salen del **álbum**, no de un segundo recuento propio: `🦜5` en la tira y
`Ornitólog@` tienen que decir lo mismo o el logro parece roto.

## Comportamiento observable

### cinco-medallas-de-figura
**WHEN** se calculan las medallas de una temporada
**THEN** un jugador gana Ornitólog@, Arquitect@, Florista o Abstract@ si alcanza el umbral de esa categoría,
y Coleccionista si tiene al menos una partida de cada una de las cuatro.

### el-umbral-sale-de-lo-que-alguien-ha-logrado
**WHEN** se fija el umbral de una medalla de figura
**THEN** está justo por debajo del máximo histórico de esa categoría, de modo que la medalla es difícil sin
ser imposible, y su rareza medida corresponde con su nivel.

### el-recuento-es-el-del-album
**WHEN** la tira de un jugador muestra N partidas de una categoría
**THEN** la medalla de esa categoría usa exactamente ese N, sin un segundo recuento que pueda divergir.

### el-espejo-perfecto-tiene-su-logro
**WHEN** alguien deja una cuadrícula simétrica fila a fila y con cuerpo suficiente
**THEN** gana un logro permanente y se anuncia el día que ocurre; y una cuadrícula simétrica de una sola fila
de cuerpo **no** lo gana, porque es simétrica por accidente y lo tendría casi medio grupo.

### el-logro-del-espejo-mira-el-rasgo-y-no-la-categoria
**WHEN** una cuadrícula simétrica está clasificada como flor o como loro
**THEN** el logro se concede igualmente, porque la simetría es un rasgo del dibujo y no su etiqueta.

### sin-patron-no-da-medalla
**WHEN** las partidas de un jugador no tienen cuadrícula guardada
**THEN** no gana ninguna medalla de figura, y tampoco la pierde quien sí las tiene.

### las-figuras-en-el-resumen-diario
**WHEN** alguien gana una medalla de figura en la jornada del día
**THEN** el resumen diario la anuncia igual que las demás, con su emoji y su nombre.

### la-temporada-del-resumen-sale-del-modelo
**WHEN** el resumen diario decide de qué temporada son las medallas
**THEN** usa la misma función que el resto del sistema, no el prefijo de la fecha.

### el-catalogo-completo-aparece-en-la-temporada
**WHEN** se pinta el bloque de logros de una temporada
**THEN** aparecen **todas** las del catálogo, cada una con su nombre, su regla y su icono; el número no se
escribe en el escenario, porque cada logro nuevo lo dejaba desfasado.

### cada-medalla-de-figura-tiene-su-icono
**WHEN** se pinta una medalla
**THEN** su icono referencia un símbolo que el sprite **define de verdad**, no una cadena que aparezca en
un comentario.

## Estado después

`badges.CATALOGO` pasa de 7 a 12 medallas y la instantánea las publica en `logros` como las otras. La vista
de temporada muestra las cinco tarjetas nuevas y la ficha las pinta en el palmarés.

Con los datos de hoy, sobre 122 pares jugador-mes del histórico:

| Medalla | Condición | Lo logran | Nivel |
|---|---|---|---|
| Ornitólog@ | 5 loros en la temporada | 3,3% | legendario |
| Arquitect@ | 4 geométricos | 1,6% | legendario |
| Florista | 11 flores | 11,5% | raro |
| Abstract@ | 7 abstractos | 23,0% | común |
| Coleccionista | las cuatro categorías | 41,0% | común |

## Edge cases

- **Temporada 0**: son 181 jornadas, así que los umbrales pensados para un mes se logran de sobra. Es la
  misma distorsión que ya tienen Fondista o Verdugo en esa temporada, y se acepta igual: inventar aquí una
  regla distinta sería una segunda definición de temporada.
- **Agosto de 2026**: 61 de 80 partidas sin patrón. Nadie gana medallas de figura, y es correcto — no hay
  dibujos que contar. Excluir agosto de la medida movía los umbrales menos de dos puntos, así que no se
  excluye.
- **Recalibrar el clasificador** cambia quién tiene qué medalla, sin migración. Es el mismo precio ya
  declarado para el álbum.

## Slices compañeros

- [[album-de-figuras]] — la tira de la que salen los recuentos.
- [[clasificacion-de-figuras]] — el cálculo que las hace posibles.
- [[medallas-en-el-resumen-diario]] — las siete que no dependen del dibujo.
