---
slice: admin-del-evento
status: shipped
kind: action
actor: admin del evento
trigger:
  type: ui
  surface: web
  detail: "ruta oculta /evento/admin: con el PIN, activar, seguir, liberar nombres, terminar y exportar los puntos por grupo"
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

# El admin activa el evento cuando quiere, lo sigue, lo termina y exporta los puntos por grupo

**Actor:** quien lleva el evento, desde un portátil
**Trigger:** abrir `/evento/admin`, escribir el PIN y pulsar «Activar el evento», «Terminar el evento», «Liberar» o
una exportación

## Contexto

El evento no tiene hora fija: **lo activa el admin a voluntad** (decisión del dueño), y desde ese momento todas las
palabras se pueden jugar. Mientras juegan, el admin ve cuántos han elegido nombre y, por palabra, cuántos la están
jugando, cuántos la han resuelto y cuántos la han fallado, **sin nombres ni tiempos**. Si alguien elige un nombre que
no es el suyo, el admin lo libera: el nombre vuelve a la lista y lo jugado con él se borra.

Al terminar, salen **los puntos** (decisión del dueño, medida con eventos simulados):

- En cada palabra, la **marca** es el tiempo más **30 segundos por intento**; menos es mejor. Un intento de más se
  compensa siendo 30 segundos más rápido. Los 30 s se cambian en la base de datos sin tocar código.
- Quien resuelve una palabra se lleva **1 punto más uno por cada resolvedor con peor marca**; la misma marca, los
  mismos puntos. Quien la falla, no la termina o no la juega, cero. Los puntos de cada participante son la suma.
- Cada grupo puntúa **la media de toda su lista**: quien no juega cuenta como cero.

Los puntos se exportan en JSON y CSV para quien lleva la cuenta de los grupos, que los recibirá en su API cuando
nos den el formato.

El PIN puede ser corto (cuatro cifras): **cada cinco fallos seguidos lo bloquean, y cada bloqueo dura el doble** (1,
2, 4… minutos, hasta una hora), también para el bueno: probar los 10.000 lleva meses. Quien sepa el id del evento
puede tener al admin bloqueado; el plan B es desbloquearlo por SQL. Ni el PIN, ni las palabras, ni la lista están en
el repositorio: se cargan por SQL en Supabase.

## Trigger técnico

Ruta `/evento/admin` de la v2, fuera de la navegación. Llama a `panel_del_evento`, `empezar_evento`,
`terminar_evento` y `liberar_nombre`, todas con el PIN. Un PIN que no vale vuelve como `{error}` y no como error de
la base de datos, para que la cuenta de fallos no se deshaga. El PIN vive solo en memoria: al recargar se vuelve a
pedir.

## Comportamiento observable

### se-entra-con-el-pin
**WHEN** se abre `/evento/admin`
**THEN** solo se ve el campo del PIN; con el PIN bueno se ve el panel del evento

### un-pin-incorrecto-no-hace-nada
**WHEN** se usa un PIN que no es el del evento para entrar, activar, terminar o liberar
**THEN** se contesta «PIN incorrecto» y no cambia nada ni se enseña nada del evento

### cinco-fallos-bloquean-el-pin-un-minuto
**WHEN** se falla el PIN cinco veces seguidas
**THEN** durante un minuto ni el PIN bueno vale y se avisa de que hay que esperar; cada cinco fallos más, el bloqueo
dura el doble, hasta una hora; un acierto pone la cuenta a cero

### se-activa-con-el-pin
**WHEN** el admin pulsa «Activar el evento» y lo confirma
**THEN** el evento queda activo con la hora del servidor y los móviles pasan a pedir el nombre; activarlo otra vez no
lo mueve

### los-contadores-no-tienen-nombres
**WHEN** el evento está activo
**THEN** el panel enseña cuántos han elegido nombre de cuántos hay en la lista y, por palabra, cuántos la juegan, la
han resuelto y la han fallado, sin nombres, tiempos, puntos ni soluciones

### se-libera-un-nombre
**WHEN** el admin pulsa «Liberar» junto a un nombre elegido y lo confirma
**THEN** el nombre vuelve a estar libre, se borra lo que se jugó con él y el móvil que lo tenía vuelve a pedir el
nombre en cuanto habla con el servidor; con el evento terminado no se libera ninguno, porque cambiaría los puntos

### se-termina-con-el-pin
**WHEN** el admin pulsa «Terminar el evento» y lo confirma
**THEN** el evento termina con la hora del servidor; sin activar no se puede terminar, y terminarlo otra vez no lo
mueve

### cada-palabra-puntua-por-tiempo-e-intentos
**WHEN** se calculan los puntos de una palabra
**THEN** su marca es el tiempo más 30 s por intento, quien la resolvió se lleva 1 punto más uno por cada resolvedor
con peor marca, quien no la resolvió (fallada o a medias) se lleva 0, y los puntos de cada participante suman los de
sus palabras

### el-empate-comparte-puntos
**WHEN** dos participantes tienen la misma marca en una palabra, o los mismos puntos en total
**THEN** se llevan los mismos puntos y comparten puesto (1, 1, 3)

### los-segundos-por-intento-se-cambian-sin-codigo
**WHEN** se cambia en la base de datos lo que vale un intento
**THEN** los puntos se recalculan con ese valor, sin desplegar nada

### la-puntuacion-del-grupo-es-la-media-de-su-lista
**WHEN** se calculan los puntos de un grupo
**THEN** son la suma de los puntos de su lista dividida entre todos sus miembros, hayan jugado o no (el puesto sale
de la media sin redondear), y el panel enseña también el total, cuántos son y cuántos jugaron

### los-puntos-solo-se-ven-al-terminar
**WHEN** el evento ha terminado
**THEN** el panel enseña el ranking de grupos, el de participantes con cada palabra (intentos, tiempo y puntos) y las
soluciones; antes de terminar no los entrega

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
- Una pantalla de proyector con el ranking: el admin la puede proyectar.

## Dependencias

- [[palabras-del-evento]] es lo que juegan los participantes.
