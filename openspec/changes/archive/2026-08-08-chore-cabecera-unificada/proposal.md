# Proposal — chore-cabecera-unificada

> **Slice:** N/A — cambio de presentación. Las mismas vistas, las mismas rutas y los mismos datos: solo
> cambia cómo se ven. No hay comportamiento observable nuevo que especificar.

## Why

La cabecera y el cuerpo eran **dos webs distintas pegadas**, y se veía a simple vista: la cabecera usaba la
paleta antigua (`--tinta`, `--verde`), tipografía del sistema y pestañas subrayadas; el cuerpo usaba la
paleta de la liga, tipografía de píxeles y bordes gruesos.

La causa estaba a la vista en la propia hoja de estilos: **Poppins se cargaba y no se usaba en ningún
sitio**. El documento de diseño la pide como tipografía de lectura, y ese descuido era la mitad del corte
visual.

## What Changes

```
v2/index.html       la cabecera pasa a marca + navegación + selector, en una barra
v2/css/styles.css   cabecera con el lenguaje del cuerpo · ancho útil · responsive
v2/js/ui/temporada.js  la barra del cuerpo pierde la marca duplicada
```

- **Tipografía unificada**: Poppins en todo el sitio, como pedía el diseño.
- **Cabecera con el lenguaje del cuerpo**: superficie plana, borde inferior de 3px, marca en píxeles y
  cifras en monoespaciada — lo mismo que ya hacía la barra de la temporada.
- **Navegación de píldoras**, no pestañas subrayadas: es el mismo gesto que los nombres pulsables del
  marcador, así que toda la web se pulsa igual. La sección activa va en verde.
- **Pegada arriba** al hacer scroll. Es lo que la convierte en navegación de verdad en una tabla de 181
  jornadas.
- **Ancho útil de 60rem a 84rem**: con un marcador de siete columnas, 960px dejaba media pantalla vacía a
  cada lado en un portátil.
- **La marca ya no sale dos veces**: la identidad la lleva la cabecera y la barra del cuerpo se queda con
  lo que siempre fue, la tira de cifras — que ahora se reparte a lo ancho.

## Responsive

Por debajo de 780px la cabecera pasa a dos filas: identidad y temporada arriba, navegación debajo a todo el
ancho con desplazamiento lateral. **Sin menú desplegable a propósito**: cinco secciones caben deslizando, y
un desplegable escondería la navegación tras un toque extra sin ganar nada.

## Cuatro fallos corregidos, tres de ellos ajenos

- **El hover de los botones de nombre dejaba el texto casi invisible** — lo reportó el dueño. Usaba
  `var(--liga-tinta)`, que **se invierte con el tema oscuro**: texto claro sobre verde claro. Ahora usa la
  tinta fija que ya emplea `.pixel.resalte` para este mismo caso. Contraste medido: **11,09:1 en los dos
  temas**.
- **El texto se pegaba al borde en móvil**: `main { padding: 2rem 0 }` reiniciaba el lateral que ponía el
  contenedor. Es `padding-block`.
- **`.columnas` desbordaba el documento entero** en móvil: 181 barras de dificultad arrastraban el scroll
  horizontal de toda la página. Ahora se desplazan dentro de su caja.
- **`.distribucion .barra` heredaba el relleno de la barra de cabecera** —comparten nombre de clase—: siete
  barras con 1rem 1.25rem cada una desbordaban la ficha en móvil. Ya se neutralizaban fondo y borde, pero
  no el relleno.

## Verificación

Siete vistas × cinco combinaciones de ancho y tema (390 / 768 / 1440 px, claro y oscuro): **ninguna
desborda y ninguna da errores de consola**. Cabecera y contenido alineados al mismo margen en los tres
anchos. Suite completa sin regresiones.
