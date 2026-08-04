# Lecciones → Reglas (bucle error→regla)

> **Principio (§11 slice-system.md):** la lección NO es el artefacto — **la regla codificada lo es**.
> Todo fallo de proceso (gate en rojo con causa raíz, error del agente, hallazgo humano) produce una
> regla permanente en el punto ejecutable más fuerte posible, en esta cascada:
>
> **1. gate/CI** (mecánico) > **2. protocolo** (slice-system) > **3. skill** (fase) > **4. CLAUDE.md** (agente)
>
> Una lección con `estado: pendiente` es DEUDA — `/slice-audit` la reporta. Se registra con `/leccion`.

## Formato de entrada

```markdown
### AAAA-MM-DD — <síntoma en una frase>
- **Qué pasó:** ...
- **Causa raíz:** ...
- **Regla:** ...
- **Codificada en:** <archivo/gate/regla concreta> · **estado:** codificada | pendiente
```

---

### 2026-08-04 — Una migración de identidad se dio por hecha sin verificarla contra los datos
- **Qué pasó:** el commit que cambiaba la identidad de jugador a `slack_user_id` dejó el código con
  la apariencia de estar migrado (diccionario de IDs, `on_conflict` por ID), pero el extractor seguía
  emitiendo nombres mostrados. Resultado: 1312 de 1530 filas guardan un nombre en la columna de ID,
  el diccionario de identidades quedó inerte y hay jugadores duplicados por renombre en Slack.
- **Causa raíz:** el cambio se validó leyendo el código, no consultando el estado de los datos que
  produce. Nada obligaba a demostrar el comportamiento observable end-to-end.
- **Regla:** un cambio de comportamiento se demuestra con un test de escenario que observe el efecto
  (la fila resultante), no con la lectura del código que lo intenta. Y antes de tocar identidad,
  ranking o deduplicación, se comprueba el estado real de la columna en Supabase.
- **Codificada en:** `openspec/slice-system.md` §6 Fase 2 (TDD rojo obligatorio antes de implementar)
  y Gate 4c (mutación: un test que no cae al mutar el código no protege nada) ·
  **estado:** codificada

### 2026-08-04 — El método no se aplicaba porque no existía
- **Qué pasó:** el proyecto creció a base de commits directos a `main` sin especificación ni tests;
  las decisiones (ancla de fechas, umbrales del ranking, unificación de nombres) viven solo en el
  código y en scripts one-shot ya ejecutados.
- **Causa raíz:** no había método ni artefactos donde registrar el comportamiento esperado.
- **Regla:** todo comportamiento observable nuevo pasa por slice + change pack + TDD antes de
  implementarse; los cambios sin comportamiento observable van como change pack `Slice: N/A`.
- **Codificada en:** `openspec/slice-system.md` (constitución completa), `.claude/skills/*` y
  `CLAUDE.md` · **estado:** codificada

### 2026-08-04 — El bytecode cacheado falseó el resultado de una prueba de mutación
- **Qué pasó:** durante el Gate 4c del pack de adopción, tras restaurar el segundo mutante
  (`DOCSTRING_LOOKAHEAD = 0` → `3`) los tests seguían en rojo con el archivo ya correcto. El
  diagnóstico mostró que el `.pyc` del mutante y el `.py` restaurado tenían **el mismo tamaño y el
  mismo mtime al segundo** (1785840201), así que Python reutilizó el bytecode del mutante.
- **Causa raíz:** la invalidación de bytecode de CPython compara mtime con resolución de segundo.
  Mutar y restaurar dentro del mismo segundo, cambiando un solo carácter, cae justo en el hueco.
  Podía haber fallado en la dirección contraria y peor: un mutante ejecutándose como código sano
  habría dado el gate por bueno.
- **Regla:** todo comando de test del protocolo se ejecuta con `python3 -B` (no escribe bytecode).
  Si ya hay `__pycache__` sospechoso, purgarlo antes de creerse un veredicto.
- **Codificada en:** `openspec/slice-system.md` §6 Fase 4.1 y Gate 4c · `.claude/skills/slice-implement/SKILL.md`
  (paso 5.c y "trampas del procedimiento") · `CLAUDE.md` (Commands) · `README.md` ·
  **estado:** codificada

### 2026-08-04 — Un `git restore` se llevó por delante un arreglo hecho durante el gate
- **Qué pasó:** al reforzar `tools/wslice/gates.py` en medio del Gate 4c, el arreglo se hizo después
  del `git add -A` inicial. El `git restore` de la mutación siguiente restauró el index — que no
  tenía el arreglo — y lo borró sin aviso.
- **Causa raíz:** el procedimiento describe el index como red de seguridad para deshacer mutaciones,
  pero no dice que hay que actualizarlo cuando aparece un cambio legítimo a mitad del gate.
- **Regla:** durante el Gate 4c, todo arreglo real (test reforzado o código corregido) se stagea
  inmediatamente antes de aplicar la siguiente mutación.
- **Codificada en:** `openspec/slice-system.md` §6 Gate 4c (viñeta "el index es la única red") +
  `.claude/skills/slice-implement/SKILL.md` ("trampas del procedimiento") · **estado:** codificada

### 2026-08-04 — El gate `federated-untouched` no veía una capability nueva completa
- **Qué pasó:** el mutante que quitaba el filtro `.md` del gate sobrevivió: ningún test lo cubría. Al
  escribir los tests que faltaban, uno de ellos falló contra el código sano y destapó un agujero real
  heredado del port: `git status --porcelain` colapsa un directorio enteramente sin trackear en una
  sola línea (`?? openspec/`), así que crear `openspec/specs/<nueva>/spec.md` en una capability nueva
  esquivaba el gate por completo.
- **Causa raíz:** el gate se portó de `slspec` literalmente, incluida esa suposición sobre la salida
  de git, y no había test que la ejercitase porque depende del repo real y no de un fixture.
- **Regla:** el gate usa `git status --porcelain --untracked-files=all`. Y ningún gate se considera
  cubierto sin al menos un test que monte el estado del que depende (aquí: un repo git temporal).
- **Codificada en:** `tools/wslice/gates.py` (`--untracked-files=all` + comentario del por qué) y
  `tests/harness/test_gates.py` (5 tests nuevos: pass, fail, staged, no-markdown, sin-repo) ·
  **estado:** codificada — *el mismo agujero existe en `slspec` de pga-cms; conviene avisar allí*

### 2026-08-04 — El gate de `test-commands` se satisface con una expresión regular
- **Qué pasó:** al portar el harness se replicó el gate que busca comandos de test en `tasks.md`
  mediante regex. Que pase no demuestra que los comandos existan, sean correctos ni se ejecuten.
- **Causa raíz:** el gate mide la presencia de una cadena, no la ejecución.
- **Regla:** el `ok` de `verify gates` no sustituye a la ejecución real de la suite; los Validation
  Gates de cada proposal listan los comandos que hay que ejecutar y el reporte de la Fase 4 debe
  incluir su salida.
- **Codificada en:** `openspec/slice-system.md` §7 (comandos deterministas) + nota de honestidad en
  el proposal del pack de adopción · **estado:** pendiente — *destino: probe en `tools/wslice` que
  ejecute los comandos declarados en lugar de buscarlos*
