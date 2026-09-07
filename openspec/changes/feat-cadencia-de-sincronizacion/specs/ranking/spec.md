# ranking — delta

## ADDED Requirements

### Requirement: La cadencia de sincronización es un requisito medible

Que los datos estén frescos deja de depender de que un planificador ajeno sea puntual y pasa a expresarse con
dos números: **ejecuciones mínimas por día** y **silencio máximo entre ejecuciones**. No se pide puntualidad.

El criterio se evalúa sobre el histórico de ejecuciones y el veredicto no depende de cuándo se mire: el
instante de referencia entra por parámetro y nunca se lee del reloj.

Los silencios se cuentan también en los bordes —desde el comienzo del día hasta la primera ejecución y desde
la última hasta el instante de referencia—, porque midiendo solo entre ejecuciones un grupo apretado seguido
de un día entero de nada pasaba por bueno.

El día del instante de referencia no se juzga por su recuento: se presume en curso, y exigirle el mínimo a
media mañana suspendería siempre al día de hoy. Sus silencios sí cuentan.

Sin ejecuciones no se afirma que la cadencia se cumpla: la ausencia de datos no es un aprobado.

#### Scenario: la cadencia es un requisito medible
- **WHEN** se juzga la sincronización
- **THEN** el veredicto sale de los dos números y del histórico, no de una impresión

#### Scenario: un día flojo se nombra
- **WHEN** un día completo no alcanza el mínimo
- **THEN** se dice cuál

#### Scenario: el silencio se mide también en los bordes
- **WHEN** las ejecuciones se agrupan y dejan el resto del día sin ninguna
- **THEN** no se cumple, aunque el recuento diario baste

#### Scenario: sin ejecuciones no se inventa un veredicto
- **WHEN** no hay ejecuciones que juzgar
- **THEN** no se afirma que la cadencia se cumpla
