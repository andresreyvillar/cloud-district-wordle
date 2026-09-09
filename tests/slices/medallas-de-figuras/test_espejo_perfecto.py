

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
    from badges import CUERPO_MINIMO_DEL_LOGRO, medallas_permanentes
    from figures import rasgos

    r = rasgos(ESPEJO_TRIVIAL)
    assert r.espejo and r.alto < CUERPO_MINIMO_DEL_LOGRO, f"el fixture debe ser trivial: {r}"
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
    from badges import CUERPO_MINIMO_DEL_LOGRO, medallas_permanentes
    from figures import rasgos

    torcida = "Y..../GG.../GG.GG/GGGGG"
    r = rasgos(torcida)
    assert not r.espejo, f"el fixture debe ser asimétrico: {r}"
    assert r.alto >= CUERPO_MINIMO_DEL_LOGRO, f"y alto de sobra: {r}"

    filas = [_partida("Ana", 1, "2099-01-05", 4, torcida)]
    assert "espejo-perfecto" not in medallas_permanentes(filas).get("Ana", [])


# ── El Coleccionista y las categorías que se han visto ──────────────────────────────────────────────────

#: Laborables reales de enero de 2099. Cae en una temporada **numerada**, así que cada jornada necesita al
#: menos cinco jugadores para contar: de ahí el relleno.
DIAS_DE_PRUEBA = ["2099-01-05", "2099-01-06", "2099-01-07", "2099-01-08", "2099-01-09",
                  "2099-01-12", "2099-01-13", "2099-01-14"]
MES_DE_PRUEBA = "2099-01"


def _con_dibujos(nombre: str, dibujos: list[str]) -> list[dict]:
    """Una partida por dibujo, más el relleno que hace que las jornadas cuenten."""
    filas = []
    for i, patron in enumerate(dibujos):
        filas.append(_partida(nombre, 1700 + i, DIAS_DE_PRUEBA[i], 4, patron))
        filas += [_partida(f"r{j}", 1700 + i, DIAS_DE_PRUEBA[i], 4, None) for j in range(4)]
    return filas


# @scenarios el-coleccionista-se-ajusta-a-lo-que-ha-salido
def test_el_coleccionista_exige_lo_que_ha_salido_en_la_temporada():
    """**Añadir el melocotón a una lista fija habría quitado la medalla a 25 personas** que ya la tienen
    publicada —8 de agosto y 17 de la temporada 0— porque el culo no existe antes del corte de reglas.
    Derivarlo de lo que ha salido lo evita sin un corte más.
    """
    from badges import _es_coleccionista

    # Cuatro categorías vistas: quien tiene las cuatro es coleccionista aunque no tenga culo.
    cuatro = {"loro", "geometrico", "flores", "abstracto"}
    tiene_cuatro = {"loro": 1, "geometrico": 1, "flores": 1, "abstracto": 1}
    assert _es_coleccionista(tiene_cuatro, cuatro)

    # Con el culo entre las vistas, ya se pide.
    cinco = cuatro | {"culo"}
    assert not _es_coleccionista(tiene_cuatro, cinco), "si el culo ha salido, hace falta"
    assert _es_coleccionista({**tiene_cuatro, "culo": 1}, cinco)


# @scenarios el-coleccionista-se-ajusta-a-lo-que-ha-salido
def test_las_categorias_vistas_salen_del_album():
    """Del mismo sitio que los recuentos: un segundo recuento de lo mismo es cómo este repositorio ya se ha
    equivocado tres veces.
    """
    from badges import categorias_vistas

    from figures import figura

    dibujos = [ESPEJO_DE_CUATRO, ".G.../.G..G/.GY../GGGGG", "G.G.G/GGGGG"]
    filas = _con_dibujos("Ana", dibujos)
    vistas = categorias_vistas(filas, MES_DE_PRUEBA)

    # Lo que ha salido es exactamente lo que dice el clasificador de esos dibujos, más el abstracto del
    # relleno sin patrón… que no cuenta, porque sin cuadrícula no hay figura.
    esperadas = {figura(p, 1700 + i) for i, p in enumerate(dibujos)}
    assert esperadas <= vistas, f"faltan categorías dibujadas: {esperadas - vistas}"
    assert vistas <= esperadas | {"abstracto"}, f"sobran categorías: {vistas - esperadas}"


# @scenarios el-coleccionista-se-ajusta-a-lo-que-ha-salido
def test_sin_categorias_vistas_se_cae_a_las_cuatro_de_siempre():
    """El respaldo importa: sin datos de temporada, la condición no puede quedar vacía y darse por buena a
    cualquiera. `all()` de un conjunto vacío es `True`, que es la trampa.
    """
    from badges import _es_coleccionista

    assert not _es_coleccionista({"loro": 1}, None), "con un solo dibujo no es coleccionista"
    assert not _es_coleccionista({}, set()), "y sin nada, tampoco"


# @scenarios el-coleccionista-se-ajusta-a-lo-que-ha-salido
def test_el_flujo_completo_exige_el_melocoton_cuando_ha_salido():
    """**El flujo, no solo la condición.** La mutación que no pasa las categorías vistas al cálculo no mataba
    ningún test: la condición estaba probada suelta y su uso no.
    """
    from badges import medallas_de_temporada
    from figures import CULO, figura

    culo = "G.G.G/GGGGG"
    loro = ".G.../.G..G/.GY../GGGGG"
    geometrico = "..G../..G../GGGGG"
    flor = "Y..../..Y../GGGGG"
    assert figura(culo, 1700) == CULO, "el fixture debe dar culo"

    # Ana tiene las cuatro de siempre pero **no** el melocotón; Bea las cinco.
    cuatro = [loro, geometrico, flor, None]
    cinco = [loro, geometrico, flor, culo]
    filas = _con_dibujos("Ana", cuatro) + [
        _partida("Bea", 1700 + i, DIAS_DE_PRUEBA[i], 4, p) for i, p in enumerate(cinco)
    ]
    medallas = medallas_de_temporada(filas, MES_DE_PRUEBA)
    assert "coleccionista" in medallas.get("Bea", []), f"Bea tiene las cinco: {medallas.get('Bea')}"
    assert "coleccionista" not in medallas.get("Ana", []), (
        f"a Ana le falta el melocotón, que sí ha salido este mes: {medallas.get('Ana')}")
