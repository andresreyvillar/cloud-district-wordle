# Proposal — chore-animaciones

> **Slice:** N/A — presentación. Los mismos datos, moviéndose. Ninguna ruta, ningún cálculo y ningún
> número cambian.

## Why

Lo pidió el dueño: animaciones elaboradas, efectos de scroll, que se vea moderna y dinámica.

**Conste que contradice el documento de diseño.** La dirección visual acordada
([liga arcade](../../../docs/context/sources/2026-08-05-diseno-liga-arcade.md)) pide «plano, sin sombras,
bordes gruesos». Se hace igualmente porque lo decide el dueño, y para que el movimiento no se coma la
legibilidad se ata a tres reglas, todas comprobadas:

1. **Solo `transform` y `opacity`.** Las resuelve el compositor sin recalcular posiciones. Medido: **cero
   fotogramas por encima de 50 ms** en un recorrido completo de la temporada 0, que tiene 181 columnas de
   dificultad y 1502 resultados.
2. **Corto y con frenada.** Nada por encima de 600 ms: esto es un marcador que se consulta, no una
   presentación que se contempla.
3. **`prefers-reduced-motion` lo apaga entero**, no lo atenúa.

## Qué se mueve

| Efecto | Dónde |
|---|---|
| Revelado al entrar en pantalla, escalonado | bloques, podio, logros, tarjetas de temporada, reglas |
| Cifras que suben hasta su valor | HUD, podio, tasa del álbum, totales de la ficha |
| Barras que crecen desde su base | dificultad por jornada y distribución de intentos |
| Casillas que entran en cascada | tiras de jornadas |
| Cabecera que se despega al bajar | sombra y menos alto |
| Barra de progreso de lectura | dirigida por scroll, **sin JavaScript** |
| Transición entre vistas | `startViewTransition` al navegar |
| Micro-interacciones | botones de nombre, tarjetas y medallas ganadas |

## La regla que no se puede romper

**Una animación no puede alterar lo que la web dice.** Un número que cambia, aunque sea durante 600 ms,
convierte el marcador en algo en lo que no se puede confiar.

Por eso el contador **guarda el texto original y lo restaura tal cual**, en lugar de reformatearlo al
llegar: reconstruirlo podía devolver `3.2` donde la vista puso `3,20`, o `1502` donde puso `1.502`. Hay un
test que lo fija sobre los seis formatos que aparecen de verdad.

Y el estado inicial invisible **lo pone JavaScript**, no la hoja de estilos: si el observador no llegara a
ejecutarse, un `opacity: 0` de CSS dejaría la web en blanco. Así, el peor caso es que no haya animación.

## Accesibilidad, que aquí no es opcional

El movimiento de aparición y de escala provoca mareo real a quien tiene un trastorno vestibular, y «más
lento» no lo arregla. Con `prefers-reduced-motion: reduce`:

- no se registra ni un observador y no se marca nada como revelable;
- las cifras se quedan en su valor final desde el primer fotograma;
- la regla de CSS que lo apaga va **la última del fichero**, para ganar sin depender de la especificidad.

Comprobado en navegador con la preferencia activada: **cero elementos ocultos sin hacer scroll, cero clases
de revelado y las cifras intactas**.

## Verificación

- 10 tests nuevos · suite JS completa en 32.
- Navegador, con y sin movimiento reducido, en las seis vistas: **ningún elemento se queda oculto** tras
  recorrer la página, y sin errores de consola.
- Un mutante que quita la desconexión del observador anterior pone el test en rojo: navegar veinte veces
  dejaba veinte observadores vivos trabajando en cada scroll.
