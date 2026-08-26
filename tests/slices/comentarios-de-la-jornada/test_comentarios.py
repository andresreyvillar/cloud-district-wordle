"""Escenarios de `comentarios-de-la-jornada` (Fase 2 — TDD rojo).

Los detectores emiten **hechos**, no texto: así se pueden verificar sin fijar la redacción, y cambiar quién
escribe la frase —una plantilla hoy, un modelo mañana— no toca la detección.

Las jornadas de los fixtures tienen siempre cinco jugadores o más: con menos, la media del día no calibra y
el sistema no comenta nada a propósito.
"""

from __future__ import annotations

import pytest

HISTORICO = "2026-03-02"


def resultado(nombre, jornada, score, fecha=HISTORICO):
    return {
        "slack_user_id": f"U_{nombre}",
        "player_name": nombre,
        "wordle_id": jornada,
        "score": score,
        "date": fecha,
        "pattern": None,
    }


def jornada(numero, scores: dict[str, int]):
    return [resultado(nombre, numero, score) for nombre, score in scores.items()]


# @scenarios sospechoso-es-el-chiste-raro
def test_resolver_en_dos_un_dia_duro_se_senala():
    from comentarios import hechos_de_la_jornada

    # Media del día: (2+5+5+5+5)/5 = 4,4 ≥ 4,0
    filas = jornada(1600, {"Ana": 2, "B": 5, "C": 5, "D": 5, "E": 5})

    hechos = hechos_de_la_jornada(filas, "0", 1600)

    assert any(h.clave == "sospechoso" and h.jugador == "Ana" for h in hechos)


# @scenarios sospechoso-es-el-chiste-raro
def test_resolver_en_dos_es_sospechoso_aunque_el_dia_sea_facil():
    """**Decisión del dueño**: resolver en uno o dos es sospechoso de base.

    Antes hacía falta además un día duro y el aviso salía en el 6% de las jornadas — prácticamente nunca, y
    por eso una jornada real con un 2 pasó sin pulla. Medido: sin esa condición sale en el 29%.
    """
    from comentarios import hechos_de_la_jornada, frase

    facil = jornada(1600, {"Ana": 2, "B": 2, "C": 3, "D": 2, "E": 3})
    hechos = hechos_de_la_jornada(facil, "0", 1600)
    sospechosos = [h for h in hechos if h.clave == "sospechoso"]

    assert sospechosos, "un 2 recibe pulla aunque el día fuera fácil"
    assert {h.jugador for h in sospechosos} == {"Ana", "B", "D"}

    # Y la pulla **no puede afirmar que el día fuera duro**, porque ya no se comprueba.
    for indice in range(20):
        texto = frase("sospechoso", 1600 + indice, "Ana", 2.0)
        assert "sufría" not in texto and "día así" not in texto, texto


# @scenarios sospechoso-es-el-chiste-raro
def test_varios_sospechosos_concuerdan_en_plural():
    """Pasa en 14 de las 167 jornadas del histórico. Sin la variante, saldría «Ana y Bea lo ha sacado»."""
    from comentarios import frase

    for indice in range(12):
        texto = frase("sospechoso", 1600 + indice, "Ana y Bea", 2.0, varios=True)
        assert " lo ha sacado" not in texto, texto
        assert "Ana y Bea" in texto


# @scenarios sembrado-y-no-inspirado-son-simetricos
def test_muy_por_debajo_de_la_media_es_estar_sembrado():
    from comentarios import MARGEN_SEMBRADO, hechos_de_la_jornada

    # Media 5,0; Ana saca 3, que es 2,0 mejor.
    filas = jornada(1600, {"Ana": 3, "B": 5, "C": 5, "D": 6, "E": 6})

    hechos = hechos_de_la_jornada(filas, "0", 1600)

    assert MARGEN_SEMBRADO == 1.5
    assert any(h.clave == "sembrado" and h.jugador == "Ana" for h in hechos)


# @scenarios sembrado-y-no-inspirado-son-simetricos
def test_el_margen_de_no_inspirado_es_el_recalibrado():
    """Con 1,5 salía 0,48 por jornada — casi un día sí y otro no. Con 2,0, 0,24."""
    from comentarios import MARGEN_NO_INSPIRADO, hechos_de_la_jornada

    assert MARGEN_NO_INSPIRADO == 2.0

    # Media 3,0. Un 4 está 1,0 por encima: no basta. Un 6 está 3,0: sí.
    justo = jornada(1600, {"Ana": 4, "B": 3, "C": 3, "D": 2, "E": 3})
    assert not any(h.clave == "no-inspirado" for h in hechos_de_la_jornada(justo, "0", 1600))

    claro = jornada(1601, {"Ana": 6, "B": 3, "C": 3, "D": 2, "E": 3})
    assert any(h.clave == "no-inspirado" and h.jugador == "Ana" for h in hechos_de_la_jornada(claro, "0", 1601))


# @scenarios rajado-usa-el-modelo-de-dificultad
def test_la_ausencia_en_dia_dificil_usa_el_umbral_de_las_medallas():
    from badges import UMBRAL_DIA_DIFICIL
    from comentarios import hechos_de_la_jornada

    # Día de media 5,0 ≥ 4,5. Fanny jugó otros días de la temporada pero hoy no.
    antes = jornada(1599, {"Ana": 4, "B": 4, "C": 4, "D": 4, "E": 4, "Fanny": 4})
    hoy = jornada(1600, {"Ana": 5, "B": 5, "C": 5, "D": 5, "E": 5})

    hechos = hechos_de_la_jornada(antes + hoy, "0", 1600)

    assert UMBRAL_DIA_DIFICIL == 4.5, "se reutiliza, no se declara otro"
    assert any(h.clave == "rajado" and h.jugador == "Fanny" for h in hechos)


# @scenarios rajado-usa-el-modelo-de-dificultad
def test_faltar_un_dia_facil_no_se_comenta():
    from comentarios import hechos_de_la_jornada

    antes = jornada(1599, {"Ana": 3, "B": 3, "C": 3, "D": 3, "E": 3, "Fanny": 3})
    hoy = jornada(1600, {"Ana": 3, "B": 3, "C": 3, "D": 3, "E": 3})

    assert not any(h.clave == "rajado" for h in hechos_de_la_jornada(antes + hoy, "0", 1600))


# @scenarios un-hecho-no-se-repite-en-dos-comentarios
def test_una_persona_aparece_una_sola_vez():
    from comentarios import hechos_de_la_jornada

    # Ana resuelve en 2 un día de media 4,4: dispara «sospechoso» y también «sembrado».
    filas = jornada(1600, {"Ana": 2, "B": 5, "C": 5, "D": 5, "E": 5})

    hechos = hechos_de_la_jornada(filas, "0", 1600)
    de_ana = [h for h in hechos if h.jugador == "Ana"]

    assert len(de_ana) == 1
    assert de_ana[0].clave == "sospechoso", "gana el hecho más notable, no el primero que se calcule"


# @scenarios los-comentarios-se-limitan
def test_la_seccion_no_se_convierte_en_un_muro():
    from comentarios import MAXIMO_COMENTARIOS, seccion_de_comentarios

    # Muchísima gente muy por encima de la media.
    scores = {"Ana": 1, "B": 1, "C": 1, "D": 1, "E": 1}
    scores.update({f"Malo{i}": 7 for i in range(10)})
    filas = jornada(1600, scores)

    texto = seccion_de_comentarios(filas, "0", 1600)

    assert 0 < len([l for l in texto.splitlines() if l.startswith("•")]) <= MAXIMO_COMENTARIOS


# @scenarios los-comentarios-se-limitan
def test_no_se_repite_el_mismo_chiste_tres_veces():
    """Lo enseñó el mensaje real, no un test: un día duro llenaba la sección con tres «se ha rajado».

    La notabilidad ordena, así que todos los hechos de la clase más notable se comían el hueco. Ahora sale
    **un comentario por tipo**, y las ausencias van juntas en una línea: tres líneas seguidas señalando a
    tres ausentes dejan de ser una broma y son una lista de morosos.
    """
    from comentarios import seccion_de_comentarios

    # TRES personas disparan «no inspirado», que es un hecho por persona y no se agrupa. Con las ausencias
    # no valía: van juntas en un solo hecho, así que la línea salía una vez aunque no hubiera deduplicación
    # por tipo — el mutante sobrevivía y el test parecía cubrirlo.
    hoy = jornada(1600, {"Ana": 1, "B": 1, "C": 1, "D": 6, "E": 6, "F": 6})

    lineas = [l for l in seccion_de_comentarios(hoy, "0", 1600).splitlines() if l.startswith("•")]

    sin_inspiracion = [l for l in lineas if any(x in l for x in ("inspirad", "atragantado", "olvidar"))]
    assert len(sin_inspiracion) == 1, f"el mismo chiste repetido: {sin_inspiracion}"
    assert len(lineas) <= 3


# @scenarios rajado-usa-el-modelo-de-dificultad
def test_no_se_llama_rajado_a_quien_no_juega_esta_temporada():
    """Carmen jugó una vez en marzo. Llamarla rajada en agosto es un chiste sobre alguien que ya no está."""
    from comentarios import hechos_de_la_jornada

    de_otra = [resultado("Carmen", 1400, 4, fecha="2026-03-02")]
    esta = jornada(1700, {n: 5 for n in ("Ana", "B", "C", "D", "E")})
    for fila in esta:
        fila["date"] = "2026-09-07"

    hechos = hechos_de_la_jornada(de_otra + esta, "2026-09", 1700)

    assert not any("Carmen" in h.jugador for h in hechos)


# @scenarios sin-hechos-no-hay-seccion
def test_sin_hechos_no_hay_seccion():
    from comentarios import seccion_de_comentarios

    filas = jornada(1600, {"Ana": 4, "B": 4, "C": 4, "D": 4, "E": 4})

    assert seccion_de_comentarios(filas, "0", 1600) == ""


# @scenarios sin-hechos-no-hay-seccion
def test_sin_dificultad_calculable_no_se_comenta():
    """Con menos de cinco jugadores la media del día no calibra nada: no hay contra qué comparar."""
    from comentarios import seccion_de_comentarios

    filas = jornada(1600, {"Ana": 1, "B": 7})

    assert seccion_de_comentarios(filas, "0", 1600) == ""


# @scenarios la-frase-varia-sin-azar
def test_el_mismo_dia_produce_exactamente_el_mismo_texto():
    from comentarios import seccion_de_comentarios

    filas = jornada(1600, {"Ana": 2, "B": 5, "C": 5, "D": 5, "E": 5})

    assert seccion_de_comentarios(filas, "0", 1600) == seccion_de_comentarios(filas, "0", 1600)


# @scenarios la-frase-varia-sin-azar
def test_el_texto_varia_entre_jornadas_sin_usar_azar():
    """Variedad sin `random`: la frase se elige con el número de jornada, que es un dato, no un sorteo."""
    from comentarios import frase

    frases = {frase("sospechoso", jornada_numero, "Ana") for jornada_numero in range(1600, 1610)}

    assert len(frases) > 1, "diez jornadas seguidas no pueden dar siempre la misma frase"
    assert all("Ana" in f for f in frases)


# @scenarios la-frase-concuerda-en-numero
def test_la_frase_concuerda_cuando_faltan_varios():
    """«Carlos, Edu Noeda no ha aparecido» salió en el mensaje real. El castellano concuerda."""
    from comentarios import FRASES, frase

    # Se comprueba en TODAS las jornadas del ciclo, no en una: con 1600 salía la frase sin verbo
    # concordado («Silencio de…») y el test pasaba sin mirar lo que decía comprobar.
    for desplazamiento in range(len(FRASES["rajado"])):
        una = frase("rajado", 1599 + desplazamiento, "Carlos", varios=False)
        varias = frase("rajado", 1599 + desplazamiento, "Carlos, Edu Noeda", varios=True)
        assert " ha " not in varias, f"concordancia rota en {varias!r}"
        assert una != varias or " ha " not in una, "si no cambia, es porque la frase no lleva verbo"

    assert "no ha aparecido" in frase("rajado", 1599, "Carlos")
    assert "no han aparecido" in frase("rajado", 1599, "Carlos, Edu Noeda", varios=True)


# ── Los disparadores que dependen de la hora de publicación ──────────────────────────────────────────
#
# `created_at` es cuando el cron escribió la fila, así que aproxima la hora de publicación con un margen de
# hasta una hora. Sirve para distinguir "publicó por la mañana" de "publicó a media tarde", que es lo único
# que estos chistes necesitan. **Solo se usa si cae el mismo día que el puzzle**: las 268 filas del backfill
# se metieron todas de golpe otro día, y con ellas el margen no es de una hora sino de meses.

def con_hora(fila, hora, dia="2026-03-02"):
    return {**fila, "created_at": f"{dia}T{hora:02d}:30:00+00:00"}


# @scenarios el-rezagado-lo-comenta-quien-tiene-la-hora-buena
def test_este_slice_ya_no_comenta_al_rezagado():
    """El detector se retiró: se apoyaba en `created_at`, que es cuando el cron escribió la fila.

    Medido: el cron escribe por lotes cada hora y solo el 34% de los resultados de una jornada tienen minuto
    distinto, así que «el último en publicar» era casi ruido. Ahora lo comenta `voz-de-la-jornada` con la hora
    real del canal, y aquí no puede volver a colarse un hecho que dependa de la hora de registro.
    """
    import comentarios

    assert not hasattr(comentarios, "_por_la_hora")
    assert "rezagado" not in comentarios.NOTABILIDAD
    assert "rezagado-con-suerte" not in comentarios.NOTABILIDAD


# @scenarios la-suerte-sospechosa-se-senala
def test_acertar_a_la_primera_es_el_chiste_estrella():
    """Una clavada sale 0,01 por jornada: dos veces en 186 jornadas."""
    from comentarios import hechos_de_la_jornada

    filas = jornada(1600, {"Ana": 1, "B": 4, "C": 4, "D": 4, "E": 4})

    hechos = hechos_de_la_jornada(filas, "0", 1600)
    de_ana = [h for h in hechos if h.jugador == "Ana"]

    assert de_ana and de_ana[0].clave == "clavada"


# @scenarios ausencia-en-dia-dificil
def test_muchos_ausentes_no_se_nombran_uno_por_uno():
    """Visto en el mensaje real: «Silencio de» seguido de ocho nombres.

    Hace crecer el mensaje con el grupo, que es lo que `el-mensaje-no-crece-con-el-grupo` impide, y señalar a
    media liga no señala a nadie. Por encima del tope la ausencia es el dato del día, no una pulla.

    **La primera versión de este test era vacua**: dejaba a dos jugadores en la jornada, y con menos de cinco
    `dificultad()` devuelve `None`, así que el detector no llegaba a dispararse y la aserción pasaba por la
    razón equivocada. Lo cazó la prueba de mutación. Ahora la jornada tiene muestra suficiente y se comprueba
    el borde por los dos lados.
    """
    from comentarios import MAXIMO_AUSENTES_NOMBRADOS, hechos_de_la_jornada

    habituales = 11
    historia = []
    for i in range(habituales):
        historia += [resultado(f"J{i}", 1500 + j, 5) for j in range(6)]

    def rajados(cuantos_juegan):
        hoy = [resultado(f"J{i}", 1600, 6) for i in range(cuantos_juegan)]
        return [h for h in hechos_de_la_jornada(historia + hoy, "0", 1600) if h.clave == "rajado"]

    # Seis juegan, cinco faltan: por encima del tope, no se comenta.
    muchos = rajados(6)
    assert not muchos, f"cinco ausentes no se nombran: {[h.jugador for h in muchos]}"

    # Nueve juegan, dos faltan: justo en el tope, sí se comenta.
    pocos = rajados(habituales - MAXIMO_AUSENTES_NOMBRADOS)
    assert pocos, "con dos ausentes la pulla sí sale, o el detector estaría muerto"
    assert pocos[0].jugador.count(",") == MAXIMO_AUSENTES_NOMBRADOS - 1


# @scenarios un-hecho-no-se-repite-en-dos-comentarios
def test_los_que_comparten_hecho_se_fusionan_en_una_linea():
    """Dos sospechosos el mismo día son **una** línea en plural, no dos idénticas ni una sola persona.

    `hechos_elegidos` devolvía solo el primero de cada clave, así que las variantes en plural del diccionario
    eran código que nunca se ejecutaba y el segundo sospechoso desaparecía del mensaje sin dejar rastro.
    """
    from comentarios import hechos_elegidos

    filas = jornada(1600, {"Ana": 2, "Bea": 2, "C": 4, "D": 5, "E": 5})

    sospechosos = [h for h in hechos_elegidos(filas, "0", 1600) if h.clave == "sospechoso"]

    assert len(sospechosos) == 1, "una sola línea"
    assert sospechosos[0].varios is True, "y en plural"
    assert sospechosos[0].jugador == "Ana y Bea", sospechosos[0].jugador


# @scenarios un-hecho-no-se-repite-en-dos-comentarios
def test_el_tope_de_comentarios_cuenta_tipos_y_no_personas():
    """El tope limita cuántos temas se comentan, no a cuánta gente se nombra dentro de cada uno."""
    from comentarios import MAXIMO_COMENTARIOS, hechos_elegidos

    filas = jornada(1600, {"Ana": 2, "Bea": 2, "C": 2, "D": 6, "E": 6})

    elegidos = hechos_elegidos(filas, "0", 1600)

    assert len({h.clave for h in elegidos}) <= MAXIMO_COMENTARIOS
    assert len(elegidos) == len({h.clave for h in elegidos}), "un hecho por tipo tras la fusión"


# @scenarios sospechoso-es-el-chiste-raro
def test_el_berrinche_sirve_para_uno_y_para_varios():
    """Las frases de berrinche están escritas **sin concordancia de número** a propósito.

    Así valen para un sospechoso y para tres sin necesitar variante en plural — que es donde este diccionario
    ya se equivocó una vez, publicando «Ana y Bea lo ha sacado en 2».
    """
    from comentarios import FRASES
    from refranero import BERRINCHE

    for registro in ("sospechoso", "sospechoso-varios"):
        assert all(f in FRASES[registro] for f in BERRINCHE), f"el berrinche falta en {registro}"

    for plantilla in BERRINCHE:
        # Un verbo conjugado delataría que la frase asume cuántos son.
        assert " ha " not in plantilla and " han " not in plantilla, plantilla
        # Y tiene que quedar bien con un sujeto plural.
        texto = plantilla.format(jugador="Ana y Bea", dato=2.0)
        assert "{" not in texto and "}" not in texto, texto


def test_ninguna_frase_deja_huecos_sin_rellenar():
    """Un `{jugador}` mal escrito saldría literal en el canal, delante de todo el grupo."""
    from comentarios import FRASES

    for clave, plantillas in FRASES.items():
        for plantilla in plantillas:
            texto = plantilla.format(jugador="Ana", dato=2.0)
            assert "{" not in texto and "}" not in texto, f"{clave}: {plantilla}"


# @scenarios la-sospecha-no-repite-el-molde
def test_la_sospecha_no_repite_siempre_el_mismo_molde():
    """**El defecto que el dueño leyó en el canal.** El registro tenía 🤨 en las 24 frases y la nota en 22,
    así que las palabras cambiaban y el molde no: se leía como el mismo chiste todos los días.

    Se comprueba **pasando por la selección real**, no mirando el registro: lo que importa es lo que sale
    publicado en una serie de jornadas.
    """
    from comentarios import frase

    salidas = [frase("sospechoso", j, "Ana", dato=2) for j in range(1, 60)]
    distintas = set(salidas)
    assert len(distintas) >= 20, f"pocas frases distintas: {len(distintas)}"

    sin_emoji = [s for s in distintas if "🤨" not in s]
    sin_nota = [s for s in distintas if "2" not in s]
    assert len(sin_emoji) >= 8, f"casi todas llevan el mismo emoji: {len(sin_emoji)} de {len(distintas)}"
    assert len(sin_nota) >= 8, f"casi todas citan la nota: {len(sin_nota)} de {len(distintas)}"


# @scenarios la-sospecha-no-repite-el-molde
def test_la_sospecha_en_plural_tampoco_repite_el_molde():
    from comentarios import frase

    salidas = {frase("sospechoso", j, "Ana y Bea", dato=2, varios=True) for j in range(1, 60)}
    sin_emoji = [s for s in salidas if "🤨" not in s]
    assert len(sin_emoji) >= 8, f"el plural sigue con el mismo molde: {len(sin_emoji)} de {len(salidas)}"
