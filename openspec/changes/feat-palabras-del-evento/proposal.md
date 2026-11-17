# feat-palabras-del-evento

## Why

Cambio de última hora del evento de la empresa: no serán frases sino **palabras**, el Wordle de siempre, todas
seguidas. Solo juega quien está en una lista cargada de antemano, repartida en diez grupos, y los puntos se cuentan por
grupo para quien lleva la cuenta del evento. El admin activa el evento cuando quiere; hasta entonces el enlace solo
dice que se activará en breve.

## What Changes

| Decisión | Quién | Valor |
|---|---|---|
| Reglas | dueño (y diseño) | Wordle de siempre: 5 letras, 6 intentos, verde/amarilla/gris por posición |
| Orden | dueño | Las palabras se juegan seguidas; «Siguiente palabra k/N» tras cada una |
| Cronómetro | dueño | Uno por palabra: de pulsar Empezar/Siguiente a resolver o fallar; sin pausa |
| Puntos por palabra | dueño, medido con eventos simulados | Marca = tiempo + 30 s por intento; 1 + resolvedores con peor marca; fallada o a medias, 0 |
| Puntos del grupo | dueño | Media de toda la lista; quien no juega cuenta 0 |
| Activar y terminar | dueño | El admin, con PIN de 4 cifras; 5 fallos bloquean el PIN 1 minuto |
| Nombres | dueño | De la lista, con buscador y desplegable; el primer móvil se lo queda; el admin lo libera |
| Exportación | dueño | JSON y CSV mientras llega el formato de la API externa |
| Estética | diseño | Negro y #FAF9F4, Host Grotesk; casillas con los colores del Wordle (no los de la marca: el evento es con otras empresas) |
| Antes de activar | dueño | Solo «El evento se activará en breve» |

La simulación (110 participantes, 10 grupos, 5 palabras, distribución real de intentos del canal) comparó «los
intentos mandan» con marcas de 15, 30, 45 y 60 s por intento: con 30 s la clasificación se repite más entre dos
mañanas iguales (0,50 frente a 0,37) y solo un 9 % de los pares acaban con el de más intentos delante. Queda por medir
la dispersión real de los tiempos: la demo la dará.

## Out of Scope

- Enviar los puntos a la API externa (formato pendiente).
- El juego de frases: sus tablas se quedan, sus funciones dejan de ser públicas.
- Comprobar que quien elige un nombre es esa persona.

## Impact

Migración aditiva `20261117120000_event_words_game.sql` (sin `drop`). Web: `v2/js/evento/{dominio,api,jugador,admin}.js`,
`v2/css/evento.css`, rutas `/evento` y `/evento/admin` (sale `/evento/pantalla`). Slices `palabras-del-evento` y
`admin-del-evento` (sustituyen a `frase-del-evento` y `pantalla-del-evento`).
