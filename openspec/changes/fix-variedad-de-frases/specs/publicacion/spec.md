# publicacion — delta

## MODIFIED Requirements

### Requirement: El meme del día no repite la misma frase

Cada forma de jornada tiene **varias** plantillas, y la que sale la elige el número de jornada. Con una sola
plantilla por forma el catch-all `dia-de-dos-mundos` era el 83% de los memes publicados en 199 jornadas, y en
un mes real salió cuatro veces en diez jornadas.

Toda forma declarada tiene su condición implementada: escribir plantillas sin condición daba la falsa
impresión de variedad y era texto que nunca se ejecutaba.

#### Scenario: la misma forma no publica siempre la misma frase
- **WHEN** la misma forma de jornada se repite en jornadas distintas
- **THEN** el texto rota entre las variantes de esa forma

#### Scenario: no se afirma que nadie dibujó cuando no hay cuadrículas
- **WHEN** no se guardó ningún patrón de la jornada
- **THEN** no se dice que no hubo figuras, porque no saberlo no es lo mismo que no haberlas

### Requirement: La sospecha no repite el molde

Las frases de sospecha no comparten todas la misma forma: unas citan la nota y otras la insinúan, y no todas
llevan el mismo emoji. Con 🤨 en las 24 frases y la nota en 22 de 24, veinticuatro textos distintos se leían
como un solo chiste repetido.

#### Scenario: la sospecha no repite el molde
- **WHEN** la sospecha se comenta en varias jornadas
- **THEN** una parte de las frases sale sin el emoji y sin citar la nota
