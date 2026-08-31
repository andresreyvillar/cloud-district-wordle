"""La palabra del día, probada **sin tocar la red**.

El fichero cifrado se construye aquí con la misma cadena que usa el juego —msgpack, XOR, gzip—, así que el
descifrado se ejercita de verdad en lugar de darse por bueno. El texto del Wikcionario es el literal que
devolvió su API, recortado.
"""

import gzip
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "tools"))

import msgpack

from palabra import (
    CLAVE_DEL_FICHERO,
    LARGO_DE_LA_ACEPCION,
    descifra,
    palabra_de,
    palabra_del_dia,
    primera_acepcion,
)

#: Las entradas tal como vienen: `id`, `solution` y un `extras` que en producción está vacío en todas.
ENTRADAS = [
    {"id": 1696, "solution": "podio", "extras": {}},
    {"id": 1697, "solution": "pizza", "extras": {}},
    {"id": 1698, "solution": "vitre", "extras": {}},
    {"id": 1699, "solution": "manana", "extras": {}},
]

#: Extracto real del Wikcionario para «pizza», recortado a lo que importa.
EXTRACTO_PIZZA = """== Español ==


=== Etimología ===
Del italiano pizza.


==== Sustantivo femenino ====
pizza ¦ plural: pizzas

1 Gastronomía
Torta plana de harina leudada, cubierta con salsa, queso y otros aderezos, que se cocina al horno.
Sinónimos: pizza napolitana.
2
El local donde se sirve.
"""


def _fichero(entradas) -> bytes:
    """Un `.binz` como el del juego: msgpack, luego XOR, luego gzip."""
    crudo = msgpack.packb(entradas, use_bin_type=True)
    cifrado = bytes(b ^ CLAVE_DEL_FICHERO[i % len(CLAVE_DEL_FICHERO)] for i, b in enumerate(crudo))
    return gzip.compress(cifrado)


# @scenarios la-palabra-abre-el-mensaje
def test_el_fichero_del_juego_se_descifra():
    """La cadena completa gzip → XOR → msgpack, ejercitada de verdad y no simulada."""
    assert descifra(_fichero(ENTRADAS)) == ENTRADAS


# @scenarios la-palabra-abre-el-mensaje
def test_la_palabra_se_busca_por_identificador_y_no_por_posicion():
    """Las entradas traen su `id`; reproducir la aritmética de índices del juego sería un acoplamiento más."""
    assert palabra_de(ENTRADAS, 1697, 1698) == "pizza"
    assert palabra_de(ENTRADAS, 1696, 1698) == "podio"
    assert palabra_de(ENTRADAS, 1234, 1698) is None, "una jornada que no está da None"


# @scenarios nunca-una-palabra-sin-jugar
def test_nunca_devuelve_una_palabra_sin_jugar():
    """**El guardarraíl.** El fichero real trae 2.000 entradas, así que sin esto bastaría cambiar un número
    para leer meses por delante. Que exista es lo que hace que este repositorio no sea una chuleta.
    """
    assert palabra_de(ENTRADAS, 1699, 1698) is None, "la de mañana no se entrega aunque esté"
    assert palabra_de(ENTRADAS, 1698, 1698) == "vitre", "la de hoy sí, que ya está jugada"


# @scenarios nunca-una-palabra-sin-jugar
def test_el_guardarrail_tambien_se_aplica_en_el_flujo_completo():
    """Probar la función suelta no basta: lo que importa es que el flujo la respete."""
    assert palabra_del_dia(1699, 1698, descargar=lambda: _fichero(ENTRADAS)) is None
    assert palabra_del_dia(1697, 1698, descargar=lambda: _fichero(ENTRADAS), extraer=lambda _: "")[0] == "pizza"


# @scenarios la-palabra-abre-el-mensaje
def test_la_acepcion_sale_del_extracto():
    assert primera_acepcion(EXTRACTO_PIZZA).startswith("Torta plana de harina leudada")


# @scenarios sin-acepcion-se-publica-la-palabra-sola
def test_sin_extracto_no_hay_acepcion_pero_si_palabra():
    palabra, acepcion = palabra_del_dia(
        1698, 1698, descargar=lambda: _fichero(ENTRADAS), extraer=lambda _: ""
    )
    assert palabra == "vitre" and acepcion == "", "vitre no tiene entrada, y aun así se publica la palabra"


# @scenarios sin-palabra-el-mensaje-sale-igual
def test_sin_descarga_no_hay_palabra_y_no_revienta():
    assert palabra_del_dia(1697, 1698, descargar=lambda: None) is None


# @scenarios sin-palabra-el-mensaje-sale-igual
def test_un_fichero_con_otro_formato_no_tumba_la_publicacion():
    assert palabra_del_dia(1697, 1698, descargar=lambda: b"esto no es gzip") is None


# @scenarios la-acepcion-se-recorta-para-caber
def test_la_acepcion_larga_se_recorta_por_la_primera_frase():
    largo = "Primera frase corta. " + "y luego una coletilla larguísima " * 10
    recortada = primera_acepcion(f"1 Campo\n{largo}\n")
    assert recortada == "Primera frase corta.", recortada


# @scenarios la-acepcion-se-recorta-para-caber
def test_la_acepcion_sin_puntos_se_recorta_por_palabra_entera():
    largo = "palabra " * 60
    recortada = primera_acepcion(f"1 Campo\n{largo}\n")
    assert len(recortada) <= LARGO_DE_LA_ACEPCION + 1, recortada
    assert recortada.endswith("…")
    assert "palabr…" not in recortada, "no se corta a mitad de palabra"


# @scenarios la-palabra-abre-el-mensaje, sin-acepcion-se-publica-la-palabra-sola
def test_la_linea_del_mensaje():
    from resumen import bloque_palabra

    assert bloque_palabra(("pizza", "Torta plana.")) == "📖 *La palabra de hoy:* PIZZA — Torta plana."
    assert bloque_palabra(("vitre", "")) == "📖 *La palabra de hoy:* VITRE"
    assert bloque_palabra(None) == ""


# @scenarios la-palabra-abre-el-mensaje
def test_la_palabra_abre_el_resumen():
    """Va **primero**, por delante de las viñetas: es el dato que el grupo no tiene por su cuenta."""
    from resumen import resumen_del_dia

    filas = [
        {"wordle_id": 1, "player_name": f"J{i}", "slack_user_id": f"J{i}", "score": 4,
         "date": "2099-01-05", "pattern": None}
        for i in range(6)
    ]
    texto = resumen_del_dia(filas, "0", 1, palabra=("pizza", "Torta plana."))
    assert texto.splitlines()[0] == "📖 *La palabra de hoy:* PIZZA — Torta plana.", texto[:120]


# @scenarios nada-de-la-palabra-se-guarda
def test_nada_de_la_palabra_se_escribe():
    """El módulo lee y devuelve: no importa la base de datos ni abre ficheros para escribir.

    Se comprueba sobre el **árbol sintáctico** y no buscando texto: la primera versión buscaba la subcadena
    `open(` y casaba con `urlopen(`, así que daba rojo con el módulo correcto.
    """
    import ast

    fuente = (Path(__file__).resolve().parents[3] / "tools" / "palabra.py").read_text(encoding="utf-8")
    arbol = ast.parse(fuente)

    importados = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            importados.update(alias.name.split(".")[0] for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            importados.add(nodo.module.split(".")[0])
    assert "supabase" not in importados, "la palabra no toca la base de datos"

    llamadas = {
        nodo.func.id for nodo in ast.walk(arbol)
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
    }
    atributos = {
        nodo.func.attr for nodo in ast.walk(arbol)
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute)
    }
    assert "open" not in llamadas, "no abre ficheros"
    for prohibido in ("insert", "upsert", "write_text", "write_bytes", "table"):
        assert prohibido not in atributos, f"no debe persistir: llama a {prohibido}()"


# @scenarios la-definicion-se-busca-tambien-con-mayuscula
def test_la_definicion_se_busca_tambien_con_mayuscula_inicial():
    """`troya` no tiene entrada en el Wikcionario y `Troya` sí: el juego usa minúsculas y el diccionario
    respeta el nombre propio. Medido, sin este respaldo se perdía una definición de cada veinticinco.
    """
    import json

    import palabra as modulo

    pedidas = []

    def falso_pide(url):
        pedidas.append(url)
        # El Wikcionario responde 200 con extracto vacío para la minúscula.
        vacia = {"query": {"pages": {"-1": {"title": "troya", "missing": ""}}}}
        llena = {"query": {"pages": {"1": {"extract": "1 Historia\nCiudad legendaria."}}}}
        return json.dumps(llena if "Troya" in url else vacia).encode()

    original = modulo._pide
    modulo._pide = falso_pide
    try:
        extracto = modulo.busca_extracto("troya")
    finally:
        modulo._pide = original

    assert "Ciudad legendaria" in extracto, extracto
    assert len(pedidas) == 2, "prueba primero la minúscula y luego la capitalizada"
    assert "troya" in pedidas[0] and "Troya" in pedidas[1]
