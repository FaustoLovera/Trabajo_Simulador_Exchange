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

    cantidad_comprada = 0
    total_invertido = 0
    for operacion in historial:
        if operacion["ticker"] == ticker and operacion["tipo"] == "compra":
            cantidad_comprada += operacion["cantidad"]
            total_invertido += operacion["monto_usdt"]

    precio_promedio = (
        total_invertido / cantidad_comprada if cantidad_comprada > 0 else 0
    )
    invertido_actual = cantidad_actual * precio_promedio
    ganancia = valor_usdt - invertido_actual
    porcentaje_ganancia = (
        (ganancia / invertido_actual) * 100 if invertido_actual != 0 else 0
    )

    detalle_cripto = {
        "ticker": ticker,
        "cantidad": cantidad_actual,
        "valor_usdt": valor_usdt,
        "precio_actual": precio_actual,
        "precio_promedio": precio_promedio,
        "invertido": invertido_actual,
        "ganancia_perdida": ganancia,
        "porcentaje_ganancia": porcentaje_ganancia,
    }

    return detalle_cripto


def estado_actual_completo():
    """
    Genera un resumen detallado del estado actual de todas las criptomonedas en la billetera.

    Carga los saldos actuales, los precios de mercado y el historial de operaciones. Filtra
    las criptomonedas para ignorar aquellas con cantidades insignificantes. Luego, calcula
    el detalle financiero de cada criptomoneda (valor en USDT, ganancia, pérdida, etc.) y 
    suma el valor total del portafolio.

    Finalmente, asigna a cada criptomoneda su porcentaje de participación dentro del portafolio
    y devuelve una lista con todos los detalles.
    """
    
    billetera = cargar_datos_billetera()
    precios = obtener_precios()
    historial = cargar_historial()

    billetera_filtrada = {}
    for ticker in billetera:
        cantidad = billetera[ticker]

        if cantidad >= 0.000001:
            billetera_filtrada[ticker] = cantidad

    detalles = []
    total_usdt = 0

    for ticker in billetera_filtrada:
        cantidad_actual = billetera_filtrada[ticker]
        detalle_cripto = calcular_detalle_cripto(
            ticker, cantidad_actual, precios, historial
        )
        total_usdt += detalle_cripto["valor_usdt"]
        detalles.append(detalle_cripto)

    calcular_porcentaje = lambda valor_usdt: (
        (valor_usdt / total_usdt) * 100 if total_usdt > 0 else 0
    )

    for detalle_cripto in detalles:
        detalle_cripto["porcentaje"] = calcular_porcentaje(detalle_cripto["valor_usdt"])

    return detalles
