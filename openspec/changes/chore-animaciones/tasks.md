# Tasks — chore-animaciones

- [x] `v2/js/ui/animacion.js`: revelado con IntersectionObserver, contadores y seguimiento de scroll.
- [x] CSS: keyframes, escalonado con tope, barra de progreso dirigida por scroll, micro-interacciones.
- [x] Enganchado **en un solo sitio**, envolviendo el despacho de vistas: ninguna vista puede olvidarse.
- [x] `startViewTransition` al navegar, con detección de soporte y de movimiento reducido.
- [x] Quitada una regla `@view-transition` que no hacía nada: es para navegaciones entre documentos y esta
      web cambia de vista con `pushState`.
- [x] **10 tests**, sobre lo que una animación sí puede romper y no se ve mirando dos segundos:
      que una cifra acabe distinta, y que el movimiento siga vivo para quien pidió que no.
- [x] Mutante comprobado: sin la desconexión del observador anterior, el test cae.
- [x] Medido el coste: **0 fotogramas de más de 50 ms** en un recorrido completo de la temporada 0.
- [x] Verificado con `prefers-reduced-motion`: 0 elementos ocultos, 0 clases de revelado, cifras intactas.
- [x] Seis vistas recorridas de arriba abajo: nada se queda invisible.

## Comandos

```bash
node --test tests/v2/animacion.test.js
node --test tests/
python3 tools/local_stack.py       # y mirar /2/ bajando despacio
```
