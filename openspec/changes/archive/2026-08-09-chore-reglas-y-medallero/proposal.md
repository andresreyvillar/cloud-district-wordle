# Proposal — chore-reglas-y-medallero

> **Slice:** N/A — presentación y navegación. Los mismos datos y las mismas rutas.

## Why

Tres peticiones del dueño en la misma tanda:

1. **La pestaña de reglas se ve mal.**
2. **La marca dice «WORDLE CD»** y debería decir el nombre completo.
3. **En el medallero los nombres no llevan a la ficha**, aunque en el resto de la web sí.

## Reglas: tres problemas, todos de aprovechamiento del espacio

Medido antes de tocar: **5957 px de alto** y, en cada tarjeta, el texto limitado a 62 caracteres dentro de
un contenedor de 84 rem — o sea, **media tarjeta vacía** y los marcadores flotando a un palmo del título al
que se refieren. Veintiuna reglas en una columna, sin forma de llegar a la quinta sección salvo rodar la
rueda. Y usaba la paleta antigua cuando el resto de la web ya había pasado a la de la liga.

Ahora:

- **rejilla de hasta tres columnas** — 5957 px pasan a **4253**;
- **índice de ejes con su recuento**, para saltar; los títulos reservan el alto de la cabecera pegajosa;
- **HUD con las tres cifras** que resumen el estado: en vigor, votadas, sin decidir;
- **marcadores junto al título**, no al otro lado de la tarjeta;
- **la regla que se aplica sin estar votada se marca en morado** — es la información accionable de esta
  página, y hasta ahora se perdía entre las demás.

## Medallero: los nombres enlazan

El medallero se cuenta **por nombre**, porque así llegan los logros en la instantánea, mientras que la ficha
se direcciona por identificador de Slack. El único sitio donde conviven los dos es la clasificación, así que
de ahí se resuelve — quedándose con la temporada de mayor ordinal en la que la persona aparece, para que el
enlace lleve a una ficha con datos y no a una en la que jugó una vez.

Un nombre que no se pueda resolver se pinta **sin enlace**: mandar a una ficha inventada es peor que no
enlazar.

## Impact

- `/reglas` deja de ser un muro y se puede recorrer.
- El medallero se comporta como el resto de la web: si hay un nombre, se puede pulsar.
- La marca dice «WORDLE · LIGA · CLOUD DISTRICT», y la casa desaparece por debajo de 900 px, donde comparte
  fila con el selector de temporada.
