---
slice: pantalla-del-evento
status: shipped
kind: action
actor: presentador del evento
trigger:
  type: ui
  surface: web
  detail: "ruta oculta /evento/pantalla: empezar y terminar el evento con un PIN y seguirlo en el proyector"
events:
  emits: []
  consumes: []
specs:
  - dashboard
  - resultados
  - ranking
tests_root: tests/slices/pantalla-del-evento/
blocked: null
---

# El presentador empieza el evento, lo sigue en el proyector y lo termina con el ranking

**Actor:** quien presenta el evento, con la pantalla en el proyector
**Trigger:** abrir `/evento/pantalla`, escribir el PIN y pulsar «Empezar el evento» o «Terminar el evento»

## Contexto

Las frases se liberan de una en una: al empezar el evento sale la primera, y cada **intervalo** sale la
siguiente. El intervalo se configura en la base de datos —10 minutos para las pruebas, 30 el día del evento— sin
tocar código. Los eventos se retrasan, así que el reloj no arranca a una hora fija: lo arranca el presentador.
Una frase liberada se juega sin tiempo máximo hasta que **el presentador termina el evento**, y entonces se
publican el ranking y las soluciones.

La pantalla del proyector da vida al evento sin filtrar nada: cuánto falta para la siguiente frase y, por cada
frase liberada, cuántos la están jugando, cuántos la han resuelto y cuántos se han quedado sin palabras, **sin
nombres ni tiempos**. La posición no se ve hasta el final (decisión del dueño).

**El ranking ordena por frases resueltas y, a igualdad, por menos tiempo total** (decisión del dueño). El tiempo
total suma las partidas terminadas, resueltas o perdidas; una partida a medias al terminar el evento no cuenta.
Desaparecen los puntos: el ranking enseña frases resueltas y tiempo.

## Trigger técnico

Ruta `/evento/pantalla` de la v2, fuera de la navegación. El PIN se comprueba en el servidor (`empezar_evento`,
`terminar_evento`) contra su huella guardada; el PIN no está en el repositorio ni viaja a la web salvo cuando lo
escribe el presentador. La pantalla lee `estado_del_evento` cada pocos segundos y `ranking_del_evento` al terminar.

## Comportamiento observable

### se-empieza-con-el-pin
**WHEN** el presentador escribe el PIN correcto y pulsa Empezar el evento
**THEN** la primera frase se libera en ese momento, con la hora del servidor

### un-pin-incorrecto-no-hace-nada
**WHEN** el presentador escribe un PIN incorrecto para empezar o para terminar
**THEN** se le dice que no es correcto y el evento sigue como estaba

### empezar-otra-vez-no-reinicia
**WHEN** se pulsa Empezar el evento con el evento ya empezado
**THEN** las liberaciones no se mueven: la hora de inicio sigue siendo la primera

### las-frases-se-liberan-cada-intervalo
**WHEN** el evento empieza con un intervalo de N minutos
**THEN** la frase k se libera a los (k−1)·N minutos del inicio y sigue jugable hasta que termina el evento

### el-intervalo-se-cambia-sin-codigo
**WHEN** el dueño cambia el intervalo del evento en la base de datos antes de empezarlo
**THEN** las frases se liberan con el nuevo intervalo sin desplegar nada; con el evento ya empezado, el cambio se
rechaza

### la-pantalla-pide-la-contrasena
**WHEN** el evento tiene contraseña de acceso y se abre el proyector
**THEN** solo se ve el campo para escribirla; con la buena, la pantalla enseña el evento, y sin ella el servidor no
entrega ni el estado ni el ranking

### antes-de-empezar-se-ve-la-espera
**WHEN** el evento no ha empezado
**THEN** la pantalla dice que está a punto de empezar, cuántos participantes hay apuntados y la dirección para
entrar

### la-cuenta-atras-a-la-siguiente-frase
**WHEN** el evento está en curso y queda alguna frase por liberar
**THEN** la pantalla enseña cuántas frases van liberadas de cuántas y cuánto falta para la siguiente, contado con la
hora del servidor

### los-contadores-no-tienen-nombres
**WHEN** el evento está en curso
**THEN** la pantalla enseña, por cada frase liberada, cuántos la están jugando, cuántos la han resuelto y cuántos
se han quedado sin palabras, sin ningún nombre ni tiempo

### se-termina-con-el-pin
**WHEN** todas las frases están liberadas y el presentador escribe el PIN y pulsa Terminar el evento
**THEN** el evento termina con la hora del servidor: no se admiten más palabras y se publican el ranking y las
soluciones

### al-terminar-se-ven-las-soluciones
**WHEN** el evento termina
**THEN** la pantalla enseña la frase entera de cada ronda, y el servidor la entrega a cualquiera que pregunte por el
evento; antes no la entrega

### el-ranking-ordena-por-frases-y-tiempo
**WHEN** se calcula el ranking final
**THEN** va delante quien resolvió más frases y, con las mismas, quien tardó menos en total

### el-tiempo-cuenta-al-terminar-la-partida
**WHEN** se suma el tiempo de un participante
**THEN** cuentan las partidas resueltas y las perdidas tras cinco palabras; una partida a medias no suma tiempo ni
frase, y quien no terminó ninguna no sale en el ranking

### el-empate-comparte-puesto
**WHEN** dos participantes resuelven las mismas frases con el mismo tiempo total en milisegundos
**THEN** comparten puesto, y el siguiente salta el puesto (1, 1, 3)

### el-ranking-sale-al-terminar-el-evento
**WHEN** el presentador termina el evento
**THEN** la pantalla enseña el ranking final con el podio, las frases resueltas y el tiempo de cada participante;
antes de ese momento el servidor no lo entrega

### el-pin-no-esta-en-el-repositorio
**WHEN** se busca el PIN o una frase real en el repositorio
**THEN** no están: las frases y la huella del PIN se cargan por SQL en la base de datos, y en el repositorio solo
están las frases y el PIN del evento de prueba

### los-nombres-se-escapan-en-la-pantalla
**WHEN** el nombre de un participante contiene HTML
**THEN** el ranking lo pinta como texto, no como marcado

## Estado después

`event_editions.empieza_en` y `event_editions.terminado_en` quedan fijados por `empezar_evento` y
`terminar_evento`. La pantalla no escribe nada más.

## Edge cases

- **Recargar el proyector**: la pantalla se reconstruye del estado del servidor; no lleva reloj propio.
- **Reiniciar un ensayo**: se hace desde Supabase, borrando las partidas del evento de prueba y poniendo
  `empieza_en` y `terminado_en` a nulo. No hay botón de reiniciar en la web, para que nadie lo pulse el día del
  evento.
- **Terminar antes de tiempo**: el botón de terminar sale cuando todas las frases están liberadas; el servidor solo
  exige que el evento haya empezado, para no dejar al presentador sin salida si algo se tuerce.

## Slices compañeros

- [[frase-del-evento]] — lo que juega cada participante en su móvil.
- [[clasificacion-del-juego]] — puntúa por puesto; el evento ordena por frases resueltas y tiempo.
