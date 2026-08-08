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
def test_resolver_en_dos_un_dia_facil_no_es_sospechoso():
    """El chiste vive de la comparación: en un día fácil, un 2 no llama la atención."""
    from comentarios import hechos_de_la_jornada

    filas = jornada(1600, {"Ana": 2, "B": 2, "C": 3, "D": 2, "E": 3})

    assert not any(h.clave == "sospechoso" for h in hechos_de_la_jornada(filas, "0", 1600))


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


# @scenarios el-rezagado-se-nota
def test_el_ultimo_en_publicar_con_mucho_hueco_se_comenta():
    from comentarios import hechos_de_la_jornada

    filas = [con_hora(f, 8) for f in jornada(1600, {"Ana": 4, "B": 4, "C": 4, "D": 4})]
    filas.append(con_hora(resultado("Tarde", 1600, 4), 17))

    hechos = hechos_de_la_jornada(filas, "0", 1600)

    assert any(h.clave == "rezagado" and h.jugador == "Tarde" for h in hechos)


# @scenarios el-rezagado-se-nota
def test_publicar_a_la_vez_que_los_demas_no_es_ser_rezagado():
    from comentarios import hechos_de_la_jornada

    filas = [con_hora(f, 8) for f in jornada(1600, {"Ana": 4, "B": 4, "C": 4, "D": 4, "E": 4})]

    assert not any(h.clave == "rezagado" for h in hechos_de_la_jornada(filas, "0", 1600))


# @scenarios el-rezagado-se-nota
def test_sin_hora_utilizable_no_se_comenta_el_retraso():
    """Las filas del backfill se escribieron todas otro día: su hora no dice cuándo se publicó."""
    from comentarios import hechos_de_la_jornada

    filas = [con_hora(f, 8, dia="2026-02-02") for f in jornada(1600, {"Ana": 4, "B": 4, "C": 4, "D": 4})]
    filas.append(con_hora(resultado("Tarde", 1600, 4), 17, dia="2026-02-02"))

    assert not any(h.clave == "rezagado" for h in hechos_de_la_jornada(filas, "0", 1600))


# @scenarios la-suerte-sospechosa-se-senala
def test_llegar_tarde_y_ademas_clavarla_es_el_chiste_bueno():
    """Publicar el último y con una nota muy por encima de la media: 0,06 por jornada."""
    from comentarios import hechos_de_la_jornada

    filas = [con_hora(f, 8) for f in jornada(1600, {"Ana": 5, "B": 5, "C": 5, "D": 5})]
    filas.append(con_hora(resultado("Listillo", 1600, 2), 17))

    hechos = hechos_de_la_jornada(filas, "0", 1600)
    suyo = [h for h in hechos if h.jugador == "Listillo"]

    assert suyo and suyo[0].clave == "rezagado-con-suerte", f"{suyo}"


# @scenarios la-suerte-sospechosa-se-senala
def test_acertar_a_la_primera_es_el_chiste_estrella():
    """Una clavada sale 0,01 por jornada: dos veces en 186 jornadas."""
    from comentarios import hechos_de_la_jornada

    filas = jornada(1600, {"Ana": 1, "B": 4, "C": 4, "D": 4, "E": 4})

    hechos = hechos_de_la_jornada(filas, "0", 1600)
    de_ana = [h for h in hechos if h.jugador == "Ana"]

    assert de_ana and de_ana[0].clave == "clavada"
