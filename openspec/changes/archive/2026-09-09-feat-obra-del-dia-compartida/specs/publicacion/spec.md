# publicacion — delta

## MODIFIED Requirements

### Requirement: La obra del día se comparte cuando hay empate

El mérito de un dibujo lo deciden la rareza de su categoría en la temporada, la simetría y los intentos. **Gana
todo el que empate en los tres**, y el mensaje los nombra a todos.

El nombre ordena la lista para que el resultado no dependa del orden en que llegaron los datos, pero no decide
quién gana: usándolo como último criterio, un cuarto de los premios se repartía por orden alfabético —medido,
52 de 204 jornadas con obra tienen empate—.

El comentario concuerda con cuántos lo comparten, con registros propios en plural.

#### Scenario: la obra del día se comparte en caso de empate
- **WHEN** varios dibujos empatan en categoría, simetría e intentos
- **THEN** el premio es de todos y se nombran todos
- **AND** la lista va ordenada por nombre, pero el nombre no decide
- **AND** el comentario va en plural

#### Scenario: con un solo ganador no cambia nada
- **WHEN** un dibujo gana sin empate
- **THEN** se nombra solo a esa persona, con el registro en singular
