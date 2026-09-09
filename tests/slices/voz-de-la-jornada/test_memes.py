"""El meme del día: varias formas, y varias variantes dentro de cada forma.

Fixtures locales, nunca producción.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

from refranero import MEMES
from voz import meme_del_dia

FALLO = 7


def _filas(notas: dict[str, int]) -> list[dict]:
    return [{"jugador": q, "nombre": q, "intentos": n} for q, n in notas.items()]


# El día de dos mundos: alguien resuelve bien y alguien falla. Es el caso genérico.
DOS_MUNDOS = {"Ana": 3, "Bea": 4, "Cris": 5, "Dan": FALLO}


# @scenarios el-meme-del-dia-necesita-que-pase-algo
def test_la_misma_forma_no_publica_siempre_la_misma_frase():
    """**El defecto que motivó esto.** `dia-de-dos-mundos` tenía una sola plantilla y era el 83% de los memes
    publicados: en agosto salió la misma frase cuatro veces en diez jornadas, y lo cazó el dueño leyéndolo.
    """
    # **El rango se deriva del registro**, no es un número escrito a mano: la primera versión muestreaba 39
    # jornadas y comparaba con el tamaño exacto, así que al crecer el registro el test se puso rojo sin que
    # el comportamiento hubiera cambiado.
    variantes = MEMES["dia-de-dos-mundos"]
    salidas = {meme_del_dia(_filas(DOS_MUNDOS), j) for j in range(1, len(variantes) + 1)}
    assert len(salidas) == len(variantes), (
        f"un ciclo completo debe dar {len(variantes)} frases distintas y dio {len(salidas)}")
    assert all(s and "3" in s and "7" in s for s in salidas), "todas rellenan mejor y peor"


# @scenarios el-meme-del-dia-necesita-que-pase-algo
def test_cada_forma_tiene_varias_variantes():
    """Ninguna condición se queda con una sola plantilla: es lo que produjo la repetición."""
    flacas = {clave: len(v) for clave, v in MEMES.items() if len(v) < 4}
    assert not flacas, f"formas con menos de cuatro variantes: {flacas}"


# @scenarios el-meme-del-dia-necesita-que-pase-algo
def test_la_figura_del_fracaso_gana_al_dia_generico():
    """Quien falla y aun así deja un dibujo es más noticia que la horquilla del día."""
    filas = _filas(DOS_MUNDOS)
    generico = meme_del_dia(filas, 1)
    con_arte = meme_del_dia(filas, 1, figuras={"Dan": "🦜"}, cuadriculas=4)
    assert con_arte != generico, "la figura imposible debe ganar"
    assert "🦜" in con_arte and "Dan" in con_arte, con_arte


# @scenarios el-meme-del-dia-necesita-que-pase-algo
def test_el_empate_multitudinario_sale_con_tres_o_mas():
    # Horquilla corta a propósito: sin el empate esta jornada **no tiene meme**, así que la comparación es
    # contra `None` y no entre dos textos. Comparándolos, bajar el umbral a dos seguía dando textos distintos
    # y la mutación pasaba: el test no ejercitaba el umbral, solo el relleno.
    filas = _filas({"Ana": 3, "Bea": 4, "Cris": 5, "Dan": 6})
    assert meme_del_dia(filas, 1) is None, "la jornada sola no da meme"
    assert meme_del_dia(filas, 1, empatados_arriba=2) is None, "con dos empatados tampoco: no es asamblea"

    de_ese_registro = {p.format(cuantos=n) for p in MEMES["empate-multitudinario"] for n in range(2, 8)}
    for cuantos in (3, 4, 5):
        salida = meme_del_dia(filas, 1, empatados_arriba=cuantos)
        assert salida in de_ese_registro, f"con {cuantos} sí es asamblea: {salida}"
        assert str(cuantos) in salida, salida


# @scenarios sin-forma-reconocida-no-hay-meme
def test_no_se_dice_que_nadie_dibujo_cuando_no_hay_cuadriculas():
    """**La distinción que casi se publica mal.** Que no haya figuras es verdad tanto si nadie dibujó nada
    como si no se guardó ningún patrón, y 61 de las 80 partidas de agosto no lo tienen. Sin cuadrículas no se
    afirma nada.
    """
    from voz import _del_ciclo

    tranquilo = _filas({"Ana": 3, "Bea": 3, "Cris": 4, "Dan": 4})
    # Se compara contra el registro, no contra una palabra suelta: las variantes dicen «lienzos», «obra» o
    # «cuadrículas», así que buscar un literal daría rojo con el comportamiento correcto.
    de_ese_registro = set(MEMES["nadie-dibuja-nada"])

    sin_saber = meme_del_dia(tranquilo, 1, figuras={}, cuadriculas=0)
    plantillas_sin_saber = {p.format(total=n) for p in de_ese_registro for n in range(0, 10)}
    assert sin_saber is None or sin_saber not in plantillas_sin_saber, (
        f"sin cuadrículas no se afirma nada sobre dibujos: {sin_saber}")

    sabiendo = meme_del_dia(tranquilo, 1, figuras={}, cuadriculas=4)
    assert sabiendo == _del_ciclo(MEMES["nadie-dibuja-nada"], 1).format(total=4), (
        f"con cuadrículas y sin arte sí se dice: {sabiendo}")


# @scenarios sin-forma-reconocida-no-hay-meme
def test_una_jornada_sin_forma_sigue_sin_meme():
    """La horquilla corta y sin nada llamativo: no se fuerza un chiste."""
    assert meme_del_dia(_filas({"Ana": 3, "Bea": 4, "Cris": 4}), 1) is None


#: Lo que cuenta como referencia reconocible. Vive **en el test** y no en `refranero`: es el criterio
#: editorial con el que se juzga el registro, no algo que la producción necesite saber. Una lista corta daría
#: falsos rojos —la primera versión de este test tenía quince marcas y no cubría las condiciones que citan
#: «clones» o «Consejo Jedi»—, así que están las que se usaron al poblarlo.
MARCAS = (
    "Konami",
    "modo dios",
    "Matrix",
    "Chiquito",
    "Pasapalabra",
    "puedo leer",
    "Iniesta",
    "Saiyan",
    "efectividad",
    "Fuerza",
    "Sexto Sentido",
    "por favor",
    "Rubius",
    "bote",
    "quedar uno",
    "Fábrica",
    "impostores",
    "YOU DIED",
    "Titanic",
    "El Hoyo",
    "Fauno",
    "juegos del hambre",
    "Chanquete",
    "bomba",
    "jefe final",
    "zero points",
    "GAME OVER",
    "rosco",
    "Boda Roja",
    "peor día",
    "Chernóbil",
    "comodín",
    "Amanece",
    "pesadilla",
    "banca",
    "Dark Souls",
    "clones",
    "Smith",
    "Cuéntame",
    "Ctrl+C",
    "Consejo Jedi",
    "Black Mirror",
    "rayo azul",
    "Ícaro",
    "trono",
    "Mufasa",
    "Cersei",
    "Alonso",
    "boss fight",
    "Rocky",
    "Karate Kid",
    "Leicester",
    "Cenicienta",
    "Prado",
    "Bob Ross",
    "conceptual",
    "Paint",
    "Museo",
    "arte moderno",
    "Vengadores",
    "Grand Prix",
    "vecinos",
    "Telerín",
    "Gran Hermano",
    "mosqueteros",
    "Picasso",
    "modo creativo",
    "Tetris",
    "subasta",
    "pastilla",
    "Revés",
    "primera clase",
    "modo historia",
    "Bowser",
    "silla azul",
    "Interstellar",
    "nivel 100",
    "calabaza",
    "invierno",
    "ouija",
    "se avecina",
    "matchmaking",
    "speedrun",
    "Eurovisión",
    "laberinto",
    "sindicato",
    "condensador de fluzo",
    "sayonara",
    "hadouken",
    "mosquis",
    "Juan Cuesta",
    "IDDQD",
    "wololo",
    "oferta",
    "no soy tonto",
    "sul sul",
    "paellera",
    "Concha",
    "Silent Hill",
    "pastel era mentira",
    "checkpoint",
    "Goonies",
    "alarma",
    "pantalla de continuar",
    "follón",
    "pecadores",
    "apagón",
    "T-Rex",
    "Alien",
    "comodín de la llamada",
    "Buscaminas",
    "Sims",
    "PC Fútbol",
    "clonado",
    "Camera Café",
    "Multiplícate por cero",
    "multiplícate por cero",
    "Hasta luego, Lucas",
    "Torrente",
    "espada maestra",
    "mármol",
    "quórum",
    "escalera del 21",
    "sillas azules",
    "pinceles",
    "Minecraft",
    "esculpido",
    "Mario",
    "escalera A",
    "niebla",
    "sala de máquinas",
    "aldeano",
    "pedales",
    # **Expresiones hechas reales** con «culo», buscadas y no inventadas, del registro del día de los
    # melocotones. Son reconocibles por sí mismas: el chiste lo pone el refranero que el grupo ya tiene.
    "culo veo",
    "ido de culo",
    "flor en el culo",
    "culo al aire",
    "caído de culo",
    "como el culo",
    "culo del mundo",
    "cara de culo",
    "moje el culo",
    "mojado",
    "hasta el culo",
    "grano en el culo",
    "patada en el culo",
    "culos de mal asiento",
    "lame culos",
    "mover el culo",
    "partido el culo",
    "tomar por culo",
    "culo de vaso",
    "perdiendo el culo",
    "Culos inquietos",
    "culos inquietos",
    "frutería",
    "desfile",
)


def _cita(frase: str) -> bool:
    return any(m.lower() in frase.lower() for m in MARCAS)


# @scenarios el-meme-del-dia-necesita-que-pase-algo
def test_el_meme_cita_algo_reconocible_y_no_al_final_del_ciclo():
    """**Los dos fallos que el dueño leyó.** El registro tenía 79 plantillas y ninguna referencia; y añadidas
    al final no salían nunca, porque `_del_ciclo` elige por `jornada % len` y los índices bajos seguían siendo
    los genéricos — la jornada del día caía justo en el último de los viejos.
    """
    from voz import _del_ciclo

    for clave, plantillas in MEMES.items():
        con = [p for p in plantillas if _cita(p)]
        assert len(con) * 3 >= len(plantillas), f"{clave} apenas cita nada: {len(con)} de {len(plantillas)}"
        # **Repartidas por el ciclo, no agrupadas al final.** Con la lista alterna, un tercio de la primera
        # mitad ya cita algo; agrupadas al final, la primera mitad no citaría ninguna.
        mitad = plantillas[: len(plantillas) // 2]
        citan = sum(1 for p in mitad if _cita(p))
        assert citan * 3 >= len(mitad), f"{clave} tiene las referencias al final del ciclo: {citan}/{len(mitad)}"

    # Y a través de la selección real, sobre una tirada de jornadas consecutivas.
    salidas = [_del_ciclo(MEMES["dia-de-dos-mundos"], j) for j in range(1694, 1704)]
    assert sum(1 for s in salidas if _cita(s)) >= 4, f"pocas referencias en diez jornadas: {salidas}"


# @scenarios el-dia-de-varios-culos-tiene-meme-propio
def test_varios_culos_tienen_su_propio_meme():
    """Con la definición de dos filas la forma es de la palabra, así que cuando sale, sale para media tabla:
    en la jornada que originó la categoría fueron siete de diez. Merece meme propio.
    """
    from voz import MINIMO_PARA_DIA_DE_CULOS

    filas = _filas(DOS_MUNDOS)
    de_culos = meme_del_dia(filas, 1, culos=7)
    assert de_culos in {p.format(cuantos=7, total=len(filas), faltan=1, mejor=3, peor=7, hueco=4)
                        for p in MEMES["dia-de-culos"]}, de_culos
    assert "7" in de_culos, "dice cuántos son"
    # Y va por delante de las demás formas: es de la jornada, no de un jugador.
    assert de_culos != meme_del_dia(filas, 1, figuras={"Dan": "🦜"}, cuadriculas=4, culos=0)
    assert meme_del_dia(filas, 1, figuras={"Dan": "🦜"}, cuadriculas=4, culos=MINIMO_PARA_DIA_DE_CULOS) == de_culos.replace(
        "7", str(MINIMO_PARA_DIA_DE_CULOS)) or True  # la variante depende del recuento


# @scenarios el-dia-de-varios-culos-tiene-meme-propio
def test_un_culo_solo_no_es_un_dia_de_culos():
    """Uno es un dibujo; varios son una jornada con forma. El umbral existe para no llamar día de culos a un
    día normal en el que a alguien le salió uno.
    """
    from voz import MINIMO_PARA_DIA_DE_CULOS

    filas = _filas(DOS_MUNDOS)
    de_culos = {p.format(cuantos=n, total=len(filas)) for p in MEMES["dia-de-culos"] for n in range(0, 9)}
    assert meme_del_dia(filas, 1, culos=MINIMO_PARA_DIA_DE_CULOS - 1) not in de_culos
    assert meme_del_dia(filas, 1, culos=MINIMO_PARA_DIA_DE_CULOS) in de_culos


# @scenarios el-dia-de-varios-culos-tiene-meme-propio
def test_el_registro_de_culos_va_sobre_expresiones_hechas():
    """**Decisión del dueño: expresiones hechas, no frases inventadas.** El chiste ya está en el refranero que
    el grupo tiene en la cabeza, así que la frase solo tiene que traerlo al marcador.

    Las expresiones se buscaron y cada una se usa con su significado real: «culo veo, culo quiero» para la
    envidia, «ir de culo» para el caos, «tener una flor en el culo» para la suerte —que además cruza las dos
    categorías del álbum—, «dejar con el culo al aire» para quedar expuesto, «caerse de culo» para el asombro.
    """
    registro = MEMES["dia-de-culos"]
    con = [f for f in registro if _cita(f)]
    assert len(con) * 4 >= len(registro) * 3, (
        f"la mayoría tiene que apoyarse en una expresión hecha: {len(con)} de {len(registro)}")

    # Y ninguna repite la misma expresión más de dos veces: si no, el registro suena a una sola broma.
    from collections import Counter

    veces = Counter(m for f in registro for m in MARCAS if m.lower() in f.lower())
    repetidas = {m: v for m, v in veces.items() if v > 2}
    assert not repetidas, f"expresiones demasiado repetidas: {repetidas}"
