---
slice: admin-del-evento
status: shipped
kind: action
actor: admin del evento
trigger:
  type: ui
  surface: web
  detail: "ruta oculta /evento/admin: dashboard sin PIN para seguir el evento en directo, echar participantes, cambiar las palabras antes de empezar, exportar y compartir los puntos"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - resultados
  - ranking
tests_root: tests/slices/admin-del-evento/
blocked: null
---

# El admin es el dashboard del evento: lo sigue en directo, revisa las palabras antes de empezar y comparte los puntos

**Actor:** quien lleva el evento, desde un portátil o un proyector
**Trigger:** abrir `/evento/admin` y pulsar «Echar», «Guardar» junto a una palabra, una exportación o «Copiar»,
«WhatsApp» o «Email»

## Contexto

El evento **empieza y termina a su hora** (decisión del dueño): `empieza_en` y `terminado_en` se cargan de antemano
—el día del evento, de 10:00 a 16:00 de Madrid— y nadie tiene que activarlo ni terminarlo. El admin es **un dashboard
sin contraseña** (decisión del dueño, avisado de que así cualquiera con el enlace ve las palabras antes de empezar),
con el estilo del cartel del evento: fondo crema con la cuadrícula fina, título grande en minúscula, anotaciones
pequeñas en monoespaciada. Antes de empezar dice cuánto falta, **pero no enseña las palabras**: el dueño tiene el
dashboard abierto y juega sin conocerlas. Las palabras se revisan y **se cambian en su propio enlace**
(`/evento/palabras`, para Nouha) por otras del diccionario del juego hasta la hora de empezar; después quedan fijas y
no se ven en ninguna parte hasta que termina. **Mientras juegan, el admin lo sigue en directo** (decisión del dueño): cuántos han elegido
nombre; por palabra, cuántos la están jugando, cuántos la han resuelto y cuántos la han fallado; y **una fila por cada
participante que ha entrado**, con su grupo, cuántas palabras ha resuelto, el tiempo de sus palabras terminadas, en
qué palabra va con su reloj, y sus puntos y su puesto. El **ranking de participantes y el de grupos se ven en directo**
y se actualizan solos cada pocos segundos; son provisionales, porque una palabra a medias cuenta cero y los puntos de
cada palabra dependen de cuántos la resuelvan peor. El móvil de los participantes sigue sin ver puntos ni puestos, y
las soluciones solo se ven al terminar. Si alguien elige un nombre que no es el suyo, el admin lo **echa** desde su
fila: el nombre vuelve a la lista y lo jugado con él se borra.

Además de la media de la lista, los grupos tienen **un campeonato F1** (decisión del dueño): los diez primeros de la
clasificación individual suman a su grupo 25, 18, 15, 12, 10, 8, 6, 4, 2 y 1 puntos; los empatados se reparten los
puntos de los puestos que ocupan juntos. Una tabla resumen enseña cada grupo con sus puntos F1 y quién los ha sumado.

Al terminar, salen **los puntos** (decisión del dueño, medida con eventos simulados): **premian sobre todo acertar, y
después la rapidez**.

- Cada palabra acertada da **10 puntos**, y **hasta 5 más** por rapidez: el más rápido de esa palabra se lleva los 5,
  el más lento ninguno, y los demás en proporción a su puesto. Quien la falla, no la termina o no la juega, cero. Los
  puntos de cada participante son la suma. Así, quien acierta más palabras queda delante casi siempre (99 % de los
  casos en la simulación), y entre quienes aciertan las mismas decide la rapidez.
- La rapidez se mide con la **marca**: el tiempo más **30 segundos por intento**; menos es mejor. La misma marca, los
  mismos puntos, y empatar no quita extra. Los 10, los 5 y los 30 s se cambian en la base de datos sin tocar código.
- Cada grupo puntúa **la media de toda su lista**: quien no juega cuenta como cero.

Los puntos se exportan en JSON y CSV para quien lleva la cuenta de los grupos, que los recibirá en su API cuando
nos den el formato. Terminado el evento, **los resultados se comparten en texto** (decisión del dueño): el ranking de
grupos (F1 con quién los sumó, y media) y el podio de participantes, para copiarlo o mandarlo por WhatsApp o por
email.

La web ya no pide el PIN. Las funciones con PIN (activar, terminar, panel, liberar) se quedan para operar a mano. El
PIN puede ser corto (cuatro cifras): **cada cinco fallos seguidos lo bloquean, y cada bloqueo dura el doble** (1,
2, 4… minutos, hasta una hora), también para el bueno: probar los 10.000 lleva meses. Quien sepa el id del evento
puede tener al admin bloqueado; el plan B es desbloquearlo por SQL. Ni el PIN, ni las palabras, ni la lista están en
el repositorio: se cargan por SQL en Supabase.

## Trigger técnico

Ruta `/evento/admin` de la v2, fuera de la navegación. Llama sin PIN a `tablero_del_evento` (cada pocos segundos),
`echar_participante` y `cambiar_palabra`. Las funciones con PIN (`panel_del_evento`, `empezar_evento`,
`terminar_evento`, `liberar_nombre`) siguen en la base de datos para operar a mano; con un PIN que no vale contestan
`{error}` y no un error de la base de datos, para que la cuenta de fallos no se deshaga.

## Comportamiento observable

### el-panel-se-ve-sin-pin
**WHEN** se abre `/evento/admin`
**THEN** se ve el dashboard del evento sin pedir contraseña: antes de empezar, cuánto falta; durante y después, los
participantes y los rankings; las palabras, solo al terminar (antes de empezar se revisan en su propio enlace)

### el-evento-empieza-y-termina-a-su-hora
**WHEN** llega la hora de empezar o la de terminar cargadas en el evento
**THEN** el evento empieza o termina solo, sin que nadie lo active; antes de su hora los móviles solo ven la espera y
no se puede elegir nombre, aunque la hora ya esté cargada

### se-cambian-las-palabras-antes-de-empezar
**WHEN** antes de la hora de empezar, en `/evento/palabras`, quien revisa las palabras cambia una y pulsa «Guardar»
**THEN** queda cambiada si tiene cinco letras, está en el diccionario del juego y no repite otra del evento; si no,
se dice por qué; llegada la hora de empezar, ya no se puede cambiar ninguna y el enlace solo dice que ya no se ven

### los-diez-primeros-suman-f1-a-su-grupo
**WHEN** se calcula la clasificación individual
**THEN** los diez primeros con puntos suman a su grupo 25, 18, 15, 12, 10, 8, 6, 4, 2 y 1; los empatados se reparten
los puntos de los puestos que ocupan (dos primeros, 21,5 cada uno); una tabla enseña cada grupo con sus puntos F1 y
quién los ha sumado, en directo y al terminar

### el-panel-tiene-el-estilo-del-cartel
**WHEN** se abre el dashboard
**THEN** se ve con el estilo del cartel: fondo crema con cuadrícula fina, título grande en minúscula, la fecha y las
anotaciones en monoespaciada pequeña

### un-pin-incorrecto-no-hace-nada
**WHEN** a mano, se usa un PIN que no es el del evento para ver el panel, activar, terminar o liberar
**THEN** se contesta «PIN incorrecto» y no cambia nada ni se enseña nada del evento

### cinco-fallos-bloquean-el-pin-un-minuto
**WHEN** se falla el PIN cinco veces seguidas
**THEN** durante un minuto ni el PIN bueno vale y se avisa de que hay que esperar; cada cinco fallos más, el bloqueo
dura el doble, hasta una hora; un acierto pone la cuenta a cero

### se-activa-con-el-pin
**WHEN** a mano, se activa el evento con el PIN (la web ya no lo hace: empieza a su hora)
**THEN** el evento queda activo con la hora del servidor y los móviles pasan a pedir el nombre; activarlo otra vez no
lo mueve

### el-admin-sigue-a-cada-participante
**WHEN** el evento está activo
**THEN** el panel enseña cuántos han elegido nombre de cuántos hay en la lista; por palabra, cuántos la juegan, la han
resuelto y la han fallado; y una fila por cada participante que ha entrado, con su grupo, sus palabras resueltas, el
tiempo de sus palabras terminadas y en qué palabra va con su reloj, o si está entre dos palabras, ha terminado o no ha
empezado; sin soluciones

### el-ranking-se-ve-en-directo
**WHEN** el evento está activo y los participantes van terminando palabras
**THEN** el panel enseña el puesto y los puntos de cada participante que ha entrado y el ranking de grupos, con lo
terminado hasta ese momento y marcados como provisionales, y se actualiza solo cada pocos segundos

### se-libera-un-nombre
**WHEN** el admin pulsa «Echar» en la fila de un participante y lo confirma (sin PIN)
**THEN** el nombre vuelve a estar libre, se borra lo que se jugó con él y el móvil que lo tenía vuelve a pedir el
nombre en cuanto habla con el servidor; con el evento terminado no se libera ninguno, porque cambiaría los puntos

### se-termina-con-el-pin
**WHEN** a mano, se termina el evento con el PIN (la web ya no lo hace: termina a su hora)
**THEN** el evento termina con la hora del servidor; sin activar no se puede terminar, y terminarlo otra vez no lo
mueve

### cada-palabra-puntua-por-tiempo-e-intentos
**WHEN** se calculan los puntos de una palabra
**THEN** quien la resolvió se lleva 10 más un extra de hasta 5 según el puesto de su marca (el tiempo más 30 s por
intento) entre quienes la resolvieron: 5 el mejor, 0 el peor, en proporción el resto; quien no la resolvió (fallada o a
medias) se lleva 0, y los puntos de cada participante suman los de sus palabras

### acertar-pesa-mas-que-la-rapidez
**WHEN** un participante acierta una palabra más que otro
**THEN** esa palabra le da 10 puntos que el otro no tiene, más que cualquier extra por rapidez en una palabra

### el-empate-comparte-puntos
**WHEN** dos participantes tienen la misma marca en una palabra, o los mismos puntos en total
**THEN** se llevan los mismos puntos y comparten puesto (1, 1, 3)

### los-segundos-por-intento-se-cambian-sin-codigo
**WHEN** se cambian en la base de datos lo que vale un intento, los puntos por acertar o el extra por rapidez
**THEN** los puntos se recalculan con esos valores, sin desplegar nada

### la-puntuacion-del-grupo-es-la-media-de-su-lista
**WHEN** se calculan los puntos de un grupo
**THEN** son la suma de los puntos de su lista dividida entre todos sus miembros, hayan jugado o no (el puesto sale
de la media sin redondear), y el panel enseña también el total, cuántos son y cuántos jugaron

### las-soluciones-solo-se-ven-al-terminar
**WHEN** el evento ha terminado
**THEN** el panel enseña los rankings de grupos, el de participantes con cada palabra (intentos, tiempo y puntos) y las
soluciones; mientras se juega no entrega las soluciones

### se-comparten-los-resultados-en-texto
**WHEN** el evento ha terminado y el admin pulsa «Copiar», «WhatsApp» o «Email»
**THEN** obtiene un texto con el campeonato F1 de grupos (puntos y quién los sumó), el ranking de grupos por la media y
el podio de participantes con su grupo y sus puntos, listo para pegar en un mensaje; los nombres van como texto, sin
HTML

### se-exportan-los-puntos
**WHEN** el admin pulsa «Grupos (CSV)», «Participantes (CSV)» o «Todo (JSON)»
**THEN** se descarga el fichero con los puntos de cada grupo y de cada participante, con el detalle de cada palabra;
los CSV escapan comas y comillas y no dejan empezar un campo por `=`, `+`, `-` ni `@`

### los-nombres-se-escapan-en-la-pantalla
**WHEN** un nombre o un grupo lleva HTML
**THEN** se pinta como texto

### el-pin-no-esta-en-el-repositorio
**WHEN** se revisan las migraciones del repositorio
**THEN** no insertan eventos, palabras ni participantes, ni llevan la huella de ningún PIN; solo la semilla local trae
el evento de prueba

## Fuera de alcance

- Enviar los puntos a la API de quien lleva la cuenta de los grupos: el formato está por llegar.
- Una pantalla de proyector aparte: el dashboard es la que se proyecta.

## Dependencias

- [[palabras-del-evento]] es lo que juegan los participantes.
