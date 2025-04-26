import requests
from guardar_datos_cotizaciones import guardar_datos_cotizaciones, guardar_datos_velas

URL = "https://api.coingecko.com/api/v3/coins/markets"


def obtener_datos_criptos_coingecko():
    """
    Obtiene información del mercado de criptomonedas desde la API pública de CoinGecko.

    Esta función consulta la API de CoinGecko para recuperar los 100 activos principales
    ordenados por capitalización de mercado, incluyendo su precio actual, variaciones
    porcentuales, volumen de trading y suministro circulante. Los datos obtenidos se procesan
    y almacenan localmente mediante la función `guardar_datos_cotizaciones`.

    Returns:
        List[Dict]: Una lista de diccionarios, donde cada uno representa una criptomoneda con:
            - id (int): Índice incremental
            - nombre (str): Nombre de la criptomoneda
            - ticker (str): Ticker en mayúsculas
            - logo (str): URL del logo del activo
            - precio_usd (float): Precio actual en USD
            - 1h_% (float): Variación porcentual en 1 hora
            - 24h_% (float): Variación porcentual en 24 horas
            - 7d_% (float): Variación porcentual en 7 días
            - market_cap (float): Capitalización de mercado
            - volumen_24h (float): Volumen de trading en 24h
            - circulating_supply (float): Suministro circulante

    Notas:
        Si ocurre un error de conexión o una respuesta inválida, la función retorna
        un diccionario con una clave "error" describiendo el problema.
    """
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d",
    }

    try:
        respuesta = requests.get(URL, params)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datos de CoinGecko: {str(e)}")
        return {"error": "Error al obtener datos de CoinGecko"}
    if respuesta.status_code != 200:
        print(
            f"❌ Error en la respuesta de CoinGecko: Status code {respuesta.status_code}"
        )
        return {"error": "Respuesta inválida de la API"}

    print(f"✅ Estado de la respuesta: {respuesta.status_code}")

    datos = respuesta.json()
    resultado = []

    indice = 1
    for cripto in datos:
        fila = {
            "id": indice,
            "nombre": cripto.get("name"),
            "ticker": cripto.get("symbol").upper(),
            "logo": cripto.get("image"),
            "precio_usd": cripto.get("current_price"),
            "1h_%": cripto.get("price_change_percentage_1h_in_currency"),
            "24h_%": cripto.get("price_change_percentage_24h_in_currency"),
            "7d_%": cripto.get("price_change_percentage_7d_in_currency"),
            "market_cap": cripto.get("market_cap"),
            "volumen_24h": cripto.get("total_volume"),
            "circulating_supply": cripto.get("circulating_supply"),
        }
        resultado.append(fila)
        indice += 1

    print(f"💡 Total de criptos procesadas: {len(resultado)}")
    guardar_datos_cotizaciones(resultado)
    return resultado


def obtener_velas_binance():
    """
    Obtiene datos históricos de velas (Klines) diarias del par BTC/USDT desde la API pública de Binance.

    Esta función consulta la API de Binance para recuperar las últimas 350 velas diarias,
    equivalente aproximadamente a un año de datos históricos. Cada vela contiene precios
    de apertura, máximo, mínimo, cierre y volumen negociado. Los datos se procesan y almacenan
    localmente mediante la función `guardar_datos_velas`.

    Returns:
        List[Dict]: Una lista de diccionarios, donde cada uno representa una vela diaria con:
            - time (int): Timestamp de apertura en segundos
            - open (float): Precio de apertura
            - high (float): Precio máximo
            - low (float): Precio mínimo
            - close (float): Precio de cierre
            - volume (float): Volumen negociado

    Notas:
        Si ocurre un error de conexión o una respuesta inválida, la función retorna
        un diccionario con una clave "error" describiendo el problema.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": "BTCUSDT",
        "interval": "1d",
        "limit": 300,
    }  # Esto se tiene que parametrizar

    try:
        respuesta = requests.get(url, params)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al obtener datos de Binance: {str(e)}")
        return {"error": "Error al obtener datos de Binance"}

    if respuesta.status_code != 200:
        print(
            f"❌ Error en la respuesta de Binance: Status code {respuesta.status_code}"
        )
        return {"error": "Respuesta inválida de la API Binance"}

    print(f"✅ Estado de la respuesta Binance: {respuesta.status_code}")

    datos = respuesta.json()
    resultado = []

    for vela in datos:
        resultado.append(
            {
                "time": int(vela[0] / 1000),  # Timestamp en segundos
                "open": float(vela[1]),
                "high": float(vela[2]),
                "low": float(vela[3]),
                "close": float(vela[4]),
                "volume": float(vela[5]),
            }
        )

    print(f"💡 Total de velas procesadas: {len(resultado)}")
    guardar_datos_velas(resultado)
    return resultado
