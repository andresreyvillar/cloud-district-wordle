# Proposal — feat-figuras-simetricas

> **Slice:** `clasificacion-de-figuras` (modificación: una señal más para el geométrico)

## Why

El clasificador manda a abstracto dibujos que a la vista son geométricos de manual. Dos casos encontrados
mirando resultados reales:

```
arco       G...G / GG.GG / GGGGG          densidad 0,60 → abstracto
escalera   G..../GG.../GGG../GGGG./GGGGG  densidad 0,50 → abstracto
```

Los dos caen por el mismo sitio: el geométrico exige **densidad ≤ 0,40**, y su docstring promete
explícitamente «un tallo, una pirámide, **una escalera**». La regla no cumple lo que dice.

La causa de fondo es que el clasificador mide **escasez de tinta** y usa eso como sustituto de la
regularidad. Son cosas distintas: un dibujo puede ser perfectamente regular y estar lleno. Lo que hace
geométrico a un geométrico es la forma, y de la forma no se medía nada.

## Lo que se añade

La **simetría en espejo**: cada fila del cuerpo igual leída al revés. Con cinco columnas es el espejo
respecto a la columna central, y es barato de calcular.

La propiedad que la hace aceptable —y que el candidato descartado en la calibración original no tenía— es
que **no crece con el tamaño de la cuadrícula**. Aquella regla («una fila verde ancha y algún amarillo») se
cumplía más según se alargaba la partida y convertía en flor el 55% de producción. Un espejo es igual de
difícil en dos filas que en cinco.

## Medido antes de implementarlo

```
              acuerdo    flores  abstracto  loro    geo      (humano 37/33/17/13)
actual        24/30 80%   46,6%    32,9%   13,4%   7,1%
espejo ≤0     24/30 80%   46,3%    32,5%   13,4%   7,8%   ← se elige
espejo ≤1     23/30 77%   43,7%    30,8%   13,4%  12,1%
espejo ≤2     21/30 70%   36,0%    26,1%   13,4%  24,5%
```

El espejo exacto **no rompe ni una ficha**: los seis desacuerdos con el etiquetado humano son exactamente
los mismos que antes (01, 16, 17, 26, 29, 30). Y mueve el geométrico hacia el 13% que puso el humano.

## Dónde va el espejo, y por qué eso importa más que el umbral

La primera versión de esta propuesta ponía el espejo como segunda vía del geométrico, evaluada en el mismo
sitio que la densidad. Estaba mal, y lo delataron los fixtures del propio slice:

```
FLOR       "Y...Y/..Y../GGGGG"   ← simétrica
ABSTRACTO  "GG.GG/GGYGG/GG.GG/GGGGG"   ← simétrica
```

Unos pétalos son simétricos por naturaleza. Como el geométrico se evalúa antes que la flor, el espejo le
robaba la categoría a flores legítimas — los «5 flores → geométrico» que aparecían en la primera medición no
eran casos marginales, eran flores.

Puesto **en último lugar**, cuando ninguna otra regla ha reconocido nada, el espejo gana una propiedad que
se puede verificar: **solo puede ascender abstractos**. Ninguna cuadrícula que hoy tiene figura la pierde.

```
                  acuerdo   flores  abstracto  loro    geo     mueve
actual            24/30 80%  46,6%    32,9%   13,4%   7,1%    —
tras la flor      24/30 80%  46,6%    32,5%   13,4%   7,5%    6 abstracto→geométrico
espejo con ≤1 amarillo  24/30 80%  46,6%    32,6%   13,4%   7,4%    4 abstracto→geométrico
```

Se elige el primero: protege lo mismo y rescata dos casos más.

**La tolerancia se descarta**, aunque su reparto sea mejor. Admitir un defecto cuesta una ficha del examen y
multiplica por siete la cobertura del espejo (1,1% → 7,7%), que empieza a comerse flores. Es el mismo canje
que tumbó al primer candidato: mejor reparto a cambio de acertar menos. Los dos criterios se miden juntos
precisamente para no volver a caer en él.

## Impact

- **6 de 1561 patrones** se reclasifican, todos **desde abstracto** a geométrico. Ninguna figura se pierde.
- El **ranking de figuras de agosto no cambia**: mismos puestos y mismas medias para los nueve
  clasificados. El único movimiento es una jugadora sin puesto, que sube de 0,00 a 3,00 pts/partida.
- **La temporada 0 sí se mueve, y más de lo que esta propuesta anticipaba.** Once jugadores cambian de
  puesto o de media; el mayor salto es de **16º a 11º** (0,80 → 0,92). El podio no cambia.
- **Una medalla cambia de manos**: el que sube de 16º a 11º alcanza el umbral de `arquitecto` en la
  temporada 0. No es un efecto colateral inesperado —las medallas de figuras leen los recuentos del
  álbum—, pero es el palmarés de una persona real, así que lo decide el humano y no el gate.
- Un fixture de los tests del slice (`ABSTRACTO`) es simétrico y pasa a geométrico. Hay que **sustituirlo por
  un abstracto asimétrico**, no relajar la aserción: el fixture era ambiguo por casualidad.
- Como la categoría no se almacena, el cambio es **retroactivo** en la siguiente materialización. Es el
  precio ya declarado de derivarla del patrón crudo.
- El conjunto dorado gana la ficha del arco, hoy ausente de las 30. Una regla nueva sin su caso en el
  examen es una regla sin red.

## Out of Scope

- **La escalera sigue en abstracto.** Es regular respecto a la diagonal, no al eje vertical: seis celdas
  rompen su espejo. Arreglarla pide otra señal y otra medición.
- **No se toca el techo de densidad** (0,40). El espejo se añade como vía alternativa, no lo sustituye.
- **No se toca el docstring que promete la escalera** más allá de dejar de prometerla.
- **Ninguna otra categoría.** Loro y flores mantienen sus reglas y su orden de evaluación.

## Validation Gates

- `wslice slice validate clasificacion-de-figuras` · `wslice verify slice` · `wslice verify gates`
- Acuerdo con el conjunto dorado **≥ 24/30** tras añadir la ficha 31 (`calibrate_figures.py --sin-red`).
- El geométrico se queda **por debajo del 13%** del reparto humano en producción.
- Prueba de mutación sobre la tolerancia: cambiar el espejo exacto por «un defecto» debe poner en rojo el
  escenario `una-celda-rota-no-es-espejo`.

## Capabilities

| Capability | Requirements |
|---|---|
| `ranking` | MODIFIED — La simetría en espejo cuenta como geométrico |
