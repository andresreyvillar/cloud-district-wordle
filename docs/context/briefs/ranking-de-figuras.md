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
reconocible es 💩. El clasificador no empata — o reconoce algo, o es caca.

| Categoría | Emoji | Qué es | Cuenta en el ranking de belleza |
|---|---|---|---|
| loro | 🦜 | masa verde compacta con amarillo pegado como pico | sí |
| flor | 🌷 | banda verde inferior con amarillos separados encima | sí |
| escuadra | 📐 | forma simétrica o geométricamente interesante (escalera, tridente) | sí |
| caca | 💩 | no se reconoce ninguna figura | **no** — se registra y se muestra, pero el ranking ordena por figuras reconocibles |

Reparto medido sobre 143 patrones reales: **💩 69% · 🌷 12% · 📐 11% · 🦜 8%**.

La tira del álbum se muestra **agrupada**, no repitiendo emojis: `🦜1 🌷2 📐1 💩12`. Con un 69% de
cacas, la tira literal satura la línea.

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
4. **Ranking de belleza** — quién ha aportado más figuras reconocibles, con la tira agrupada (`🦜1 🌷2 📐1 💩12`).
5. **Comentarios jocosos de la jornada**, con memes o emojis.

## Hechos medidos que condicionan el diseño

### El patrón hoy se descarta, pero es recuperable

La ingesta guarda solo la primera línea del mensaje (`raw_text = "La palabra del día #N X/6"`); la
cuadrícula nunca se persiste. En cambio el canal **conserva el histórico completo**: comprobado a 240
días, las cuadrículas siguen accesibles. El álbum puede nacer con histórico vía backfill.

### La última fila no se analiza

El **97%** de las cuadrículas resueltas acaban en `GGGGG`. Esa banda verde completa dispararía la
señal de "flor" en casi todos los aciertos, así que el análisis usa solo el *camino* (las filas
anteriores a la solución).

### El 37% de las partidas no tiene lienzo — y son las de los buenos

Quitando la última fila, 53 de 143 cuadrículas dejan 2 filas o menos. En dos filas no hay figura
posible. Esas partidas caen en 💩 (**decisión pendiente**: ver Abierto).

De ahí el mejor efecto del diseño: **correlación −0,37 entre media de intentos y número de cacas**. Es
negativa, o sea que **quien juega mejor acumula más cacas**, porque resuelve en dos o tres intentos y no
deja lienzo. Medido: los tres jugadores con mejor media del periodo tienen 7, 12 y 10 cacas
respectivamente. Ganar el mes y tener el álbum lleno de mierda es la tensión que hace que los dos
rankings no se pisen.

### Los dos rankings premian a gente distinta — y eso es una virtud

| | Intentos medios |
|---|---|
| Partidas sin lienzo (≤2 filas) | 2,9 |
| Partidas con lienzo (≥3 filas) | 4,7 |

La figura sale de las partidas que salen mal. Quien gana el mes en puntuación casi nunca va a ganar el
álbum, y al revés. El ranking de figuras da un premio a quien sufre.

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
| ¿Las partidas sin lienzo (≤2 filas) son 💩 o categoría aparte? | Si son 💩: reparto 69% de cacas y los mejores jugadores son los que más acumulan (divertido, y una sola regla que explicar). Si van aparte: 31% de cacas y 37% sin figura, pero hay que explicar una categoría técnica más |
| Puntuación del álbum | Recuento absoluto de figuras reconocibles, o ponderado por rareza. Medido: 🦜 8%, 📐 11%, 🌷 12% — el loro es la pieza rara |
| Calibración del clasificador | **Sin resolver**: la heurística falla en el único patrón etiquetado disponible. Necesita 20-30 patrones etiquetados a mano para ajustar pesos y medir acierto |
| Capability | La clasificación es un dominio nuevo (`patrones`?). Crear capability requiere acuerdo explícito |
| Qué pasa con la captura de Playwright | Sustituir la imagen por texto elimina el navegador del workflow diario: menos dependencias y más rápido, pero se pierde el gráfico |

## Límite honesto

El clasificador heurístico **no está validado**. Dos síntomas concretos: manda el 69% de los patrones a
💩, y clasifica como 📐 el único patrón que un humano etiquetó como 🦜. Parte de ese 69% es real (el 37%
sin lienzo lo es por construcción), pero el resto apunta a pesos mal calibrados.

La idea es viable —las señales geométricas existen, se calculan y separan casos claros— pero cualquier
ponderación escrita hoy es una conjetura. **Antes de especificar el slice de clasificación hace falta un
conjunto de 20-30 patrones etiquetados a mano** contra el que medir el acierto. Sin eso no hay forma de
saber si la heurística basta o si el trabajo lo tiene que hacer un modelo mirando la imagen.
