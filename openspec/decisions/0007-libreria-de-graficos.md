---
adr: 0007
titulo: Librería de gráficos y forma de las visualizaciones de la v2.0
estado: aceptado
fecha: 2026-08-04
decide: Andrés Rey
afecta: [dashboard, estadisticas, ranking]
---

## Contexto

La v1 tiene tres visualizaciones: un gráfico de burbujas (media vs partidas), un gráfico de líneas con
la evolución diaria, y una distribución de intentos hecha con `div`s y CSS. Las dos primeras usan Plotly
2.27 cargado por CDN.

El grupo ha pedido **escala horizontal fija en todos los gráficos** para poder comparar meses y animar
la evolución, y la petición general es "más dinamismo y modernidad manteniendo la funcionalidad".

### El problema no es la librería, es la forma

Auditados contra el catálogo de anti-patrones de visualización, los gráficos actuales incumplen seis
reglas, y **ninguna se arregla cambiando de librería**:

| Gráfico | Anti-patrón | Por qué falla |
|---|---|---|
| Evolución | **hues cicladas más allá de 8** | Hay hasta 22 jugadores y la paleta de Plotly tiene 10 colores: se repiten. Dos jugadores comparten color y nadie puede distinguirlos |
| Evolución | **8 hues cuando la historia es un número** | 22 líneas superpuestas no cuentan nada. La forma correcta para "cómo voy yo frente al grupo" es **emphasis**: una serie en color, el resto en gris |
| Burbujas | **value-ramp que duplica un canal** | El color codifica la media, que ya es el eje X. Se gasta el único canal libre en información que el gráfico ya muestra |
| Burbujas | **rampa multi-hue para magnitud** | Viridis va de violeta a amarillo. Para magnitud la regla es un solo tono, claro→oscuro |
| Burbujas | **una etiqueta en cada punto** | 15 nombres en `textposition: top center` colisionan entre sí |
| Distribución | **el tooltip como única forma de leer el valor** | El número de veces vive en un atributo `data-count`; si el tooltip no aparece, el dato no existe |

Y dos ausencias transversales: **no hay modo oscuro** y **no hay vista de tabla** equivalente para las
dos gráficas de Plotly (la pestaña de datos crudos cubre parte, pero no los agregados).

### El peso, medido

Descargado del CDN con compresión, que es lo que paga el navegador del grupo:

| Librería | Peso | ESM por CDN |
|---|---|---|
| **Plotly 2.27 completo (lo que se carga hoy)** | **1063 KB** | — |
| Plotly basic (solo scatter y bar) | 326 KB | — |
| ECharts 5 | 327 KB | sí |
| ApexCharts | 233 KB | sí |
| Chart.js 4 | **68 KB** | sí |
| Observable Plot | 67 KB | sí |
| uPlot | 21 KB | sí |
| SVG propio + CSS | 0 KB | — |

**Se está pagando 1 MB por tres gráficos.** Chart.js hace lo mismo con 68 KB: quince veces menos.

## Opciones

**A. Quedarse en Plotly y arreglar solo la forma.**
*Pro:* cero riesgo, cero aprendizaje, el diff es pequeño y todo el valor está en la forma.
*Contra:* sigue pesando 1 MB (o 326 KB con el bundle basic); el control de estilo es limitado y las
animaciones de Plotly son las suyas, no las que se diseñen.

**B. Chart.js 4.**
*Pro:* 68 KB, animaciones y transiciones nativas suaves, temas claro/oscuro por configuración, ESM por
CDN sin build. *Contra:* dibuja en `canvas`, así que los marks no son inspeccionables por el DOM y la
accesibilidad depende de la vista de tabla.

**C. ECharts 5.**
*Pro:* el más vistoso de los tres en movimiento — animaciones de entrada y transiciones entre estados
muy pulidas, que es literalmente lo que se ha pedido; tema oscuro nativo. *Contra:* 327 KB, cinco veces
Chart.js, para un dashboard de cuatro secciones.

**D. SVG propio con CSS y Web Animations API.**
*Pro:* 0 KB de dependencia, control total del estilo, animaciones exactamente como se diseñen, marks en
el DOM (accesibles y estilables con la misma hoja de estilos que el resto). *Contra:* hay que escribir
escalas, ejes, leyendas y tooltips; son cuatro formas simples (barras, líneas, distribución, sparkline)
pero es trabajo real y sin tests de terceros detrás.

## Decisión

**Opción A, y en dos pasos: primero la forma, con Plotly; la librería después.**

1. **Primero la forma, con la librería que ya está.** Cambiar el gráfico de líneas a *emphasis*, quitar
   el color redundante de las burbujas, poner el valor visible en la distribución y fijar las escalas.
   Eso arregla los seis anti-patrones y es lo que de verdad hace legibles los gráficos. Cambiar de
   librería sin esto produce un espagueti más bonito.
2. **Después la librería**, cuando las formas estén decididas y se sepa exactamente qué hace falta. Con
   las formas de arriba —barras horizontales, líneas con emphasis, distribución, sparklines— ninguna
   necesita Plotly, y la elección entre Chart.js y SVG propio pasa a ser una cuestión de cuánto estilo
   propio se quiere.

## Consecuencias

**Se vuelve fácil:** ver el salto de legibilidad de inmediato y sin riesgo técnico — el diff toca un solo
archivo y ninguna dependencia. Y cuando llegue la decisión de librería, se tomará sabiendo exactamente
qué formas hay que dibujar, en lugar de adivinar.

**Se vuelve difícil:** nada, a corto plazo. A medio, el kilobyte sigue ahí: **1063 KB de Plotly para
cuatro formas simples**. La decisión no lo resuelve, la aplaza con los ojos abiertos.

**Disparador explícito para retomar la opción B o D:** que las formas de la tabla de abajo estén
implementadas y estables. Ese es el momento de medir cuánto cuesta cambiar de librería, y no antes.

**Lo que NO se aplaza:** el modo oscuro y las escalas fijas entran en el primer paso. La escala fija es
una petición del grupo y el modo oscuro es un requisito de accesibilidad de las guías de visualización,
no un adorno.

## Formas propuestas por vista

Independiente de la librería que se elija, y derivado del trabajo que hace cada gráfico:

| Vista | Forma actual | Forma propuesta | Motivo |
|---|---|---|---|
| Clasificación de la temporada | burbujas (media vs partidas) | **barras horizontales** ordenadas por media, un solo tono | "comparar magnitud" pide barras; en horizontal caben los nombres largos |
| Habilidad vs constancia | el mismo gráfico de burbujas | se mantiene como vista secundaria, con **un solo color** y etiquetas solo en los extremos | sigue siendo la forma correcta para dos medidas por jugador, pero sin gastar el canal de color |
| Evolución en la temporada | 22 líneas de colores | **emphasis**: el jugador elegido en color, el resto en gris fino | la pregunta real es "cómo voy yo frente al grupo", no "22 identidades a la vez" |
| Distribución de intentos | barras CSS con el valor solo en el tooltip | igual, con el **valor visible** y escala fija 1-6 | el tooltip enhances, nunca gatea el dato |
| Jugador del día, media del grupo | dentro de tarjetas de texto | **stat tiles** con sparkline | un número no es un gráfico de una barra |
| Comparación entre meses | no existe | **small multiples** con la misma escala | es la petición del grupo: escala fija para poder comparar y animar |
