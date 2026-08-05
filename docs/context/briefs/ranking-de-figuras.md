# Ranking de figuras — nonogramas y resumen diario

> Síntesis citable. Fuente: diseño acordado en conversación (2026-08-04), validado contra 143
> cuadrículas y 17 jornadas completas extraídas del canal.
> Relacionado: [reglas-temporadas](reglas-temporadas.md) (el otro ranking, el de puntuación).

## Qué es

Un segundo ranking, independiente del de puntuación, basado en **la figura que dibuja la cuadrícula de
emojis** de cada resultado. Cada partida deja un patrón; el patrón se clasifica en una categoría; las
categorías se acumulan en un álbum por jugador.

**No influye en el ranking de puntuación general** (decisión explícita, "por el momento").

**Solo cuentan los días laborables**, igual que los otros dos ejes (decisión de alcance del 2026-08-04,
ver [reglas-temporadas](reglas-temporadas.md)). Un patrón de sábado se captura, se guarda y se puede
mirar, pero no cuenta para el ranking de belleza ni para las medallas de figuras. Afecta a 13 patrones del
histórico de 1533 resultados.

## Lo acordado

### Categorías y emojis

Cuatro categorías. **No existe la categoría "ambiguo"**: todo patrón que no alcance una figura
reconocible es `abstracto`. El clasificador no empata — o reconoce algo, o es abstracto.

**Vocabulario fijado el 2026-08-05**, el que el dueño usó al etiquetar de verdad
([conjunto dorado](../sources/2026-08-05-etiquetado-de-patrones.md)):

| Categoría | Emoji | Qué es, según las etiquetas humanas | Cuenta en el ranking de belleza |
|---|---|---|---|
| loro | 🦜 | columna verde vertical **más** un segundo elemento verde y un amarillo de pico | sí |
| flores | 🌷 | la banda verde final como suelo y amarillos dispersos encima; poca celda, aireado | sí |
| geometrico | 📐 | pocas celdas y forma limpia: un tallo, una pirámide, una escalera | sí |
| abstracto | 🌀 | ruido disperso, o un bloque verde uniforme y grande | **no** — se registra y se muestra, pero el ranking ordena por figuras reconocibles |

`caca` pasa a llamarse **`abstracto`** y `escuadra` a **`geometrico`**. No es cosmética: `caca` se le cuelga
a un tercio de las partidas y, por la correlación −0,37 medida más abajo, sobre todo **a quien juega bien**.
Llamarlo abstracto describe el dibujo en lugar de insultar al jugador.

### Reparto medido: la heurística estaba muy equivocada

| | abstracto | flores | loro | geometrico |
|---|---|---|---|---|
| **Etiquetas humanas** (30) | **33%** | **37%** | 17% | 13% |
| Heurística sin calibrar (143) | 69% | 12% | 8% | 11% |

La heurística mandaba a la papelera el doble de lo que un humano descarta, y veía un tercio de las flores.
Las dos causas están identificadas y son supuestos del propio brief: ver abajo.

La tira del álbum se muestra **agrupada**, no repitiendo emojis: `🦜1 🌷2 📐1 🌀12`. Incluso con un
tercio de abstractos, la tira literal satura la línea.

### Almacenamiento

El patrón vive en **una columna nueva** de `wordle_results`. Aditivo, compatible con la invariante del
[ADR 0005](../../../openspec/decisions/0005-hosting-y-convivencia-v1-v2.md).

Se guarda el **patrón crudo**, no solo la categoría: el clasificador va a mejorar, y guardar solo el
veredicto haría irrecuperable el histórico en cada recalibración.

### El resumen diario cambia

Sustituye la captura del gráfico por un mensaje compuesto:

1. **Jugador del día** — mejor puntuación.
2. **Obra del día** — mejor figura. *(Separado del anterior por evidencia: ver más abajo.)*
3. **Top 5 del ranking** con el emoji de figura de cada uno.
4. **Ranking de belleza** — quién ha aportado más figuras reconocibles, con la tira agrupada (`🦜1 🌷2 📐1 🌀12`).
5. **Comentarios jocosos de la jornada**, con memes o emojis.

## Hechos medidos que condicionan el diseño

### El patrón hoy se descarta, pero es recuperable

La ingesta guarda solo la primera línea del mensaje (`raw_text = "La palabra del día #N X/6"`); la
cuadrícula nunca se persiste. En cambio el canal **conserva el histórico completo**: comprobado a 240
días, las cuadrículas siguen accesibles. El álbum puede nacer con histórico vía backfill.

### ~~La última fila no se analiza~~ — DESMENTIDO por las etiquetas

El brief descartaba la última fila porque el 97% de las cuadrículas resueltas acaban en `GGGGG` y "esa banda
verde dispararía la señal de flor en casi todos los aciertos".

**Estaba justo al revés.** En las etiquetas humanas, esa banda **es el suelo de la flor** y los amarillos
dispersos encima son los pétalos:

```
Y....        ..Y..        .Y..G
.Y..Y        ...Y.        Y.Y.G
GGGGG        .GGG.        GGGGG
             GGGGG
```

Quitar esa fila eliminaba precisamente la señal que define una flor, y de ahí sale la mayor parte del error
del 69%. **El clasificador analiza la cuadrícula completa.**

### ~~En dos filas no hay figura posible~~ — DESMENTIDO por las etiquetas

El brief daba por hecho que una cuadrícula con dos filas sobre la base no puede contener figura, y con eso
mandaba el 37% de las partidas a la papelera por construcción.

Tres de las treinta etiquetas (fichas 01, 03 y 06) tienen exactamente dos filas sobre la base y son
**flores**. El número de filas no decide nada: lo que decide es la densidad y la limpieza del dibujo.

### La tensión entre los dos rankings — HAY QUE VOLVER A MEDIRLA

El brief afirmaba una **correlación −0,37 entre media de intentos y número de cacas**: quien juega mejor
acumula más papelera, porque resuelve pronto y no deja lienzo. Era el mejor efecto del diseño, la razón por
la que los dos rankings premian a gente distinta.

**Esa cifra se midió con el clasificador desmentido**, el que mandaba el 69% a la papelera por contar filas.
Con el número de filas descartado como criterio, el signo puede mantenerse, atenuarse o desaparecer. Queda
**pendiente de remedir** cuando el clasificador esté calibrado, y hasta entonces no se cita como hecho.

Lo que sí sigue en pie, porque no depende del clasificador, es la diferencia de intentos entre partidas con
y sin lienzo (2,9 frente a 4,7): la figura sale de las partidas que salen mal. La *intuición* de que los dos
rankings premian a gente distinta es sólida; la cifra que la medía, no.

### Por eso el "jugador del día" se separa en dos premios

Medido sobre 17 jornadas completas, exigir *mejor puntuación **y** figura reconocible* deja el premio
vacío: el mejor score tiene figura reconocible en **1 de 17 jornadas (6%)**, y en **16 de 17 (94%)** no
tiene ni lienzo. De ahí los dos premios separados: *jugador del día* (puntuación) y *obra del día*
(figura).

### Los comentarios se calibran por frecuencia

Un chiste que sale a diario deja de ser chiste. Frecuencia medida por jornada:

| Comentario | Disparador | Frecuencia | Ajuste |
|---|---|---|---|
| "es sospechoso…" | score ≤2 con media del día ≥4,0 | 0,06 | dejar así: es el chiste estrella por raro |
| "no estaba inspirado" | 1,5 peor que la media del día | 0,71 | **subir a 2,0**: sale casi todos los días |
| "está sembrado" | 1,5 mejor que la media del día | 0,35 | bien |
| "se ha rajado" | ausencia en día difícil | — | reutiliza el modelo de dificultad de [reglas-temporadas](reglas-temporadas.md) |

### Arquitectura: determinista detecta, el modelo redacta

El mismo patrón para las dos piezas creativas:

| Determinista (testeable, golden tests) | Generativo (no verificable más allá de "se produjo") |
|---|---|
| clasificar el patrón en una categoría | generar la imagen de la figura |
| detectar los hechos del día (sospechoso, sembrado, rajado) | redactar el comentario jocoso |
| calcular álbum, top 5 y premios | elegir el meme |

Consecuencia práctica: **la generación de imagen cuesta dinero por pieza**. Con ~10 resultados diarios,
generar todas es inviable; lo razonable es una al día (la obra del día) o solo las de veredicto claro.

## Lo que sigue abierto

| Abierto | Qué falta decidir |
|---|---|
| ~~¿Las partidas sin lienzo son categoría aparte?~~ | **CERRADO por las etiquetas**: el número de filas no decide nada, así que la pregunta desaparece. Hay flores de dos filas sobre la base |
| Puntuación del álbum | Recuento absoluto de figuras reconocibles, o ponderado por rareza. Medido: 🦜 8%, 📐 11%, 🌷 12% — el loro es la pieza rara |
| Calibración del clasificador | **Desbloqueado**: hay 30 patrones etiquetados ([conjunto dorado](../sources/2026-08-05-etiquetado-de-patrones.md)). Falta escribir el clasificador y medir su acierto contra ellos |
| La categoría `loto` | Apareció una vez al etiquetar (ficha 29: dos masas verdes con un canal vertical en medio). **Plegada en `flores` por ahora**: con un ejemplo no se calibra nada, se acertaría por azar. Si al mirar más patrones sale a menudo, se separa |
| Capability | La clasificación es un dominio nuevo (`patrones`?). Crear capability requiere acuerdo explícito |
| Qué pasa con la captura de Playwright | Sustituir la imagen por texto elimina el navegador del workflow diario: menos dependencias y más rápido, pero se pierde el gráfico |

## Cómo funciona el etiquetado en la práctica

**A mano se etiqueta una vez.** Las 30 fichas son el examen, no el mecanismo. En producción no hay humano ni
coste por partida:

1. alguien publica en Slack;
2. el cron horario ingiere y guarda el **patrón crudo** (ya funciona: 1521 de 1521 filas lo tienen);
3. al materializar la temporada, una función pura convierte patrón → figura;
4. el álbum y el ranking de belleza salen de ahí.

Determinista, sin llamadas a ningún modelo y sin céntimos por resultado.

**Se guarda el dibujo, no el veredicto.** La categoría no vive en ninguna columna: se deriva cada vez. Por
eso cambiar un peso **reclasifica todo el histórico solo**, sin migración — y por eso el conjunto dorado es
lo que hace seguro tocarlo: cada cambio se mide en "coincidía en N de 30, ahora en M de 30".

**Equivocarse es barato.** El álbum no toca el ranking de puntuación (decisión explícita), así que una figura
mal puesta es una gracia perdida, no una injusticia en la tabla.

## Límite honesto

**30 etiquetas dan para medir, no para afinar.** El margen de una precisión medida sobre 30 casos es de unos
±9 puntos: distingue "60% frente a 85%", no "78% frente a 82%". Y con cuatro categorías salen unos 7-8
ejemplos por categoría, que es poco para ajustar umbrales finos.

Si el clasificador se queda por debajo de un acierto razonable con la cuadrícula completa, la alternativa es
un modelo mirando el dibujo — y eso cambia el trato: deja de ser determinista, deja de ser gratis y no se
puede cubrir con golden tests. Esa decisión, si llega, es un ADR.
