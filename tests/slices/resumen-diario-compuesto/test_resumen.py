"""Escenarios de `resumen-diario-compuesto` (Fase 2 — TDD rojo).

El resumen es una **función pura**: entran los resultados, la temporada y la jornada, y sale texto. Ni
reloj, ni Slack, ni navegador — por eso el mensaje que el grupo verá se puede fijar en un test.

Las cuadrículas son las mismas que verifica el slice del clasificador, y aquí se vuelven a comprobar antes
de usarse.
"""

from __future__ import annotations

import pytest

LORO = ".G.../.G..G/.GY../GGGGG"
GEOMETRICO = "..G../..G../GGGGG"
FLOR = "Y...Y/..Y../GGGGG"
#: **Asimétrico a propósito.** El anterior (`GG.GG/GGYGG/GG.GG`) era un espejo perfecto sin que nadie
#: lo hubiera notado, así que al añadirse la regla del espejo dejó de ser abstracto. Se sustituyó el
#: fixture, no la aserción.
ABSTRACTO = "GG.GG/GGYG./GG.GG/GGGGG"

HISTORICO = "2026-03-02"
HOY = 1600


def resultado(nombre, jornada, score, patron=None, fecha=HISTORICO):
    return {
        "slack_user_id": f"U_{nombre}",
        "player_name": nombre,
        "wordle_id": jornada,
        "score": score,
        "date": fecha,
        "pattern": patron,
    }


def historia(nombre, cuantas, score=4, patron=FLOR):
    """Partidas anteriores, para que la temporada tenga marcador y álbum."""
    return [resultado(nombre, 1500 + i, score, patron) for i in range(cuantas)]


def test_los_fixtures_dibujan_lo_que_dicen_dibujar():
    from figures import figura

    assert (figura(LORO), figura(GEOMETRICO), figura(FLOR), figura(ABSTRACTO)) == (
        "loro",
        "geometrico",
        "flores",
        "abstracto",
    )


# @scenarios jugador-del-dia
def test_el_jugador_del_dia_es_la_mejor_puntuacion():
    from resumen import resumen_del_dia

    filas = historia("Ana", 6) + historia("Bea", 6) + [
        resultado("Ana", HOY, 2, FLOR),
        resultado("Bea", HOY, 5, ABSTRACTO),
    ]

    texto = resumen_del_dia(filas, "0", HOY)

    # Sobre SU línea, no sobre el mensaje entero: Ana aparece también en el top y en el álbum, así que
    # `"Ana" in texto` pasaba aunque el premio se lo llevara Bea. Lo cazó un mutante.
    # Sobre SU línea, no sobre el mensaje entero: Ana aparece también en el top y en el álbum, así que
    # `"Ana" in texto` pasaba aunque el premio se lo llevara Bea. Lo cazó un mutante.
    linea = next(l for l in texto.splitlines() if "mejores" in l or "bordado" in l or "Arriba del todo" in l)
    assert "Ana" in linea and "Bea" not in linea
    assert "2" in linea, "y con la puntuación que lo gana"


# @scenarios jugador-del-dia
def test_el_empate_en_la_mejor_puntuacion_nombra_a_todos():
    """Con diez jugadores y notas de 1 a 7, el empate es lo normal. Elegir uno sería arbitrario."""
    from resumen import bloque_jugador_del_dia

    hoy = [
        resultado("Ana", HOY, 2, FLOR),
        resultado("Bea", HOY, 2, LORO),
        resultado("Cris", HOY, 5, ABSTRACTO),
    ]

    linea = bloque_jugador_del_dia(hoy)

    assert "Ana" in linea and "Bea" in linea
    # **El plural también se conjuga.** Este test comprobaba a quién se nombra y nunca cómo, así que
    # «resolvión» —pegarle una «n» a «resolvió»— pasó los gates y estuvo a punto de publicarse en el canal.
    # Lo cazó previsualizar el mensaje real, no la suite.
    assert "resolvieron en 2" in linea, f"el plural del pretérito, no una letra pegada: {linea}"
    assert "Jugadores del día" in linea, f"con dos empatados el título también va en plural: {linea}"
    assert "Cris" not in linea


# @scenarios obra-del-dia
def test_la_obra_del_dia_es_la_figura_mas_rara_de_la_temporada():
    """La rareza sale del reparto de la propia temporada, no de una tabla escrita a mano."""
    from resumen import bloque_obra_del_dia

    # En la temporada hay muchas flores y pocos geométricos: el geométrico es lo raro.
    temporada = historia("Ana", 12, patron=FLOR) + historia("Bea", 12, patron=FLOR)
    hoy = [resultado("Ana", HOY, 4, FLOR), resultado("Bea", HOY, 5, GEOMETRICO)]

    linea = bloque_obra_del_dia(temporada + hoy, "0", HOY)

    assert "Bea" in linea, "gana la categoría menos frecuente, no la mejor puntuación"
    assert "📐" in linea


# @scenarios la-simetria-gana-la-obra-del-dia
def test_la_simetria_gana_la_obra_del_dia_por_delante_de_los_intentos():
    """El caso real del día en que se decidió: dos geométricos, y el premio se lo llevaba el escaso.

    Las dos cuadrículas son de la misma categoría, así que la rareza no separa. Antes decidía «más
    intentos» y ganaba el de 4; ahora decide la simetría y gana el espejo, aunque resolviera en 3. El
    clasificador solo devuelve categorías, así que sin este desempate un espejo perfecto y una forma escasa
    son indistinguibles.
    """
    from resumen import bloque_obra_del_dia

    simetrico = "G...G/GG.GG/GGGGG"      # espejo perfecto, densidad 0,60
    escaso = "...../.G..G/GGG.G/GGGGG"   # geométrico por poca tinta, sin simetría

    temporada = historia("Ana", 12, patron=FLOR) + historia("Bea", 12, patron=FLOR)
    hoy = [resultado("Ana", HOY, 3, simetrico), resultado("Bea", HOY, 4, escaso)]

    linea = bloque_obra_del_dia(temporada + hoy, "0", HOY)

    assert "Ana" in linea, f"gana el espejo aunque tardara menos: {linea}"
    assert "Bea" not in linea


# @scenarios obra-del-dia
def test_sin_figuras_el_premio_queda_desierto():
    from resumen import bloque_obra_del_dia

    filas = historia("Ana", 6) + [resultado("Ana", HOY, 6, ABSTRACTO)]

    linea = bloque_obra_del_dia(filas, "0", HOY)

    assert "🌀" not in linea, "un abstracto no es una obra"
    assert "desiert" in linea.lower()


# @scenarios top-cinco-con-su-dibujo
def test_el_top_cinco_lleva_el_emoji_de_lo_que_cada_uno_dibujo_hoy():
    from resumen import bloque_top

    temporada = historia("Ana", 10, score=3) + historia("Bea", 10, score=5)
    hoy = [resultado("Ana", HOY, 3, LORO)]  # Bea no jugó hoy

    bloque = bloque_top(temporada + hoy, "0", HOY)

    lineas = {linea.split()[1].rstrip(".") if linea.split() else "": linea for linea in bloque.splitlines()}
    ana = next(l for l in bloque.splitlines() if "Ana" in l)
    bea = next(l for l in bloque.splitlines() if "Bea" in l)
    assert "🦜" in ana
    assert "🦜" not in bea and "🌷" not in bea, "quien no jugó hoy no lleva dibujo del día"


# @scenarios top-cinco-con-su-dibujo
def test_el_top_no_pasa_de_cinco():
    from resumen import bloque_top

    muchos = []
    for indice in range(9):
        muchos += historia(f"J{indice}", 6, score=1 + indice % 6)

    bloque = bloque_top(muchos, "0", 1505)

    # Se corta por PUESTO, no por número de filas: con empates puede haber más de cinco líneas, y lo que
    # no puede pasar es que aparezca un sexto puesto.
    puestos = [int(l.split("º")[0]) for l in bloque.splitlines()[1:] if "º" in l.split(" ")[0]]
    assert puestos and max(puestos) <= 5


# @scenarios cabeza-del-album
def test_la_cabeza_del_album_sale_con_su_tasa_y_su_tira():
    from resumen import bloque_album

    limpia = historia("Ana", 8, patron=LORO)
    sucia = historia("Bea", 8, patron=ABSTRACTO)

    bloque = bloque_album(limpia + sucia, "0")

    assert "Ana" in bloque
    # Ocho loros a 2 puntos entre ocho partidas: 2,00 puntos por partida. Antes esto era «100 %», y cambió
    # con la ponderación del 2026-08-09 (geométrico 3 · loro 2 · flor 1).
    assert "2,00 pts" in bloque, f"la puntuación ponderada no sale: {bloque}"
    assert "🦜8" in bloque, "su tira agrupada"


# @scenarios sin-jornada-no-hay-resumen
def test_sin_resultados_no_se_inventa_ninguna_seccion():
    from resumen import resumen_del_dia

    texto = resumen_del_dia([], "0", HOY)

    assert "mejores del día" not in texto.lower()
    assert "Obra del día" not in texto
    assert texto.strip() == "" or "ranking" in texto.lower()


# @scenarios sin-jornada-no-hay-resumen
def test_una_temporada_sin_album_no_imprime_la_seccion_del_album():
    """Es el estado real de agosto de 2026: 61 de 80 partidas sin cuadrícula guardada."""
    from resumen import resumen_del_dia

    filas = historia("Ana", 8, patron=None) + [resultado("Ana", HOY, 3, None)]

    texto = resumen_del_dia(filas, "0", HOY)

    assert "Álbum" not in texto
    assert "Ana" in texto, "las secciones con datos sí salen"


# @scenarios el-resumen-no-recalcula
def test_el_marcador_del_resumen_es_el_mismo_que_publica_la_web():
    """Una segunda versión de las reglas dentro del publicador diría cosas distintas que la web."""
    from resumen import bloque_top
    from standings import clasificacion

    filas = historia("Ana", 10, score=3) + historia("Bea", 10, score=5) + historia("Cris", 10, score=4)

    lider = clasificacion(filas, "0")[0]
    bloque = bloque_top(filas, "0", 1509)

    primera = next(l for l in bloque.splitlines() if l.strip().startswith("1º"))
    assert lider["nombre"] in primera


# @scenarios el-mensaje-no-crece-con-el-grupo
def test_el_mensaje_no_crece_con_el_numero_de_jugadores():
    """La propiedad que hace que quepa en Slack no es un recorte, es que está acotado por construcción.

    El primer test de esto comparaba con el límite de 3000 y pasaba con 499 caracteres: no ejercitaba nada.
    Aquí se compara **el mensaje de un grupo pequeño con el de uno seis veces mayor**, que es lo que de
    verdad podría desbordarlo.
    """
    from resumen import LIMITE_DE_SLACK, TOP, resumen_del_dia

    def grupo(cuantos):
        filas = []
        for indice in range(cuantos):
            filas += historia(f"Jugador con nombre largo {indice}", 20, score=1 + indice % 6)
        return filas + [resultado("Jugador con nombre largo 0", HOY, 2, LORO)]

    pequeno = resumen_del_dia(grupo(5), "0", HOY)
    grande = resumen_del_dia(grupo(30), "0", HOY)

    assert len(grande) < len(pequeno) * 1.5, "seis veces más gente no puede dar un mensaje mucho mayor"
    assert len(grande) <= LIMITE_DE_SLACK
    # Se cuentan las LÍNEAS del bloque del top, no los prefijos "1.": con puestos compartidos varios
    # jugadores llevan el mismo número y ese proxy dejó de medir lo que decía medir.
    def filas_del_top(texto):
        bloque = texto.split("📊 *Marcador")[1].split("\n\n")[0]
        return len(bloque.splitlines())

    assert "Marcador" in grande
    # La propiedad: el bloque del marcador NO crece con el grupo. Se comparan los dos entre sí en lugar de
    # contra un número fijo, porque con empates el recuento depende de cuántos comparten puesto y lo que
    # importa es que seis veces más gente no produzca un bloque mayor.
    assert filas_del_top(grande) == filas_del_top(pequeno)
    assert filas_del_top(grande) <= TOP + 1, "el encabezado más como mucho cinco puestos"


# @scenarios el-resumen-se-enciende-con-una-variable
def test_el_resumen_va_apagado_por_defecto():
    """Mergear a `main` cambia lo que el cron ejecuta esa tarde: el mensaje no puede cambiar solo."""
    import os

    from post_ranking import OBJETIVOS, comentario, resumen_activo

    filas = historia("Ana", 6) + [resultado("Ana", HOY, 2, LORO)]
    previo = os.environ.pop("RESUMEN_COMPUESTO", None)
    try:
        assert resumen_activo() is False
        apagado = comentario("", OBJETIVOS["v1"], filas)
        assert "mejores del día" not in apagado.lower()
        assert "ranking actualizado" in apagado, "el mensaje de siempre sigue saliendo"

        os.environ["RESUMEN_COMPUESTO"] = "1"
        assert resumen_activo() is True
        assert "2" in comentario("", OBJETIVOS["v1"], filas)
    finally:
        os.environ.pop("RESUMEN_COMPUESTO", None)
        if previo is not None:
            os.environ["RESUMEN_COMPUESTO"] = previo


# @scenarios la-pelea-por-el-primer-puesto-se-cuenta
def test_el_empate_en_cabeza_se_cuenta_como_pelea():
    """El caso real: dos personas compartiendo el primer puesto con la misma media.

    La web publicaba «le sigue a 0,00» en su titular porque tomaba el segundo elemento de la lista como el
    segundo clasificado. `posicion` ya venía en los datos y nadie la leía.
    """
    from resumen import bloque_rivalidad

    filas = historia("Ana", 8, score=3) + historia("Bea", 8, score=3) + historia("Cris", 8, score=5)

    linea = bloque_rivalidad(filas, "0", 1007)

    assert "Ana" in linea and "Bea" in linea
    assert "Cris" not in linea, "el tercero no está en la pelea"
    assert "0,00" not in linea, "un empate no es una ventaja de cero"


# @scenarios la-pelea-por-el-primer-puesto-se-cuenta
def test_una_ventaja_amplia_no_inventa_rivalidad():
    """Con alguien destacado no hay pelea que contar, y el mensaje ya tiene bastantes líneas."""
    from resumen import bloque_rivalidad

    filas = historia("Ana", 8, score=2) + historia("Bea", 8, score=6)

    assert bloque_rivalidad(filas, "0", 1007) == ""


# @scenarios la-pelea-por-el-primer-puesto-se-cuenta
def test_con_un_solo_clasificado_no_hay_pelea():
    from resumen import bloque_rivalidad

    assert bloque_rivalidad(historia("Ana", 8, score=3), "0", 1007) == ""


# @scenarios la-pelea-por-el-primer-puesto-se-cuenta
def test_la_pelea_no_deja_huecos_de_plantilla():
    """Un `{a}` sin rellenar saldría literal en el canal."""
    from resumen import bloque_rivalidad

    filas = historia("Ana", 8, score=3) + historia("Bea", 8, score=3)

    assert "{" not in bloque_rivalidad(filas, "0", 1007)


class _Senales:
    """Doble de las señales del canal. La red se queda en el borde, así que aquí basta un objeto."""

    def __init__(self, publicacion=None, reacciones=None, respuestas=None, aperturas=None, vistas=0):
        self.publicacion = publicacion or {}
        self.reacciones = reacciones or {}
        self.respuestas = respuestas or {}
        self.aperturas = aperturas or {}
        self.jornadas_vistas = vistas


# @scenarios la-jornada-se-cuenta-en-lugar-de-rotularse
def test_la_jornada_se_cuenta_en_frases_y_no_en_rotulos():
    from resumen import bloque_la_jornada

    # **Cinco jugadores como mínimo**: con menos, `dificultad()` devuelve None y la línea que compara la
    # jornada con la temporada no sale. Un fixture corto haría pasar el test por la razón equivocada.
    filas, hoy = [], []
    for i, nota in enumerate((2, 4, 4, 5, 5)):
        filas += historia(f"J{i}", 8, score=4)
        hoy.append(resultado(f"J{i}", HOY, nota, LORO if i == 0 else ABSTRACTO))

    bloque = bloque_la_jornada(filas + hoy, "0", HOY)

    assert "Jugador del día" not in bloque and "Obra del día" not in bloque, "ya no se rotula"
    assert bloque.startswith("• "), "es una lista"
    assert "de media" in bloque, f"la primera línea compara la jornada con la temporada: {bloque}"
    assert "J0" in bloque


# @scenarios la-jornada-se-cuenta-en-lugar-de-rotularse
def test_el_registro_de_la_linea_lo_decide_la_diferencia_con_la_temporada():
    """Los cortes están medidos sobre 166 jornadas: ±0,40 deja el 55% de los días en «normal»."""
    from resumen import DELTA_NOTABLE, bloque_la_jornada

    assert DELTA_NOTABLE == 0.40

    def jornada_de(historico: int, hoy_nota: int) -> str:
        filas, hoy = [], []
        for i in range(5):  # la muestra mínima, o no habría línea que comprobar
            filas += historia(f"J{i}", 8, score=historico)
            hoy.append(resultado(f"J{i}", HOY, hoy_nota, LORO))
        bloque = bloque_la_jornada(filas + hoy, "0", HOY)
        # **Se busca la línea, no se asume su posición**: el orden del bloque lo decide la relevancia, así que
        # la comparación con la temporada ya no es necesariamente la primera.
        return next(l for l in bloque.splitlines() if "de media" in l).removeprefix("• ")

    # **Contra el registro, no contra una palabra.** «difícil» solo está en una de las tres frases del
    # registro duro, así que la aserción literal fallaba con las otras dos según rotara el ciclo — y habría
    # vuelto a fallar al editar el diccionario, que está hecho para editarse.
    from refranero import DIFICULTAD_MUCHO_MAS_DURA, DIFICULTAD_MUCHO_MAS_FACIL

    duro = jornada_de(historico=3, hoy_nota=6)
    assert any(duro.startswith(f.split("{")[0]) for f in DIFICULTAD_MUCHO_MAS_DURA), duro

    facil = jornada_de(historico=5, hoy_nota=2)
    assert any(facil.startswith(f.split("{")[0]) for f in DIFICULTAD_MUCHO_MAS_FACIL), facil


# @scenarios quien-abre-por-costumbre-se-distingue-de-quien-abre-un-dia
def test_la_costumbre_de_madrugar_necesita_historico():
    from resumen import bloque_la_jornada

    filas = historia("Ana", 8, score=3) + historia("Bea", 8, score=4) + [
        resultado("Ana", HOY, 3, LORO), resultado("Bea", HOY, 4, FLOR),
    ]
    horas = {"U_Ana": 1788249600.0, "U_Bea": 1788253200.0}

    # Sin histórico suficiente: solo se dice que hoy abrió.
    suelto = bloque_la_jornada(filas, "0", HOY, _Senales(publicacion=horas))
    assert "Ana" in suelto and "costumbre" not in suelto and "de las últimas" not in suelto

    # Con costumbre demostrada: se dice, y con el recuento.
    habitual = bloque_la_jornada(
        filas, "0", HOY, _Senales(publicacion=horas, aperturas={"U_Ana": 8}, vistas=10)
    )
    assert "8" in habitual and "10" in habitual, habitual

    # **El caso que separa el umbral**, y sin él la prueba de mutación pasaba con `COSTUMBRE = 0`: quien ha
    # abierto 2 de 10 jornadas no lo hace por costumbre, lo hizo dos veces.
    from resumen import COSTUMBRE

    assert COSTUMBRE == 0.5
    poco = bloque_la_jornada(
        filas, "0", HOY, _Senales(publicacion=horas, aperturas={"U_Ana": 2}, vistas=10)
    )
    assert "costumbre" not in poco and "de las últimas" not in poco, poco


# @scenarios los-ausentes-se-nombran-sin-listarlos-todos
def test_los_ausentes_se_resumen_en_lugar_de_listarse():
    """Nombrar a todos hacía crecer el mensaje con el grupo, y señalar a doce no señala a nadie."""
    from resumen import AUSENTES_NOMBRADOS, bloque_la_jornada

    filas = []
    for i in range(9):
        filas += historia(f"J{i}", 8, score=4)
    filas += [resultado("J0", HOY, 4, FLOR), resultado("J1", HOY, 4, FLOR)]
    senales = _Senales(publicacion={"U_J0": 1788249600.0, "U_J1": 1788253200.0})

    bloque = bloque_la_jornada(filas, "0", HOY, senales)
    linea = next(l for l in bloque.splitlines() if "faltan" in l or "Sin noticias" in l or "libre" in l
                 or "presentado" in l)

    assert "y otros" in linea, f"el resto se resume: {linea}"
    assert linea.count(",") <= AUSENTES_NOMBRADOS, f"no se listan todos: {linea}"
    assert " y y " not in linea and ", y " not in linea, f"puntuación doblada: {linea}"


# @scenarios la-jornada-se-cuenta-en-lugar-de-rotularse
def test_la_dificultad_se_compara_con_las_jornadas_no_con_la_media_imputada():
    """La referencia es la dificultad media de las jornadas, no la media imputada del marcador.

    La imputada incluye la penalización de los días que cada uno no juega, así que está inflada y achata la
    diferencia: con los datos del día en que se corrigió, una jornada que estaba a +0,49 de la media real de
    las jornadas salía a +0,20 de la imputada y se publicaba como «de las de siempre». Lo cazó el dueño
    leyendo el mensaje, no la suite.
    """
    from resumen import _media_de_dificultades

    # Cinco jugadores que faltan la mitad de los días: su media imputada sube, la de las jornadas no.
    filas = []
    for i in range(5):
        filas += [resultado(f"J{i}", 1500 + j, 3) for j in range(4)]
    # Una jornada más, jugada por todos, con la misma nota: la dificultad media sigue siendo 3.
    filas += [resultado(f"J{i}", 1504, 3) for i in range(5)]

    referencia = _media_de_dificultades(filas, "0")

    assert referencia == pytest.approx(3.0), (
        f"la referencia son los intentos reales de las jornadas, no las medias imputadas: {referencia}"
    )


# @scenarios la-jornada-se-cuenta-en-lugar-de-rotularse
def test_la_linea_publicada_usa_la_referencia_correcta():
    """**Sobre el texto, no sobre la función.** Probar `_media_de_dificultades` no basta: la primera versión
    de este arreglo tenía esa función correcta y la línea seguía usando la media imputada, y la mutación pasó.

    El fixture está construido para que las dos referencias den textos distintos: cuatro jugadores juegan las
    diez jornadas —ocho fáciles y dos duras— y uno falta a las dos duras, así que su imputación penaliza y
    sube la media del marcador. Dificultades reales 2,11; imputada del grupo 2,68. Con la jornada de hoy en
    3,00 la primera da «mucho más dura» y la segunda «normal».
    """
    from resumen import bloque_la_jornada

    filas = []
    for i in range(4):
        filas += [resultado(f"J{i}", 1500 + j, 2 if j < 8 else 6, LORO) for j in range(10)]
    filas += [resultado("J4", 1500 + j, 2, LORO) for j in range(8)]
    hoy = [resultado(f"J{i}", HOY, 3, LORO) for i in range(5)]

    bloque = bloque_la_jornada(filas + hoy, "0", HOY)
    linea = next(l for l in bloque.splitlines() if "de media" in l)

    assert "2,11" in linea, f"la referencia publicada es la de las jornadas: {linea}"
    assert "2,68" not in linea, f"no la media imputada del marcador: {linea}"


# @scenarios el-mensaje-tiene-una-sola-voz
def test_el_estado_de_animo_sale_de_los_datos_y_gobierna_las_piezas_con_tono():
    """El mensaje sonaba a tres personas: cada pieza elegía de su propio registro sin mirar a las demás."""
    from refranero import CIERRE, CONECTORES, DERROTA, EPICA, FIESTA, INCREDULIDAD, RUTINA
    from voz import estado_de_animo

    # Un 1 o un 2 manda sobre todo lo demás: es de lo único que se va a hablar.
    assert estado_de_animo(3.0, 4.5, 2) == INCREDULIDAD, "aunque el día fuera fácil"
    # Día duro: épica si alguien destaca **sobre la dificultad de hoy**, derrota si no.
    assert estado_de_animo(5.2, 4.3, 3) == EPICA
    assert estado_de_animo(5.2, 4.3, 5) == DERROTA
    assert estado_de_animo(3.0, 4.3, 3) == FIESTA
    assert estado_de_animo(4.3, 4.3, 4) == RUTINA
    # Sin muestra no se afirma un estado: se cae a rutina.
    assert estado_de_animo(None, None, 4) == RUTINA

    for estado in (INCREDULIDAD, EPICA, DERROTA, RUTINA, FIESTA):
        assert CIERRE[estado] and CONECTORES[estado], f"{estado} sin frases"


# @scenarios lo-mas-notable-abre-el-comentario
def test_la_pulla_del_sospechoso_abre_el_comentario():
    """Con el orden fijo anterior, el titular del día aparecía en la séptima línea."""
    from resumen import bloque_la_jornada

    filas, hoy = [], []
    for i, nota in enumerate((2, 4, 4, 5, 5)):
        filas += historia(f"J{i}", 8, score=4)
        hoy.append(resultado(f"J{i}", HOY, nota, LORO))

    primera = bloque_la_jornada(filas + hoy, "0", HOY).splitlines()[0]

    assert "J0" in primera, f"quien resolvió en 2 abre: {primera}"
    assert "🤨" in primera, f"y con la pulla, no con el dato: {primera}"


# @scenarios lo-mas-notable-abre-el-comentario
def test_un_hecho_menor_no_se_cuela_por_delante_de_los_mejores():
    """**El caso que distingue el orden del de inserción.** Los hechos se construyen antes que las demás
    piezas, así que sin ordenar por relevancia cualquiera de ellos abriría el comentario. Un «día fino» no es
    el titular: los mejores del día sí. Lo cazó la prueba de mutación.
    """
    from resumen import bloque_la_jornada

    # Nadie baja de 3, así que no hay pulla; y J0 saca 3 en un día de media 5, que es «sembrado».
    filas, hoy = [], []
    for i, nota in enumerate((3, 5, 5, 6, 6)):
        filas += historia(f"J{i}", 8, score=5)
        hoy.append(resultado(f"J{i}", HOY, nota, LORO))

    lineas = bloque_la_jornada(filas + hoy, "0", HOY).splitlines()

    assert "🌟" not in lineas[0], f"un «día fino» no abre el comentario: {lineas[0]}"
    assert any("🌟" in l for l in lineas), "pero sí sale, más abajo"


# @scenarios la-segunda-linea-se-encadena-con-la-primera
def test_la_segunda_linea_se_encadena_sin_romper_los_nombres():
    """Minusculizar a ciegas publicaba «Faltaba decir que claire se lleva la jornada».

    El nombre de una compañera en minúscula es justo el detalle que delata que el texto lo escribe una
    máquina.
    """
    from refranero import CONECTORES, INCREDULIDAD
    from resumen import bloque_la_jornada

    filas, hoy = [], []
    for i, nota in enumerate((2, 4, 4, 5, 5)):
        filas += historia(f"Nombre{i}", 8, score=4)
        hoy.append(resultado(f"Nombre{i}", HOY, nota, LORO))

    lineas = bloque_la_jornada(filas + hoy, "0", HOY).splitlines()
    segunda = lineas[1].removeprefix("• ")

    assert any(segunda.startswith(c) for c in CONECTORES[INCREDULIDAD]), segunda
    assert "nombre0" not in segunda, f"el nombre propio conserva su mayúscula: {segunda}"
    assert "Nombre0" in segunda, segunda


def test_el_encadenado_baja_la_inicial_salvo_en_los_nombres():
    """Sobre la función, porque el caso integrado depende de qué frase rote ese día.

    «Hoy ha ido rodada» tras un conector tiene que ser «y hoy ha ido rodada», pero «Claire se lleva la
    jornada» no puede convertirse en «claire»: el nombre de una compañera en minúscula delata que el texto lo
    escribe una máquina.
    """
    from resumen import _en_minuscula

    nombres = ["Claire", "Andrés R."]

    assert _en_minuscula("Hoy ha ido rodada.", nombres) == "hoy ha ido rodada."
    assert _en_minuscula("Claire se lleva la jornada.", nombres) == "Claire se lleva la jornada."
    assert _en_minuscula("Andrés R. firma el dibujo.", nombres).startswith("Andrés R."), (
        "un nombre con punto dentro tampoco se toca"
    )
