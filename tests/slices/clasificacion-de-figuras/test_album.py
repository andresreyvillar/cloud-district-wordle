"""Escenarios de `clasificacion-de-figuras` (Fase 2 — TDD rojo).

Fixtures a mano, con **patrones reales verificados contra el clasificador**: cada cuadrícula de este
fichero se comprueba en `test_los_fixtures_dibujan_lo_que_dicen_dibujar` antes de usarse. Un fixture que
creyera dibujar un loro y dibujara un abstracto haría pasar tests que no prueban nada.

Casi todos los escenarios usan la **temporada 0**, donde no hay filtros de jornada: así el fixture prueba
el álbum y no el modelo de temporada, que ya tiene sus propios tests. El único que necesita una temporada
numerada es el que comprueba justamente que el álbum hereda sus días.
"""

from __future__ import annotations

import pytest

MOTIVO = "TDD rojo — tools/album.py no existe todavía"

#: Cuadrículas de cada categoría, en el formato en que la ingesta las guarda (`G/Y/.` separado por barras).
LORO = ".G.../.G..G/.GY../GGGGG"
GEOMETRICO = "..G../..G../GGGGG"
FLOR = "Y...Y/..Y../GGGGG"

#: **Asimétrico a propósito.** El anterior (`GG.GG/GGYGG/GG.GG`) era un espejo perfecto sin que nadie lo
#: hubiera notado, así que al añadirse la regla del espejo dejó de ser abstracto y se llevó cinco tests por
#: delante. Se sustituyó el fixture, no la aserción: era el fixture el que había dejado de ser cierto.
ABSTRACTO = "GG.GG/GGYG./GG.GG/GGGGG"

#: Una jornada de la temporada 0 (anterior al límite de temporadas, así que no filtra ni finde ni muestra).
HISTORICO = "2026-03-02"


def resultado(
    jugador: str,
    jornada: int,
    patron: str | None,
    fecha: str = HISTORICO,
    nombre: str | None = None,
    score: int = 4,
) -> dict:
    return {
        "slack_user_id": jugador,
        "player_name": nombre or jugador,
        "wordle_id": jornada,
        "score": score,
        "date": fecha,
        "pattern": patron,
    }


def partidas(jugador: str, patrones: list[str | None], nombre: str | None = None) -> list[dict]:
    """Una partida por patrón, cada una en su jornada."""
    return [
        resultado(jugador, 1500 + indice, patron, nombre=nombre)
        for indice, patron in enumerate(patrones)
    ]


def fila_de(carga: dict, jugador: str) -> dict:
    return next(fila for fila in carga["jugadores"] if fila["jugador"] == jugador)


def test_los_fixtures_dibujan_lo_que_dicen_dibujar():
    """El fixture se verifica contra el clasificador, no contra la intención de quien lo escribió."""
    from figures import figura

    assert figura(LORO) == "loro"
    assert figura(GEOMETRICO) == "geometrico"
    assert figura(FLOR) == "flores"
    assert figura(ABSTRACTO) == "abstracto"


# @scenarios figura-de-cada-partida
def test_cada_partida_aporta_su_categoria_al_recuento_del_jugador():
    from album import album

    filas = partidas("U1", [LORO, FLOR, FLOR, GEOMETRICO, ABSTRACTO], nombre="Ana")

    carga = album(filas, "0")
    ana = fila_de(carga, "U1")

    assert ana["recuento"] == {"loro": 1, "flores": 2, "geometrico": 1, "abstracto": 1}
    assert ana["nombre"] == "Ana"
    assert carga["reparto"] == {"loro": 1, "flores": 2, "geometrico": 1, "abstracto": 1}


# @scenarios figura-de-cada-partida
def test_la_categoria_no_se_escribe_en_ninguna_fila():
    """Se deriva del patrón: las filas de entrada salen intactas y siguen sin columna de categoría."""
    from album import album

    filas = partidas("U1", [LORO, FLOR, FLOR, GEOMETRICO, ABSTRACTO])
    antes = [dict(fila) for fila in filas]

    album(filas, "0")

    assert filas == antes


# @scenarios sin-patron-no-cuenta
def test_una_partida_sin_patron_no_es_una_figura_ni_un_abstracto():
    from album import album

    filas = partidas("U1", [FLOR, FLOR, FLOR, FLOR, FLOR, None, None, None])

    carga = album(filas, "0")
    fila = fila_de(carga, "U1")

    assert fila["partidas"] == 5, "las tres sin patrón no entran en el denominador"
    assert fila["recuento"]["abstracto"] == 0, "sin dibujo no hay veredicto de abstracto"
    assert fila["tasa"] == 1.0


# @scenarios sin-patron-no-cuenta
def test_la_instantanea_declara_cuantas_partidas_se_quedaron_sin_clasificar():
    """Es la cobertura del álbum: sin ella, un ranking sobre el 24% de las partidas parece uno completo."""
    from album import album

    filas = partidas("U1", [FLOR, None, None, None])

    carga = album(filas, "0")

    assert carga["clasificadas"] == 1
    assert carga["sin_patron"] == 3


# @scenarios tasa-de-figuras-por-partida
def test_la_puntuacion_es_la_media_de_puntos_por_partida():
    """Cambio de regla del 2026-08-09: las figuras dejan de valer lo mismo.

    Antes la puntuación era la proporción de partidas con figura. Ahora es la media de PUNTOS por partida,
    con geométrico 3, loro 2 y flor 1. La propiedad que se conserva —y que es la que importa— es que sigue
    siendo **por partida**: jugar más no sube la puntuación por sí solo.
    """
    from album import album

    filas = partidas("U1", [FLOR, FLOR, FLOR, ABSTRACTO, ABSTRACTO])

    fila = fila_de(album(filas, "0"), "U1")

    assert fila["figuras"] == 3
    assert fila["partidas"] == 5
    assert fila["puntos"] == 3, "tres flores a 1 punto"
    assert fila["media"] == 0.6
    assert fila["tasa"] == 0.6, "la proporción se sigue publicando, ya no es el criterio"


# @scenarios tasa-de-figuras-por-partida
def test_un_geometrico_vale_mas_que_un_loro_y_un_loro_mas_que_una_flor():
    from album import album

    geo = partidas("U1", [GEOMETRICO] * 5, nombre="geo")
    loro = partidas("U2", [LORO] * 5, nombre="loro")
    flor = partidas("U3", [FLOR] * 5, nombre="flor")

    orden = [f["nombre"] for f in album(geo + loro + flor, "0")["jugadores"]]

    assert orden == ["geo", "loro", "flor"], f"la escala no se respeta: {orden}"


# @scenarios tasa-de-figuras-por-partida
def test_jugar_mas_no_sube_la_tasa_por_si_solo():
    """El criterio descartado —recuento absoluto— coronaba a quien más juega. Este no puede."""
    from album import album

    constante = partidas("U1", [FLOR, ABSTRACTO], nombre="constante")
    prolifico = partidas("U2", [FLOR, ABSTRACTO] * 10, nombre="prolifico")

    carga = album(constante + prolifico, "0")

    assert fila_de(carga, "U1")["media"] == fila_de(carga, "U2")["media"]
    assert fila_de(carga, "U2")["partidas"] == 20


# @scenarios abstracto-se-registra-y-no-puntua
def test_un_abstracto_aparece_en_el_recuento_y_baja_la_tasa():
    from album import album

    solo_figuras = partidas("U1", [FLOR] * 4, nombre="limpia")
    con_abstracto = partidas("U2", [FLOR] * 4 + [ABSTRACTO], nombre="con ruido")

    carga = album(solo_figuras + con_abstracto, "0")
    ruidosa = fila_de(carga, "U2")

    assert ruidosa["recuento"]["abstracto"] == 1, "el abstracto se registra, no desaparece"
    assert ruidosa["media"] < fila_de(carga, "U1")["media"]


# @scenarios minimo-de-partidas-para-clasificar
def test_por_debajo_del_minimo_no_hay_puesto_aunque_la_tasa_sea_la_mejor():
    """Con mínimo 3, la temporada 0 la ganaba alguien con un 100% de tres partidas.

    Las cantidades van **literales, 4 y 5**, y no derivadas de la constante: un fixture que se ajuste solo
    al umbral deja de medir cuál es el umbral, y el número es justo lo que aquí se decidió.
    """
    from album import album

    perfecta_pero_corta = partidas("U1", [FLOR] * 4, nombre="Sandra")
    regular_pero_larga = partidas("U2", [FLOR] * 4 + [ABSTRACTO], nombre="Juan")

    carga = album(perfecta_pero_corta + regular_pero_larga, "0")
    sandra, juan = fila_de(carga, "U1"), fila_de(carga, "U2")

    assert sandra["media"] > juan["media"]
    assert sandra["clasificado"] is False and sandra["posicion"] is None
    assert juan["clasificado"] is True and juan["posicion"] == 1
    assert carga["jugadores"][0]["jugador"] == "U2", "quien no clasifica no encabeza"


# @scenarios minimo-de-partidas-para-clasificar
def test_quien_no_llega_al_minimo_sigue_apareciendo():
    """Verse en el sitio de uno informa más que no verse. Es lo mismo que hace la tabla de puntuación."""
    from album import album

    carga = album(partidas("U1", [FLOR]), "0")

    assert [fila["jugador"] for fila in carga["jugadores"]] == ["U1"]
    assert carga["jugadores"][0]["clasificado"] is False


# @scenarios orden-determinista-del-album
def test_a_igualdad_de_tasa_va_delante_quien_aporto_mas_figuras():
    from album import album

    pocas = partidas("U1", [FLOR] * 5, nombre="zeta")
    muchas = partidas("U2", [FLOR] * 9, nombre="alfa")

    carga = album(pocas + muchas, "0")

    assert [fila["jugador"] for fila in carga["jugadores"]] == ["U2", "U1"]
    assert carga["jugadores"][0]["figuras"] == 9


# @scenarios orden-determinista-del-album
def test_el_empate_total_se_rompe_por_nombre_y_no_por_el_orden_de_entrada():
    from album import album

    zeta = partidas("U1", [FLOR] * 5, nombre="Zeta")
    alfa = partidas("U2", [FLOR] * 5, nombre="Alfa")

    de_una_forma = [fila["nombre"] for fila in album(zeta + alfa, "0")["jugadores"]]
    de_la_otra = [fila["nombre"] for fila in album(alfa + zeta, "0")["jugadores"]]

    assert de_una_forma == de_la_otra == ["Alfa", "Zeta"]


# @scenarios el-album-hereda-los-dias-de-la-temporada
def test_un_patron_de_un_dia_que_no_cuenta_no_entra_en_el_album():
    """Sábado con cinco jugadores: lo único que lo excluye es el fin de semana, no la falta de muestra."""
    from album import album

    sabado = [
        resultado(f"U{n}", 1898, LORO, fecha="2026-09-05", nombre=f"j{n}") for n in range(1, 6)
    ]
    lunes = [
        resultado(f"U{n}", 1900, FLOR, fecha="2026-09-07", nombre=f"j{n}") for n in range(1, 6)
    ]

    carga = album(sabado + lunes, "2026-09")

    assert carga["reparto"]["loro"] == 0, "el patrón del sábado no entra"
    assert carga["reparto"]["flores"] == 5
    assert fila_de(carga, "U1")["partidas"] == 1


# @scenarios temporada-sin-patrones-no-inventa-ranking
def test_una_temporada_sin_ningun_patron_no_produce_campeon_de_belleza():
    """El estado real de agosto de 2026: 61 de 80 filas sin patrón porque el cron aún no lo guardaba."""
    from album import album

    carga = album(partidas("U1", [None] * 10), "0")

    assert carga["jugadores"] == []
    assert carga["clasificadas"] == 0
    assert carga["sin_patron"] == 10


# @scenarios temporada-sin-patrones-no-inventa-ranking
def test_una_temporada_sin_resultados_devuelve_un_album_vacio_y_no_revienta():
    from album import album

    carga = album([], "2026-09")

    assert carga["jugadores"] == []
    assert carga["clasificadas"] == 0


# @scenarios figura-de-cada-partida
def test_el_album_viaja_en_la_instantanea_con_el_catalogo_de_categorias():
    """La web pinta el emoji que dice Python: un mapa duplicado en JavaScript sería una segunda verdad."""
    from seasons import instantanea

    filas = partidas("U1", [LORO, FLOR, FLOR, GEOMETRICO, ABSTRACTO], nombre="Ana")

    carga = instantanea(filas, "0")

    assert carga["album"]["jugadores"][0]["recuento"]["loro"] == 1
    # El catálogo publica también LO QUE VALE cada figura, para que la web no tenga su propia tabla de
    # puntos (decisión del dueño el 2026-08-09: geométrico > loro > flores).
    assert carga["album"]["categorias"][0] == {
        "clave": "loro",
        "emoji": "🦜",
        "puntua": True,
        "puntos": 2,
    }


# @scenarios figura-de-cada-partida
def test_el_catalogo_viaja_como_lista_porque_jsonb_no_conserva_el_orden_de_las_claves():
    """Postgres devuelve las claves de un JSONB por longitud y luego alfabéticamente.

    Comprobado contra la instantánea real: `logros` vuelve como `verdugo, fondista, suertudo, impecable,
    dia-imposible, superviviente`. Con un diccionario, `abstracto` (9) llegaría antes que `geometrico` (10)
    y la web pintaría el ruido entre las figuras que puntúan.
    """
    from album import categorias

    catalogo = categorias()

    assert isinstance(catalogo, list)
    assert [c["clave"] for c in catalogo] == ["loro", "flores", "geometrico", "abstracto"]
    assert [c["puntua"] for c in catalogo] == [True, True, True, False]
    # El orden por longitud de clave, que es el que aplicaría JSONB, es OTRO:
    assert sorted(["loro", "flores", "geometrico", "abstracto"], key=lambda c: (len(c), c)) != [
        c["clave"] for c in catalogo
    ]


# @scenarios orden-determinista-del-album
def test_el_empate_lo_deshace_la_puntuacion_general():
    """En una temporada de pocas jornadas la puntuación del álbum apenas distingue.

    Con cinco jornadas jugadas por todos, los puntos por partida solo pueden tomar seis valores: siete de
    ocho jugadores acababan empatados, y con **colecciones idénticas**, así que ningún criterio sacado del
    propio álbum podía separarlos. Decisión del dueño el 2026-08-09: los deshace la tabla de puntuación.
    """
    from album import album

    # Misma colección exacta —una flor cada uno— y por tanto la misma puntuación de álbum. Lo único que
    # los separa es lo que hicieron en el marcador: `mejor` resolvió en 2 y `peor` en 5.
    mejor = [
        resultado("U1", 1500 + i, FLOR, nombre="Mejor", score=2) for i in range(5)
    ]
    peor = [resultado("U2", 1500 + i, FLOR, nombre="Peor", score=5) for i in range(5)]

    filas = album(mejor + peor, "0")["jugadores"]

    assert filas[0]["media"] == filas[1]["media"], "el criterio del álbum no los separa"
    assert [f["nombre"] for f in filas] == ["Mejor", "Peor"]
    assert [f["posicion"] for f in filas] == [1, 2], "ya no comparten puesto"


# @scenarios orden-determinista-del-album
def test_si_no_hay_nada_que_los_separe_siguen_compartiendo_puesto():
    """El desempate no fabrica diferencias: dos personas idénticas en todo siguen empatadas."""
    from album import album

    a = [resultado("U1", 1500 + i, FLOR, nombre="Ana", score=4) for i in range(5)]
    b = [resultado("U2", 1500 + i, FLOR, nombre="Bea", score=4) for i in range(5)]

    filas = album(a + b, "0")["jugadores"]

    assert [f["posicion"] for f in filas] == [1, 1]


# @scenarios faltar-no-mejora-la-media-del-album
def test_faltar_no_mejora_la_media_del_album():
    """El defecto que esto corrige, con los números reales que lo destaparon.

    Dos jugadores con los mismos 8 puntos: uno jugó las 8 jornadas y tres le salieron abstractas, el otro jugó
    5 y ninguna. Salían a 1,00 y 1,60 — el segundo ganaba **por haber faltado tres días**, porque sus
    abstractos no llegaban a existir. El marcador protege esto con un escenario propio desde el principio; el
    álbum no lo tenía.
    """
    from album import album

    dias = ["2026-08-03", "2026-08-04", "2026-08-05", "2026-08-06", "2026-08-07"]
    filas = []
    for indice, dia in enumerate(dias):
        # Aparece todos los días: tres flores y dos abstractos.
        filas.append(resultado("U_todos", 1700 + indice, FLOR if indice < 3 else ABSTRACTO, dia))
        # Solo aparece cuando le sale bonito: tres flores y a casa.
        if indice < 3:
            filas.append(resultado("U_selectivo", 1700 + indice, FLOR, dia))
        # Relleno para que **todos** los días alcancen la muestra mínima, también los que el selectivo se
        # salta: con tres rellenos, esos días no contaban como jornada y el denominador salía 3 en vez de 5.
        for otro in range(4):
            filas.append(resultado(f"U_relleno{otro}", 1700 + indice, ABSTRACTO, dia))

    carga = album(filas, "2026-08")
    todos, selectivo = fila_de(carga, "U_todos"), fila_de(carga, "U_selectivo")

    assert todos["puntos"] == selectivo["puntos"] == 3, "los mismos puntos"
    assert todos["partidas"] == 5 and selectivo["partidas"] == 3, "y distinto número de partidas"
    assert todos["denominador"] == selectivo["denominador"] == 5, "el denominador son las jornadas"
    assert todos["media"] == selectivo["media"], (
        f"faltar no puede mejorar la media: {todos['media']} vs {selectivo['media']}"
    )


# @scenarios la-temporada-cero-mide-contra-las-partidas-jugadas
def test_la_temporada_cero_mide_contra_las_partidas_jugadas():
    """Son 181 jornadas de dieciocho meses con gente entrando y saliendo.

    Medir contra todas ordenaría por antigüedad en el grupo, no por quién dibuja mejor, y la temporada 0 se
    rige por las reglas con las que se jugó.
    """
    from album import album

    corta = partidas("U1", [FLOR] * 6)
    larga = [resultado("U2", 1500 + i, FLOR) for i in range(20)]

    carga = album(corta + larga, "0")

    assert fila_de(carga, "U1")["denominador"] == 6, "sus partidas, no las 20 jornadas"
    assert fila_de(carga, "U1")["media"] == fila_de(carga, "U2")["media"] == 1.0
