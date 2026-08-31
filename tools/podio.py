"""El podio del mes que cierra: a quién se felicita y a quién se le desea suerte.

Slice: `podio-de-cierre-de-mes` (openspec/slices/publicacion/podio-de-cierre-de-mes.md).

**Qué mes se celebra sale de los datos, no del reloj** (§10). La temporada en curso es la del último resultado
de la tabla, y la que se celebra es la inmediatamente anterior. Si el mes nuevo todavía no tiene resultados
—a primera hora del día 1 puede no haberlos— no se celebra nada y se vuelve a intentar al día siguiente: el
cron corre del 1 al 7 justo para eso.

**No se recalcula nada.** El podio sale de `standings.clasificacion` y las medallas de `badges`, los mismos
que publica la web ([ADR 0008](../openspec/decisions/0008-donde-vive-el-calculo.md)).
"""

from __future__ import annotations

from badges import ORDEN_NIVEL, POR_CLAVE, medallas_de_temporada
from seasons import TEMPORADA_CERO, etiqueta, temporada_de
from standings import clasificacion

#: Cuántos suben al podio.
DEL_PODIO = 3


def temporada_que_cierra(resultados: list[dict]) -> str | None:
    """La temporada cerrada que toca celebrar, o `None` si no hay ninguna.

    Es la anterior a la del último resultado. **La temporada 0 no se celebra**: no cerró un mes, es el bloque
    histórico anterior a que existieran las temporadas.

    Devuelve `None` cuando el mes nuevo aún no tiene resultados, porque entonces la «anterior» sería la de
    hace dos meses y se felicitaría a quien ganó algo que ya se celebró.
    """
    if not resultados:
        return None
    meses = sorted({temporada_de(fila["date"]) for fila in resultados} - {TEMPORADA_CERO})
    if len(meses) < 2:
        return None
    en_curso, cerrada = meses[-1], meses[-2]
    # El mes en curso tiene que ser **consecutivo** al cerrado: si hay un salto, es que el mes nuevo todavía
    # no ha empezado a jugarse y lo que se está mirando es un cierre viejo.
    if _siguiente(cerrada) != en_curso:
        return None
    return cerrada


def _siguiente(temporada: str) -> str:
    año, mes = (int(parte) for parte in temporada.split("-"))
    return f"{año + 1}-01" if mes == 12 else f"{año}-{mes + 1:02d}"


def podio_de(resultados: list[dict], temporada: str) -> list[dict]:
    """Los tres primeros de una temporada, **con los empates enteros**.

    Se corta por puesto y no por número de filas: dos personas empatadas en el tercero suben las dos, igual
    que en el marcador diario. Cortar por filas partiría un empate por la mitad.
    """
    clasificados = [fila for fila in clasificacion(resultados, temporada) if fila["clasificado"]]
    return [fila for fila in clasificados if fila["posicion"] and fila["posicion"] <= DEL_PODIO]


def campeones(podio: list[dict]) -> list[str]:
    """Quién ganó el mes. Más de uno si hubo empate en el primer puesto."""
    if not podio:
        return []
    primero = podio[0]["posicion"]
    return [fila["nombre"] for fila in podio if fila["posicion"] == primero]


def medallas_del_campeon(resultados: list[dict], temporada: str, nombre: str) -> list[str]:
    """Las medallas que el campeón ganó **en esa temporada**, de la más difícil a la más común."""
    claves = medallas_de_temporada(resultados, temporada).get(nombre, [])
    return sorted(claves, key=lambda clave: (ORDEN_NIVEL[POR_CLAVE[clave].nivel], clave))


def texto(resultados: list[dict], temporada: str, jornada: int) -> str:
    """El mensaje del cierre de mes. Cadena vacía si no hay podio que enseñar.

    `jornada` solo elige la variante de las frases (§10: sin azar), no entra en el cálculo.
    """
    from refranero import NUEVA_TEMPORADA, PODIO_CAMPEON
    from resumen import _cifra
    from voz import _del_ciclo, con_nombre

    tabla = podio_de(resultados, temporada)
    if not tabla:
        return ""

    lineas = [f"🏆 *{etiqueta(temporada)} — así queda el podio*", ""]
    medalla = {1: "🥇", 2: "🥈", 3: "🥉"}
    anterior = None
    for fila in tabla:
        marca = medalla.get(fila["posicion"], "  ") if fila["posicion"] != anterior else "  ·"
        anterior = fila["posicion"]
        # La coma decimal se pone **solo en el número**. Aplicando `replace(".", ",")` a la línea entera,
        # «Andrés R.» salía como «Andrés R,»: varios nombres del grupo acaban en punto. Se reutiliza `_cifra`
        # del compositor en lugar de repetir el formateo, que es donde se cometió el fallo.
        lineas.append(f"{marca} {fila['nombre']} — {_cifra(fila['media_temporada'])}")

    quienes = campeones(tabla)
    if quienes:
        nombres = quienes[0] if len(quienes) == 1 else " y ".join(quienes)
        lineas += ["", con_nombre(_del_ciclo(PODIO_CAMPEON, jornada), nombres)]
        insignias = medallas_del_campeon(resultados, temporada, quienes[0]) if len(quienes) == 1 else []
        if insignias:
            lucidas = " ".join(POR_CLAVE[clave].emoji for clave in insignias)
            lineas.append(f"Se lleva además {lucidas} de la temporada.")

    lineas += ["", _del_ciclo(NUEVA_TEMPORADA, jornada)]
    return "\n".join(lineas)
