import json

HISTORIAL_PATH = "./datos/historial_operaciones.json"
BILLETERA_PATH = "./datos/billetera.json"
COTIZACIONES_PATH = "./datos/datos_cotizaciones.json"


def obtener_precios():
    """
    Lee el archivo de cotizaciones y devuelve un diccionario con los nombres de las
    criptomonedas como claves y sus precios actuales en USD como valores.
    """
    with open(COTIZACIONES_PATH, "r") as f:
        datos = json.load(f)
    return {cripto["ticker"]: cripto["precio_usd"] for cripto in datos}


def cargar_historial():
    """
    Carga el historial de operaciones desde un archivo JSON.

    Intenta abrir y leer el archivo especificado por `HISTORIAL_PATH`. Si el archivo
    se encuentra, retorna su contenido como una lista de operaciones. Si el archivo
    no existe, retorna una lista vacía.
    """

    try:
        with open(HISTORIAL_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def cargar_datos_billetera():
    """
    Carga la billetera desde un archivo JSON.

    Intenta abrir y leer el archivo especificado por `BILLETERA_PATH`. Si el archivo
    se encuentra, retorna su contenido como un diccionario. Si el archivo no existe,
    retorna un diccionario vacío.
    """
    try:
        with open(BILLETERA_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def calcular_detalle_cripto(ticker, cantidad_actual, precios, historial):
    """
    Calcula el estado financiero de una criptomoneda en base a su cantidad actual, el precio de mercado
    y el historial de compras.

    Obtiene el precio actual, calcula el valor de la tenencia en USDT, el precio promedio de compra,
    el monto invertido en la cantidad disponible, y la ganancia o pérdida actual tanto en USDT como en porcentaje.

    Devuelve un diccionario con toda esta información resumida.
    """

    precio_actual = precios.get(ticker, 0)
    valor_usdt = cantidad_actual * precio_actual

    # Filtra las operaciones de compra para el ticker especificado
    compras = [
        op for op in historial if op["ticker"] == ticker and op["tipo"] == "compra"
    ]

    cantidad_comprada = sum(op["cantidad"] for op in compras)
    total_invertido = sum(op["monto_usdt"] for op in compras)

    # Evita divisiones por 0 y devuelve 0 en caso de que el denominador sea 0
    division_por_0_segura = lambda num, den: num / den if den != 0 else 0

    precio_promedio = division_por_0_segura(total_invertido, cantidad_comprada)
    invertido_actual = cantidad_actual * precio_promedio

    ganancia = valor_usdt - invertido_actual
    porcentaje_ganancia = division_por_0_segura(ganancia, invertido_actual) * 100

    return {
        "ticker": ticker,
        "cantidad": cantidad_actual,
        "valor_usdt": valor_usdt,
        "precio_actual": precio_actual,
        "precio_promedio": precio_promedio,
        "invertido": invertido_actual,
        "ganancia_perdida": ganancia,
        "porcentaje_ganancia": porcentaje_ganancia,
    }


def estado_actual_completo():
    """
    Calcula un resumen financiero completo del portafolio de criptomonedas actual.

    Este resumen incluye, para cada activo con saldo significativo (> 0.000001):
    - Cantidad disponible
    - Valor de mercado en USDT
    - Precio promedio de compra
    - Monto invertido
    - Ganancia/pérdida neta y en porcentaje
    - Porcentaje de participación en el portafolio total

    Returns:
        List[Dict]: Lista de diccionarios, cada uno representando una criptomoneda con su detalle financiero.
    """

    # Cargar los datos actuales desde archivos locales
    billetera = cargar_datos_billetera()
    precios = obtener_precios()
    historial = cargar_historial()

    # Filtrar solo las criptomonedas con una cantidad significativa
    billetera_filtrada = {
        ticker: cantidad
        for ticker, cantidad in billetera.items()
        if cantidad >= 0.000001
    }

    # Calcular el detalle financiero de cada criptomoneda
    detalles = list(
        map(
            lambda par: calcular_detalle_cripto(par[0], par[1], precios, historial),
            billetera_filtrada.items(),
        )
    )

    # Calcular el valor total en USDT del portafolio
    total_usdt = sum(d["valor_usdt"] for d in detalles)

    # Función para calcular el porcentaje que representa cada cripto sobre el total
    calcular_porcentaje = lambda valor_usdt: (
        (valor_usdt / total_usdt) * 100 if total_usdt > 0 else 0
    )

    # Asignar el porcentaje correspondiente a cada criptomoneda
    for detalle_cripto in detalles:
        detalle_cripto["porcentaje"] = calcular_porcentaje(detalle_cripto["valor_usdt"])

    return detalles
