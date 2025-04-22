import logging
import requests
from guardar_datos_cotizaciones import guardar_datos_cotizaciones, guardar_datos_velas
from typing import Dict, List

URL = "https://api.coingecko.com/api/v3/coins/markets"


def obtener_datos_criptos_coingecko() -> List[Dict]:
    """
    Obtiene los datos de criptomonedas desde la API de CoinGecko.
    
    Returns:
        List[Dict]: Lista de diccionarios con los datos de cada criptomoneda
    """
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d",
    }

    try:
        r = requests.get(URL, params=params)
        r.raise_for_status()  # Lanzará una excepción para códigos de error HTTP
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Error al obtener datos de CoinGecko: {str(e)}")
        return {"error": "No se pudo obtener los datos"}

    logging.info(f"✅ Estado de la respuesta: {r.status_code}")

    datos = r.json()
    # print(f"💡 Datos obtenidos: {datos}")
    resultado = []
    indice = 1

    for cripto in datos:
        fila = {}
        fila["id"] = indice
        fila["nombre"] = cripto.get("name")
        fila["ticker"] = cripto.get("symbol").upper()
        fila["logo"] = cripto.get("image")
        fila["precio_usd"] = cripto.get("current_price")
        fila["1h_%"] = cripto.get("price_change_percentage_1h_in_currency")
        fila["24h_%"] = cripto.get("price_change_percentage_24h_in_currency")
        fila["7d_%"] = cripto.get("price_change_percentage_7d_in_currency")
        fila["market_cap"] = cripto.get("market_cap")
        fila["volumen_24h"] = cripto.get("total_volume")
        fila["circulating_supply"] = cripto.get("circulating_supply")

        resultado.append(fila)

        indice = indice + 1

    print(f"💡 Total de criptos procesadas: {len(resultado)}")
    guardar_datos_cotizaciones(resultado)
    return resultado


def obtener_velas_binance() -> List[Dict]:
    """
    Obtiene los datos de velas (Klines) desde la API de Binance.
    
    Returns:
        List[Dict]: Lista de diccionarios con los datos de cada vela
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": "BTCUSDT", "interval": "1d", "limit": 350}

    try:
        r = requests.get(url, params=params)
        r.raise_for_status()  # Lanzará una excepción para códigos de error HTTP
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Error al obtener datos de Binance: {str(e)}")
        return {"error": "No se pudo obtener los datos"}

    logging.info(f"✅ Estado de la respuesta Binance: {r.status_code}")

    datos = r.json()
    resultado = []

    for vela in datos:
        resultado.append(
            {
                "time": int(vela[0] / 1000),  # timestamp en segundos
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
