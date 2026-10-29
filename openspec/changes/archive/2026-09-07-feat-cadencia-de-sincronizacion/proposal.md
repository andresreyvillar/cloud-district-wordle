# La cadencia deja de ser una esperanza y pasa a ser un requisito

## Por qué

Cuatro intentos de arreglar el cron horario, y ninguno funcionó:

| Intento | Resultado |
|---|---|
| Mover el cron fuera del minuto en punto (lo que GitHub recomienda) | **empeoró**: de 21-23 diarias a 2-6. Revertido |
| Cron del Worker de Cloudflare | **cero disparos** en cuatro días. Descartado escuchando sus logs: 23 invocaciones `fetch`, 0 de cron |
| cron-job.org | **cero disparos**. Sin diagnóstico: su historial vive en su panel |
| Latido de 5,5 h por disparo | funciona, pero necesita que alguien lo arranque y GitHub llegó a callar 5,9 h |

Y la búsqueda no aporta ningún truco: lo único que la documentación y los artículos recomiendan es un
disparador externo, que es justo lo que ya falló dos veces.

## El cambio que sí resuelve el problema

Lo que cambió no es el mecanismo, es **el requisito**. Antes se perseguía una ejecución puntual cada hora, que
GitHub no puede dar. Ahora se pide una cadencia, con dos números que el dueño fijó:

```
al menos 12 ejecuciones al día
ningún silencio de más de 2 horas
```

Eso es alcanzable sin puntualidad, y sobre todo **es auditable**: `tools/cadencia.py` lo evalúa contra el
histórico real, así que dejamos de discutir impresiones.

## Cómo se persigue: dos piezas que se complementan

**Tres ventanas por hora** (72 al día, contra 24). No para ser puntual, sino para que baje la probabilidad de
un silencio largo.

**El latido de 5,5 h**, que ya estaba: cada ejecución sincroniza cada 55 minutos durante casi seis horas.

**Y el sistema se adapta solo**, que es lo que lo hace robusto sin ser complicado:

- planificador sano → cada ventana cancela el latido y sincroniza; la cadencia la dan las ventanas y el bucle
  nunca pasa de su primera vuelta;
- planificador callado → el latido vivo sigue sincronizando y cubre el silencio.

Ninguna pieza sobra: las ventanas dan frecuencia, el latido da continuidad.

## De dónde salió el punto de partida

Auditado el histórico de 15 días con el criterio nuevo:

```
119 ejecuciones en 15 días · hueco máximo 15,7 h · 64 huecos excesivos · 12 días por debajo
CUMPLE: False
```

Ese es el suelo desde el que se mide la mejora.

## Dos huecos del criterio que sus propios tests destaparon

**Un silencio en el borde era invisible.** Midiendo solo *entre* ejecuciones, doce agrupadas en dos horas no
tenían ningún hueco grande y dejaban veintidós de nada. Ahora cuentan también el tramo desde el comienzo del
día hasta la primera y el que va desde la última hasta el instante de referencia.

**Y sin datos se decía que la cadencia se cumplía.** Un conjunto vacío no tiene huecos excesivos ni días
flojos, así que pasaba. Ahora la ausencia de datos no es un aprobado.

El instante de referencia **entra por parámetro** (§10) y no se lee del reloj: sin él el silencio de la cola no
se puede juzgar, porque no se distingue de un día que todavía no ha terminado. Y el día de ese instante no se
juzga por su recuento, porque exigirle doce ejecuciones a media mañana suspendería siempre al día de hoy.

## Qué no hace

- **No garantiza la cadencia**: la persigue y la mide. Si GitHub calla más de 5,5 h, sigue habiendo hueco.
- No dispara nada: `cadencia.py` es el criterio, no un reloj.
- No añade dependencias ni credenciales.
