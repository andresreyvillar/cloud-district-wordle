

# ── El espejo perfecto ──────────────────────────────────────────────────────────────────────────────────
#
# El umbral es lo que hace el logro. Medido sobre las 1.706 cuadrículas del histórico: con cuerpo >= 1 hay 19
# espejos y los tendría el 43% del grupo; con >= 4 existe una sola en toda la historia; con >= 3 hay siete, de
# siete personas distintas, una cada cinco meses.

#: La cuadrícula que motivó el logro: cuatro filas de cuerpo, simétrica, y etiquetada «flores».
ESPEJO_DE_CUATRO = "Y...Y/GG.GG/GG.GG/GG.GG/GGGGG"
#: Simétrica pero de una sola fila: simetría por accidente.
ESPEJO_TRIVIAL = ".GGG./GGGGG"


def _partida(nombre: str, jornada: int, dia: str, score: int, patron: str | None) -> dict:
    return {
        "player_name": nombre,
        "slack_user_id": nombre,
        "wordle_id": jornada,
        "date": dia,
        "score": score,
        "pattern": patron,
    }


# @scenarios el-espejo-perfecto-tiene-su-logro
def test_el_espejo_con_cuerpo_suficiente_da_el_logro():
    from badges import medallas_permanentes

    filas = [_partida("Ana", 1, "2099-01-05", 5, ESPEJO_DE_CUATRO)]
    assert "espejo-perfecto" in medallas_permanentes(filas).get("Ana", [])


# @scenarios el-espejo-perfecto-tiene-su-logro
def test_el_espejo_trivial_no_da_el_logro():
    """Con cuerpo de una fila lo tendría el 43% del grupo: no distinguiría a nadie."""
    from badges import MINIMO_CUERPO_DEL_ESPEJO, medallas_permanentes
    from figures import rasgos

    r = rasgos(ESPEJO_TRIVIAL)
    assert r.espejo and r.alto < MINIMO_CUERPO_DEL_ESPEJO, f"el fixture debe ser trivial: {r}"
    filas = [_partida("Ana", 1, "2099-01-05", 2, ESPEJO_TRIVIAL)]
    assert "espejo-perfecto" not in medallas_permanentes(filas).get("Ana", [])


# @scenarios el-espejo-perfecto-tiene-su-logro
def test_el_logro_del_espejo_se_anuncia_el_dia_que_ocurre():
    from badges import medallas_permanentes

    filas = [
        _partida("Ana", 1, "2099-01-05", 4, ".GGG./GGGGG"),
        _partida("Ana", 2, "2099-01-06", 5, ESPEJO_DE_CUATRO),
    ]
    assert "espejo-perfecto" not in medallas_permanentes(filas, jornada=1).get("Ana", [])
    assert "espejo-perfecto" in medallas_permanentes(filas, jornada=2).get("Ana", [])


# @scenarios el-logro-del-espejo-mira-el-rasgo-y-no-la-categoria
def test_el_logro_se_da_aunque_la_categoria_sea_flor():
    """**El caso que lo motivó.** En `figura()` el espejo se consulta en último lugar, así que esa cuadrícula
    se etiqueta «flores»: si el logro dependiera de la categoría, se perdería justo en el mejor dibujo.
    """
    from badges import medallas_permanentes
    from figures import figura

    assert figura(ESPEJO_DE_CUATRO) == "flores", "la etiqueta es flor, y aun así el logro debe darse"
    filas = [_partida("Ana", 1, "2099-01-05", 5, ESPEJO_DE_CUATRO)]
    assert "espejo-perfecto" in medallas_permanentes(filas).get("Ana", [])


# @scenarios sin-patron-no-da-medalla
def test_sin_patron_no_hay_logro_de_espejo():
    from badges import medallas_permanentes

    filas = [_partida("Ana", 1, "2099-01-05", 5, None)]
    assert "espejo-perfecto" not in medallas_permanentes(filas).get("Ana", [])


# @scenarios el-espejo-perfecto-tiene-su-logro
def test_una_cuadricula_alta_pero_asimetrica_no_da_el_logro():
    """**El caso que faltaba.** Los otros fixtures eran o simétricos y altos, o simétricos y bajos, así que
    quitar la exigencia de simetría no ponía nada en rojo: el logro se habría dado a cualquier cuadrícula de
    tres filas. Lo destapó la prueba de mutación.
    """
    from badges import MINIMO_CUERPO_DEL_ESPEJO, medallas_permanentes
    from figures import rasgos

    torcida = "Y..../GG.../GG.GG/GGGGG"
    r = rasgos(torcida)
    assert not r.espejo, f"el fixture debe ser asimétrico: {r}"
    assert r.alto >= MINIMO_CUERPO_DEL_ESPEJO, f"y alto de sobra: {r}"

    filas = [_partida("Ana", 1, "2099-01-05", 4, torcida)]
    assert "espejo-perfecto" not in medallas_permanentes(filas).get("Ana", [])
