---
slice: resultados-del-evento
status: shipped
kind: action
actor: presentador del evento
trigger:
  type: ui
  surface: web
  detail: "ruta /evento/resultados: revelar los premios F1 del último puesto premiado al primero, con teclado y botones"
events:
  emits: []
  consumes: []
specs: [dashboard, ranking]
tests_root: tests/slices/resultados-del-evento/
blocked: null
---

# Los premios individuales se revelan y suman al barrio

## Contexto

El presentador muestra los resultados en una pantalla compartida. Los equipos empiezan con cero puntos visibles y cada avance anuncia quién consigue el siguiente premio F1 y a qué equipo se suma. Se usa el tablero terminado del evento, nunca resultados de ensayo incluidos en la web.

## Trigger técnico

Abrir `/2/evento/resultados` (admite `?evento=` como las otras pantallas del evento). API de solo lectura: `tablero_del_evento`. Avanzar con botón, espacio, flecha derecha o PageDown; volver con botón, flecha izquierda o PageUp; reiniciar y pantalla completa con botones.

## Comportamiento observable

### ruta-independiente
**WHEN** se abre la ruta de resultados
**THEN** aparece una presentación independiente, fuera de la navegación de estadísticas.

### espera-al-cierre
**WHEN** el evento todavía no termina
**THEN** solo aparece una espera, sin puntos ni premiados; se consulta de nuevo hasta que termine.

### reintenta-la-lectura
**WHEN** falla la lectura del tablero
**THEN** aparece un aviso y se puede reintentar sin escribir datos.

### comienza-en-cero
**WHEN** se abre un evento terminado
**THEN** aparecen todos sus grupos con cero puntos, sin anunciar todavía ningún premiado.

### reparte-en-orden-inverso
**WHEN** se avanza un premio
**THEN** se anuncia el siguiente puesto individual desde el último premiado hasta el primero y se suman únicamente sus puntos F1 a sus grupos.

### conserva-los-empates
**WHEN** varias personas comparten un puesto premiado
**THEN** se revelan juntas con los puntos que devuelve la API; los grupos empatados comparten puesto.

### retrocede-y-reinicia
**WHEN** se vuelve atrás o se reinicia
**THEN** se retiran los premios posteriores y avanzar de nuevo no duplica puntos ni supera los límites.

### anima-el-podio
**WHEN** se avanza hacia el tercero, segundo o primer puesto
**THEN** parpadean los puntos; el primero añade fuegos artificiales; volver atrás o reiniciar retira el efecto, y la preferencia de movimiento reducido lo desactiva.

### presenta-sin-desbordes
**WHEN** el presentador usa los controles o el teclado en pantalla de 1440 por 900
**THEN** puede completar y retroceder la presentación con los diez grupos visibles, y la vista móvil no desborda horizontalmente.

### sin-puntos-no-inventa-premios
**WHEN** el evento termina sin premios F1
**THEN** se indica que no hay puntos para repartir y avanzar permanece desactivado.

## Estado después

Solo cambia el estado de presentación del navegador. Nunca se escribe en Supabase, se modifican resultados ni se publican mensajes. Recargar vuelve al inicio. El título es «Resultados de wordle del barrio» y el encabezado «Se suman al barrio los siguientes puntos:».
